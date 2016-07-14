package com.will.hivesolver;

import java.io.IOException;
import java.sql.SQLException;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.DriverManager;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.will.hivesolver.util.PropertiesUtils;
import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

import com.will.hivesolver.util.JsonUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class HiveJdbcClient {
    private String HIVE_SERVER_DRIVER = "org.apache.hive.jdbc.HiveDriver";

    @Autowired
    private PropertiesUtils propertiesUtils;

    private String HIVE_SERVER_URL;
    private String HIVE_SERVER_USER;
    private String HIVE_SERVER_PWD;
    {
        HIVE_SERVER_URL = propertiesUtils.getPropertiesValue("hive.server.url");
        HIVE_SERVER_USER = propertiesUtils.getPropertiesValue("hive.server.user");
        HIVE_SERVER_URL = propertiesUtils.getPropertiesValue("hive.server.password");
        HIVE_SERVER_DRIVER = propertiesUtils.getPropertiesValue("hive.server.driver");
    }


    public Set<String> get(String sql) {
        sql = sql.substring(sql.toLowerCase().indexOf("select"), sql.length());
        try {
            Class.forName(HIVE_SERVER_DRIVER);
        } catch (ClassNotFoundException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            System.exit(1);
        }
        Connection con = null;
        Statement stmt = null;
        try {
            con = DriverManager.getConnection(HIVE_SERVER_URL, HIVE_SERVER_USER, HIVE_SERVER_PWD);
            stmt = con.createStatement();
            // show tables
//        String sql = "show tables ";
//        System.out.println("Running: " + sql);
//        ResultSet res = stmt.executeQuery(sql);
//        if (res.next()) {
//          System.out.println(res.getString(1));
//        }

            // explain select
            sql = "explain dependency " + sql;
            System.out.println("Running: " + sql);
            ResultSet res = stmt.executeQuery(sql);
            if (res.next()) {
                String json = res.getString(1);
                System.out.println("json is : " + json);
                ObjectMapper mapper = JsonUtil.getMapperInstance(false);
                return getTbls(json, mapper);
            }
        } catch (SQLException | IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (stmt != null && stmt.isClosed() == false) {
                    stmt.close();
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
            try {
                if (con != null && con.isClosed() == false) {
                    con.close();
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        return null;
    }

    /**
     * extract dependency tables from hql
     *
     * @param json
     * @param mapper
     * @throws IOException
     * @throws JsonParseException
     * @throws JsonMappingException
     */
    private static Set<String> getTbls(String json, ObjectMapper mapper)
            throws IOException, JsonParseException, JsonMappingException {
        Map<String, Object> map = mapper.readValue(json, Map.class);
        List<Map<String, String>> tbMap = (List<Map<String, String>>) map.get("input_tables");
        Set<String> tbls = new HashSet<String>();
        for (Map<String, String> mp : tbMap) {
            tbls.add(mp.get("tablename"));
        }
        return tbls;
    }
}