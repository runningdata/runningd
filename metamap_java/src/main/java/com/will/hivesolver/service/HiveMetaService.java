package com.will.hivesolver.service;

import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import com.will.hivesolver.repositories.ColMetaRepository;
import com.will.hivesolver.util.JsonUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import com.will.hivesolver.entity.ColMeta;
import org.springframework.transaction.annotation.Transactional;

@Service("hiveMetaService")
public class HiveMetaService {

    private static Logger log = LoggerFactory.getLogger(HiveMetaService.class);

    @Resource(name = "hivemetaJdbcTemplate")
    private JdbcTemplate hivemetaJdbcTemplate;

    @Resource(name = "metamapJdbcTemplate")
    private JdbcTemplate metamapJdbcTemplate;

    @Resource
    private ColMetaRepository colMetaRepository;

    public Object executeSql(String sql) {
        return metamapJdbcTemplate.queryForList(sql);
    }

    public List<ColMeta> getAll() {
        return colMetaRepository.findAll();
    }

    public boolean deleteAll() {
        colMetaRepository.deleteAll();
        return true;
    }

    @Transactional
    public String prepareColMeta() {
        String sql = "  SELECT\n" +
                "    db.DB_ID as db_id,\n" +
                "    db.`NAME` as db_name,\n" +
                "    a.TBL_ID as tbl_id,\n" +
                "    a.TBL_NAME as tbl_name,\n" +
                "    a.TBL_TYPE as tbl_type,\n" +
                "    d.TYPE_NAME as col_type_name,\n" +
                "    d.`COMMENT` as col_comment,\n" +
                "    d.COLUMN_NAME as col_name\n" +
                "FROM\n" +
                "    TBLS a\n" +
                "LEFT JOIN SDS b ON a.SD_ID = b.SD_ID\n" +
                "LEFT JOIN COLUMNS_V2 d ON b.CD_ID = d.CD_ID\n" +
                "LEFT JOIN DBS db ON a.DB_ID = db.DB_ID";
        final List<Map<String, Object>> list = hivemetaJdbcTemplate.queryForList(sql);


        String insert = "insert into col_tbl_db(db_name, db_id,tbl_id,tbl_name" +
                ",col_type_name,col_comment,col_name,tbl_type) " +
                "values(?,?,?,?,?,?,?,?)";
        metamapJdbcTemplate.batchUpdate(insert, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                String db_name = list.get(i).get("db_name").toString();
                int db_id = Integer.valueOf(list.get(i).get("db_id").toString());
                int tbl_id = Integer.valueOf(list.get(i).get("tbl_id").toString());
                String tbl_name = list.get(i).get("tbl_name").toString();
                String tbl_type = list.get(i).get("tbl_type").toString();
                String col_type_name = list.get(i).get("col_type_name").toString();
                String col_comment = null;
                Object comment = list.get(i).get("col_comment");
                if (null != comment) {
                    col_comment = comment.toString();
                }
                String col_name = list.get(i).get("col_name").toString();
                ps.setString(1, db_name);
                ps.setInt(2, db_id);
                ps.setInt(3, tbl_id);
                ps.setString(4, tbl_name);
                ps.setString(5, col_type_name);
                ps.setString(6, col_comment);
                ps.setString(7, col_name);
                ps.setString(8, tbl_type);
            }

            @Override
            public int getBatchSize() {
                return list.size();
            }
        });
        return "success";
    }

    public List<ColMeta> search(String colName) {
        return colMetaRepository.findByColName(colName);
    }

    public Map tblInfo(ColMeta meta) {
        Map<String, Object> result = new HashMap<String, Object>();
        List<ColMeta> cols = colMetaRepository.findByDbIdAndTblId(meta.getDbId(), meta.getTblId());

        Map<String, Object> tbl = hivemetaJdbcTemplate.queryForMap("select tbl.*,db.name as db_name from hive1.TBLS tbl" +
                " join hive1.DBS db on db.db_id = tbl.db_id " +
                " where tbl.tbl_id = " + meta.getTblId());
        result.put("cols", cols);
        result.put("tbl", tbl);
        return result;
    }
}
