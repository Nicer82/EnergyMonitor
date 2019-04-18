CREATE TABLE `CapacityData` (
  `TimeStamp` datetime NOT NULL,
  `Type` enum('Production','Consumption') NOT NULL,
  `InstallationWh` double NOT NULL,
  `GridWh` double NOT NULL,
  PRIMARY KEY (`TimeStamp`,`Type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ChannelSetup` (
  `Device` varchar(30) NOT NULL,
  `Channel` int(11) NOT NULL,
  `Type` enum('Production','Consumption') NOT NULL,
  PRIMARY KEY (`Device`,`Channel`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ReadingData` (
  `TimeStamp` datetime NOT NULL,
  `Device` varchar(30) NOT NULL,
  `Channel` tinyint(4) NOT NULL,
  `Power` double NOT NULL,
  `Uploaded` datetime NOT NULL,
  PRIMARY KEY (`TimeStamp`,`Device`,`Channel`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
