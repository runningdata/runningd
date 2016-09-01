ALTER TABLE `djcelery_periodictask` ADD COLUMN `etl_id` integer NULL;
ALTER TABLE `djcelery_periodictask` ALTER COLUMN `etl_id` DROP DEFAULT;
CREATE INDEX `djcelery_periodictask_3c540a78` ON `djcelery_periodictask` (`etl_id`);
ALTER TABLE `djcelery_periodictask` ADD CONSTRAINT `djcelery_periodictask_etl_id_f058f0b9_fk_metamap_etl_id` FOREIGN KEY (`etl_id`) REFERENCES `metamap_etl` (`id`);