/*
Navicat MySQL Data Transfer

Source Server         : 10.0.0.29
Source Server Version : 50530
Source Host           : 10.0.0.29:3306
Source Database       : xio

Target Server Type    : MYSQL
Target Server Version : 50530
File Encoding         : 65001

Date: 2013-03-26 09:53:43
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `tb_xweibo_comments_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_comments_info`;
CREATE TABLE `tb_xweibo_comments_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wid` varchar(20) NOT NULL,
  `uid` bigint(20) DEFAULT NULL,
  `text` text,
  `source` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `commented_status_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wid` (`wid`) USING BTREE,
  KEY `idx_uid` (`uid`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_comments_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_comments_user_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_comments_user_info`;
CREATE TABLE `tb_xweibo_comments_user_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` bigint(20) DEFAULT NULL,
  `screen_name` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `province` varchar(8) DEFAULT NULL,
  `city` varchar(8) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text,
  `url` varchar(255) DEFAULT NULL,
  `profile_image_url` varchar(255) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `gender` char(2) DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `friends_count` int(11) DEFAULT NULL,
  `statuses_count` int(11) DEFAULT NULL,
  `favourites_count` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `verified` tinyint(4) DEFAULT NULL,
  `verified_type` int(11) DEFAULT NULL,
  `verified_reason` varchar(255) DEFAULT NULL,
  `bi_followers_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`uid`),
  KEY `idx_friends_count` (`friends_count`) USING BTREE,
  KEY `indx_followers_counts` (`followers_count`) USING BTREE,
  KEY `idx_verified` (`verified`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_comments_user_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_followers_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_followers_info`;
CREATE TABLE `tb_xweibo_followers_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` bigint(20) DEFAULT NULL,
  `screen_name` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `province` varchar(8) CHARACTER SET utf8 DEFAULT NULL,
  `city` varchar(8) CHARACTER SET utf8 DEFAULT NULL,
  `location` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `description` text CHARACTER SET utf8,
  `url` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `profile_image_url` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `domain` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `gender` char(2) CHARACTER SET utf8 DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `friends_count` int(11) DEFAULT NULL,
  `statuses_count` int(11) DEFAULT NULL,
  `favourites_count` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `verified` tinyint(4) DEFAULT NULL,
  `verified_type` int(11) DEFAULT NULL,
  `verified_reason` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `bi_followers_count` int(11) DEFAULT NULL,
  `follow_who` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uid` (`uid`,`follow_who`) USING BTREE,
  KEY `idx_friends_count` (`friends_count`) USING BTREE,
  KEY `indx_followers_counts` (`followers_count`) USING BTREE,
  KEY `idx_verified` (`verified`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_followers_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_friendship`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_friendship`;
CREATE TABLE `tb_xweibo_friendship` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` bigint(20) DEFAULT NULL,
  `fid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uni` (`uid`,`fid`) USING BTREE,
  KEY `idx_uid` (`uid`),
  KEY `idx_fid` (`fid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_friendship
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_info`;
CREATE TABLE `tb_xweibo_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wid` varchar(20) CHARACTER SET utf8 NOT NULL,
  `uid` bigint(20) DEFAULT NULL,
  `text` text CHARACTER SET utf8,
  `url` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `source` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `thumbnail_pic` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `bmiddle_pic` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `original_pic` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `comments` int(11) NOT NULL DEFAULT '-1',
  `rt` int(11) NOT NULL DEFAULT '-1',
  `retweeted_status_id` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wid` (`wid`) USING BTREE,
  KEY `idx_uid` (`uid`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE,
  KEY `idx_comments` (`comments`) USING BTREE,
  KEY `idx_rt` (`rt`) USING BTREE,
  KEY `idx_retweeted_status_id` (`retweeted_status_id`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_reposts_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_reposts_info`;
CREATE TABLE `tb_xweibo_reposts_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wid` bigint(20) NOT NULL,
  `uid` bigint(20) DEFAULT NULL,
  `text` text,
  `url` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `thumbnail_pic` varchar(255) DEFAULT NULL,
  `bmiddle_pic` varchar(255) DEFAULT NULL,
  `original_pic` varchar(255) DEFAULT NULL,
  `comments` int(11) NOT NULL DEFAULT '-1',
  `rt` int(11) NOT NULL DEFAULT '-1',
  `retweeted_status_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wid` (`wid`) USING BTREE,
  KEY `idx_uid` (`uid`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE,
  KEY `idx_comments` (`comments`) USING BTREE,
  KEY `idx_rt` (`rt`) USING BTREE,
  KEY `idx_retweeted_status_id` (`retweeted_status_id`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_reposts_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_reposts_user_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_reposts_user_info`;
CREATE TABLE `tb_xweibo_reposts_user_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` bigint(20) DEFAULT NULL,
  `screen_name` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `province` varchar(8) DEFAULT NULL,
  `city` varchar(8) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text,
  `url` varchar(255) DEFAULT NULL,
  `profile_image_url` varchar(255) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `gender` char(2) DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `friends_count` int(11) DEFAULT NULL,
  `statuses_count` int(11) DEFAULT NULL,
  `favourites_count` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `verified` tinyint(4) DEFAULT NULL,
  `verified_type` int(11) DEFAULT NULL,
  `verified_reason` varchar(255) DEFAULT NULL,
  `bi_followers_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`uid`),
  KEY `idx_friends_count` (`friends_count`) USING BTREE,
  KEY `indx_followers_counts` (`followers_count`) USING BTREE,
  KEY `idx_verified` (`verified`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_reposts_user_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_user_info`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_user_info`;
CREATE TABLE `tb_xweibo_user_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` bigint(20) DEFAULT NULL,
  `screen_name` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `province` varchar(8) DEFAULT NULL,
  `city` varchar(8) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text,
  `url` varchar(255) DEFAULT NULL,
  `profile_image_url` varchar(255) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `gender` char(2) DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `friends_count` int(11) DEFAULT NULL,
  `statuses_count` int(11) DEFAULT NULL,
  `favourites_count` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `verified` tinyint(4) DEFAULT NULL,
  `verified_type` int(11) DEFAULT NULL,
  `verified_reason` varchar(255) DEFAULT NULL,
  `bi_followers_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uid` (`uid`) USING BTREE,
  KEY `idx_friends_count` (`friends_count`) USING BTREE,
  KEY `indx_followers_counts` (`followers_count`) USING BTREE,
  KEY `idx_verified` (`verified`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_user_info
-- ----------------------------

-- ----------------------------
-- Table structure for `tb_xweibo_user_tags`
-- ----------------------------
DROP TABLE IF EXISTS `tb_xweibo_user_tags`;
CREATE TABLE `tb_xweibo_user_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tid` int(11) DEFAULT NULL,
  `uid` bigint(20) DEFAULT NULL,
  `tag` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uni` (`tid`,`uid`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of tb_xweibo_user_tags
-- ----------------------------
