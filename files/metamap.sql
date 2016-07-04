/*
Navicat MySQL Data Transfer

Source Server         : 113
Source Server Version : 50625
Source Host           : 10.1.5.113:3306
Source Database       : hivedb

Target Server Type    : MYSQL
Target Server Version : 50625
File Encoding         : 65001

Date: 2016-07-01 18:37:59
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for col_tbl_db
-- ----------------------------
DROP TABLE IF EXISTS `col_tbl_db`;
CREATE TABLE `col_tbl_db` (
`db_id`  int(11) NOT NULL ,
`db_name`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`tbl_id`  int(11) NOT NULL ,
`tbl_name`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`tbl_type`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`col_type_name`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`col_comment`  varchar(150) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ,
`col_name`  varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL 
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci

;

-- ----------------------------
-- Records of col_tbl_db
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for etl
-- ----------------------------
DROP TABLE IF EXISTS `etl`;
CREATE TABLE `etl` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`query`  varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'sql语句' ,
`meta`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '数据库' ,
`tbl_name`  varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '表名' ,
`author`  varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建人' ,
`pre_sql`  varchar(2000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '先执行的sql' ,
`priority`  int(5) NOT NULL DEFAULT 5 ,
`on_schedule`  tinyint(4) NULL DEFAULT NULL COMMENT '0 不调度 1 调度中' ,
`valid`  tinyint(4) NULL DEFAULT NULL ,
`ctime`  bigint(20) NULL DEFAULT NULL ,
`utime`  bigint(20) NULL DEFAULT NULL ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
AUTO_INCREMENT=18

;

-- ----------------------------
-- Records of etl
-- ----------------------------
BEGIN;
INSERT INTO `etl` VALUES ('1', 'select * from batting', 'default', 'batting', 'will', 'delete from default.tbl', '0', '1', '1', '1465297644', '1465297644'), ('2', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '0', '1465716103', '1465716103'), ('3', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '0', '1465716473', '1465716473'), ('4', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '0', '1465716722', '1465716722'), ('12', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '0', '1465717609', '1465717609'), ('14', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '0', '1465720686', '1465720686'), ('15', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '0', '1465720788', '1465720788'), ('16', 'select * from batting', 'mymeta', 'my_table', 'will', 'delete from default.tbl', '0', '1', '1', '1465720899', '1465720899'), ('17', 'select * from ttt', 'mymeta', 'my_table_p2', 'will', 'set mapred.map.tasks=10', '5', '1', '1', null, null);
COMMIT;

-- ----------------------------
-- Table structure for tbl_blood
-- ----------------------------
DROP TABLE IF EXISTS `tbl_blood`;
CREATE TABLE `tbl_blood` (
`id`  int(11) NOT NULL AUTO_INCREMENT ,
`tbl_name`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`parent_tbl`  varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ,
`related_etl_id`  int(11) NOT NULL ,
`valid`  tinyint(4) NOT NULL DEFAULT 0 ,
`ctime`  bigint(20) NULL DEFAULT 0 ,
`utime`  bigint(20) NULL DEFAULT 0 ,
PRIMARY KEY (`id`)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=latin1 COLLATE=latin1_swedish_ci
AUTO_INCREMENT=21

;

-- ----------------------------
-- Records of tbl_blood
-- ----------------------------
BEGIN;
INSERT INTO `tbl_blood` VALUES ('9', 'mymeta@my_table', 'default@batting', '16', '1', '0', '1465720901'), ('10', 'mymeta@my_table_c', 'mymeta@my_table', '1', '1', '0', '0'), ('11', 'default@batting', 'mymeta@my_table_p', '2', '1', '0', '0'), ('12', 'mymeta@my_table_p', 'mymeta@my_table_p2', '1', '1', '0', '0'), ('13', 'mymeta@my_table_c2', 'mymeta@my_table_c', '2', '1', '0', '0'), ('14', 'mymeta@my_table_p2', '', '1', '1', '0', '0'), ('15', 'mymeta@my_table_p', 'mymeta@my_table_pp', '1', '1', '0', '0'), ('16', 'mymeta@my_table_pp', 'mymeta@my_table_pp2', '1', '1', '0', '0'), ('17', 'mymeta@my_table_cc', 'mymeta@my_table_c', '1', '1', '0', '0'), ('18', 'mymeta@my_table_cc2', 'mymeta@my_table_cc', '1', '1', '0', '0'), ('20', 'mymeta@my_table', 'default@batting', '16', '1', '0', '1465973359');
COMMIT;

-- ----------------------------
-- Auto increment value for etl
-- ----------------------------
ALTER TABLE `etl` AUTO_INCREMENT=18;

-- ----------------------------
-- Auto increment value for tbl_blood
-- ----------------------------
ALTER TABLE `tbl_blood` AUTO_INCREMENT=21;
