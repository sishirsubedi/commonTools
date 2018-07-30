CREATE TABLE sampleAnalysisQueue(
      queueID INT NOT NULL AUTO_INCREMENT,
      ID INT NOT NULL,
      runID INT NOT NULL,
      sampleID  VARCHAR(50) NOT NULL,
      coverageID VARCHAR(15),
      vcallerID VARCHAR(15),
      assayID  VARCHAR(15) NOT NULL,
      instrumentID VARCHAR(15) NOT NULL,
      environmentID VARCHAR(15) NOT NULL,
      status BOOLEAN NOT NULL DEFAULT 0,
      timeSubmitted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY ( queueID )
      );


CREATE TABLE pipelineStatus(
            pipelineStatusID INT NOT NULL AUTO_INCREMENT,
            queueID INT NOT NULL,
            plStatus VARCHAR(15) NOT NULL,
            timeUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (pipelineStatusID),
            FOREIGN KEY (queueID) REFERENCES sampleAnalysisQueue(queueID)
                              );

DELIMITER $$
CREATE TRIGGER addtoPipelineStatus_fromQueue AFTER INSERT ON sampleAnalysisQueue
FOR EACH ROW
BEGIN
DECLARE s VARCHAR(15);
SET s='queued';
INSERT INTO pipelineStatus (queueID,plStatus, timeUpdated) VALUES (new.queueID,s,now());
END $$
DELIMITER ;



alter table ampliconCount modify sampleID INT;



CREATE TABLE analysisStatus(
            queueID INT NOT NULL,
            analysisStatus INT NOT NULL DEFAULT 0,
            timeUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (queueID, analysisStatus),
            FOREIGN KEY (queueID) REFERENCES sampleAnalysisQueue(queueID)
                              );

DELIMITER $$
DROP TRIGGER IF EXISTS addAnalysisStatus_inPipelineStatus;
CREATE TRIGGER addAnalysisStatus_inPipelineStatus
AFTER INSERT ON pipelineStatus
FOR EACH ROW
BEGIN
DECLARE s VARCHAR(15);
IF new.plStatus='finished'
THEN
  SET s='analysisq';
  INSERT INTO pipelineStatus (queueID,plStatus, timeUpdated) VALUES (new.queueID,s,now());
END IF;
END $$
DELIMITER ;

select t4.queueID, t4.runID, t4.sampleID, t4.assayID, t4.instrumentID, t4.environmentID, t3.plStatus, t3.timeUpdated
from sampleAnalysisQueue as t4
left join (
  select  t2.queueID, t2.plStatus,t2.timeUpdated
  from pipelineStatus as t2
  inner join (
    select queueID, max(timeUpdated) as latestTime
    from pipelineStatus
    group by queueID
  ) as t1
on  t2.queueID = t1.queueID and t2.timeUpdated = t1.latestTime ) as t3
ON t3.queueID = t4.queueID
order by t4.queueID ;



DROP TABLE IF EXISTS `Samples`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Samples` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `assay` varchar(45) DEFAULT NULL,
  `instrument` varchar(45) DEFAULT NULL,
  `lastName` varchar(45) DEFAULT NULL,
  `firstName` varchar(45) DEFAULT NULL,
  `orderNumber` varchar(45) DEFAULT NULL,
  `pathNumber` varchar(45) DEFAULT NULL,
  `tumorSource` varchar(200) DEFAULT NULL,
  `tumorPercent` varchar(45) DEFAULT NULL,
  `runID` varchar(45) DEFAULT NULL,
  `sampleID` varchar(45) DEFAULT NULL,
  `coverageID` varchar(45) DEFAULT NULL,
  `callerID` varchar(45) DEFAULT NULL,
  `runDate` date DEFAULT NULL,
  `note` varchar(200) DEFAULT NULL,
  `environment` varchar(15) DEFAULT NULL,
  `enteredBy` varchar(45) DEFAULT 'niyunyun',
  PRIMARY KEY (`ID`),
  KEY `id` (`ID`,`assay`,`instrument`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;



CREATE TABLE networkIDTOemail(
            ID INT NOT NULL AUTO_INCREMENT,
            name varchar(45) DEFAULT NULL,
            networkID varchar(45) DEFAULT NULL,
            email varchar(100) DEFAULT NULL,
             PRIMARY KEY (ID)
                              );
 insert into networkIDTOemail (name, networkID, email) values('Sishir Subedi', 'tmhsxs240', 'ssubedi@houstonmethodist.org');

insert into networkIDTOemail (name, networkID, email) values('Paul Christensen', 'tmhpac', 'PAChristensen@houstonmethodist.org');



  CREATE TABLE GeneAnnotation(
        geneAnnotationID INT NOT NULL AUTO_INCREMENT,
        gene  VARCHAR(45) NOT NULL,
        curation VARCHAR(5000) NOT NULL,
        enteredBy VARCHAR(45) NOT NULL,
		enterDate Date NOT NULL,
        PRIMARY KEY ( geneAnnotationID )
      );

  DROP TABLE IF EXISTS annotation;
  CREATE TABLE annotation(
    annotationID INT NOT NULL AUTO_INCREMENT,
    chr  VARCHAR(45) NOT NULL,
    pos INT NOT NULL,
    ref VARCHAR(45) NOT NULL,
		alt VARCHAR(45) NOT NULL,
		classification VARCHAR(45) NOT NULL,
		curation VARCHAR(5000) NOT NULL,
		somatic  VARCHAR(45) NOT NULL,
		enteredBy VARCHAR(45) NOT NULL,
		enterDate Date NOT NULL,
        PRIMARY KEY ( annotationID )
      );
