--
-- Database: `EnergyMonitor`
--
CREATE DATABASE IF NOT EXISTS `EnergyMonitor` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `EnergyMonitor`;

--
-- Table: `VolumeData`
--

CREATE TABLE `VolumeData` (
  `TimeStamp` datetime NOT NULL,
  `Point` varchar(10) NOT NULL,
  `NumReads` int(11) NOT NULL,
  `SupplyWh` double NOT NULL,
  `SupplyMaxW` double NOT NULL,
  `SupplyMinW` double NOT NULL,
  `SupplyAvgW` double NOT NULL,
  `UsageWh` double NOT NULL,
  `UsageMaxW` double NOT NULL,
  `UsageMinW` double NOT NULL,
  `UsageAvgW` double NOT NULL,
  `TotalAvgW` int(11) GENERATED ALWAYS AS (round(`SupplyAvgW` - `UsageAvgW`,0)) VIRTUAL,
  `TotalMaxW` int(11) GENERATED ALWAYS AS (case when `SupplyMaxW` > 0 then `SupplyMaxW` else -`UsageMinW` end) VIRTUAL,
  `TotalMinW` int(11) GENERATED ALWAYS AS (case when `UsageMaxW` > 0 then -`UsageMaxW` else `SupplyMinW` end) VIRTUAL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes
--

--
-- Indexes for table `VolumeData`
--
ALTER TABLE `VolumeData`
  ADD PRIMARY KEY (`TimeStamp`,`Point`),
  ADD KEY `PointTimestampIdx` (`Point`,`TimeStamp`);
