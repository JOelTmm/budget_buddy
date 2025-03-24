-- MySQL dump 10.13  Distrib 9.2.0, for Win64 (x86_64)
--
-- Host: localhost    Database: finance
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `balance` decimal(15,2) DEFAULT '0.00',
  `account_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `account_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
INSERT INTO `account` VALUES (1,1,20.00,'Checking'),(2,1,30.00,'Checking'),(3,2,300.00,'joel'),(4,5,0.06,'joel'),(5,5,10.94,'lucas');
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banker`
--

DROP TABLE IF EXISTS `banker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banker` (
  `id` int NOT NULL AUTO_INCREMENT,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banker`
--

LOCK TABLES `banker` WRITE;
/*!40000 ALTER TABLE `banker` DISABLE KEYS */;
INSERT INTO `banker` VALUES (1,'jjj','vvv','morgan@gmail.com','$2b$12$Xft01r6bWQWmb6JybTtZzuSYBpBYn9JGxBqnIGPChrG75fw0PIkW2'),(2,'mor','gan','moorgan@gmail.com','$2b$12$O8f6CvIrSfKaQ9TZE./rB.hzkaXNhT1b3IWbHYMGpOkhEaGF11lu6');
/*!40000 ALTER TABLE `banker` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction`
--

DROP TABLE IF EXISTS `transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reference` varchar(50) NOT NULL,
  `description` text,
  `amount` decimal(15,2) NOT NULL,
  `transaction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `transaction_type` enum('withdrawal','deposit','transfer') NOT NULL,
  `account_id` int NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `destination_account_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `account_id` (`account_id`),
  KEY `destination_account_id` (`destination_account_id`),
  CONSTRAINT `transaction_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE CASCADE,
  CONSTRAINT `transaction_ibfk_2` FOREIGN KEY (`destination_account_id`) REFERENCES `account` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction`
--

LOCK TABLES `transaction` WRITE;
/*!40000 ALTER TABLE `transaction` DISABLE KEYS */;
INSERT INTO `transaction` VALUES (1,'TX002','Test deposit',100.00,'2025-03-20 14:27:47','deposit',1,'test',NULL),(2,'TX003','Test withdrawal',50.00,'2025-03-20 14:35:51','withdrawal',1,'test',NULL),(4,'TX004','Test transfer',30.00,'2025-03-20 14:39:26','transfer',1,'test',2),(5,'TX005','Test withdrawal',1000.00,'2025-03-20 14:47:20','withdrawal',1,'test',NULL),(6,'TX001','Test deposit',100.00,'2025-03-21 03:14:25','deposit',3,'test',NULL),(7,'TX6155','TEST',200.00,'2025-03-21 03:37:07','deposit',3,'Revenu',NULL),(8,'TX1984','test',1000.00,'2025-03-21 16:57:30','deposit',4,'Revenu',NULL),(9,'TX8970','test',100.00,'2025-03-21 17:06:48','deposit',4,'Loisir',NULL),(10,'TX2928','test',1000.00,'2025-03-21 17:15:42','withdrawal',4,'Loisir',NULL),(11,'TX3363','test',50.00,'2025-03-22 13:27:55','transfer',4,'Loisir',5),(12,'TX8290','test',100.00,'2025-03-24 04:45:54','deposit',4,'Income',NULL),(13,'TX9273','test',100.00,'2025-03-24 04:45:55','deposit',4,'Income',NULL),(14,'TX9182','test',45.00,'2025-03-24 04:46:23','withdrawal',4,'Leisure',NULL),(15,'TX5518','tes',5.00,'2025-03-24 04:46:48','transfer',4,'Leisure',5),(16,'TX8470','test',1500.00,'2025-03-24 05:08:28','deposit',4,'Leisure',NULL),(17,'TX8946','test',5.00,'2025-03-24 05:20:08','deposit',4,'Leisure',NULL),(18,'TX8396','test',57.00,'2025-03-24 05:20:51','withdrawal',4,'Leisure',NULL),(19,'TX3085','TEST',67.94,'2025-03-24 05:21:18','transfer',4,'Leisure',5),(20,'TX7383','test',1580.00,'2025-03-24 05:39:39','withdrawal',4,'Leisure',NULL),(21,'TX8770','test',122.00,'2025-03-24 05:40:50','withdrawal',5,'Leisure',NULL),(22,'TX3566','test',10.00,'2025-03-24 08:33:45','deposit',4,'Leisure',NULL),(23,'TX6069','test',10.00,'2025-03-24 08:34:21','transfer',4,'Leisure',5);
/*!40000 ALTER TABLE `transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `creation_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `banker_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `banker_id` (`banker_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`banker_id`) REFERENCES `banker` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Smith','John','john.smith@example.com','$2b$12$rEIewJkyUTwhva.aw2tkhuDQeqnPf20sChle9R0NTrdkC.dGDgC3y','2025-03-19 11:25:04',1),(2,'joel','Messina','Veromessij@gmail.com','$2b$12$8ECZmYMpkpavzg61JBeagO5XO9kqzuycDTirXlpjaplGck94PLRae','2025-03-20 15:10:52',1),(3,'ribamonti','axel','axel@gmail.com','$2b$12$faLFMsRxYeAcScstWvJ9COqT9hcHSu/7yviW63cJ2rVIUzQVgQN4O','2025-03-21 14:52:33',1),(4,'ricart','lucas','lucas@gmail.com','$2b$12$4loGjtInGk9ZS6sTknwiG.lqu9DI/g4UBpC.pwB9gNoX8LV594kUO','2025-03-21 14:54:00',1),(5,'verom','joel','joel@gmail.com','$2b$12$c7LxCni.CAKYwQg5S5yXeOaIIycadhHX2L29uc9C/VieEC1Wg.da6','2025-03-21 16:25:15',1),(6,'vvv','vv','vv@gmail','$2b$12$tpG/k8pw8N.W6ihAGR/6Duzio11AyGpaweTtZU7V3EYlu6qONj0o2','2025-03-24 04:44:10',1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-24 10:35:27
