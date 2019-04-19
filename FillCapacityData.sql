SET time_zone='+00:00';
SET @CapInterval := 60;

SELECT @TotalChannels := COUNT(*) FROM ChannelSetup;

SELECT @LastCapTimeStamp := CAST(COALESCE(MAX(TimeStamp),'1970-01-01') AS DATETIME) FROM CapacityData;

SELECT @LastReadTimeStamp := rd.TimeStamp
FROM ReadingData rd
	INNER JOIN ChannelSetup cs
    ON cs.Device = rd.Device
    AND cs.Channel = rd.Channel
WHERE rd.TimeStamp > @LastCapTimeStamp 
GROUP BY rd.TimeStamp
HAVING COUNT(*) = @TotalChannels
ORDER BY rd.TimeStamp DESC
LIMIT 1;

SELECT @PenultimateReadTimeStamp := rd.TimeStamp
FROM ReadingData rd
WHERE rd.TimeStamp < @LastReadTimeStamp 
ORDER BY rd.TimeStamp DESC
LIMIT 1;

SELECT @ReadInterval := TIMESTAMPDIFF(SECOND,@PenultimateReadTimeStamp,@LastReadTimeStamp);

INSERT INTO CapacityData (TimeStamp,Type,InstallationWh,GridWh)
WITH InstallationData AS
(
	SELECT
		rd.TimeStamp AS TimeStamp,
		cs.Type AS Type,
		SUM(rd.Power) * @ReadInterval / 3600 AS InstallationWh
	FROM ReadingData AS rd
		INNER JOIN ChannelSetup AS cs
		ON cs.Device = rd.Device
		AND cs.Channel = rd.Channel
	WHERE rd.TimeStamp >= FROM_UNIXTIME((UNIX_TIMESTAMP(@LastCapTimeStamp) DIV @CapInterval + 1) * @CapInterval)
	AND rd.TimeStamp < FROM_UNIXTIME(UNIX_TIMESTAMP(@LastReadTimeStamp) DIV @CapInterval * @CapInterval)
	GROUP BY 
		rd.TimeStamp, 
		cs.Type
),
GridData AS
(
	SELECT 
		TimeStamp,
		SUM(
			CASE Type
				WHEN 'Production' THEN -InstallationWh
                WHEN 'Consumption' THEN InstallationWh
			END
		) AS GridWh
	FROM InstallationData
    GROUP BY TimeStamp
)
SELECT
	FROM_UNIXTIME(UNIX_TIMESTAMP(i.TimeStamp) DIV @CapInterval * @CapInterval),
    i.Type,
    SUM(i.InstallationWh),
    SUM(
		CASE
			WHEN i.Type = 'Production' AND g.GridWh > 0 THEN 0.0
			WHEN i.Type = 'Production' AND g.GridWh < 0 THEN g.GridWh
			WHEN i.Type = 'Consumption' AND g.GridWh > 0 THEN g.GridWh
			WHEN i.Type = 'Consumption' AND g.GridWh  < 0 THEN 0.0
			ELSE 0.0
		END
	)
FROM InstallationData AS i
	INNER JOIN GridData AS g
    ON g.TimeStamp = i.TimeStamp
GROUP BY
	FROM_UNIXTIME(UNIX_TIMESTAMP(i.TimeStamp) DIV @CapInterval * @CapInterval),
    i.Type;
