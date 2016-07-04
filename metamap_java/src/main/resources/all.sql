SELECT
	db.DB_ID,
	db.`NAME` as db_name,
	a.TBL_ID,
	a.TBL_NAME,
	a.TBL_TYPE,
	d.TYPE_NAME as col_type_name,
	d.`COMMENT` as col_comment,
	d.COLUMN_NAME as col_name
FROM
	TBLS a
LEFT JOIN SDS b ON a.SD_ID = b.SD_ID
LEFT JOIN COLUMNS_V2 d ON b.CD_ID = d.CD_ID
LEFT JOIN DBS db ON a.DB_ID = db.DB_ID
