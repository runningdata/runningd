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

import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

import com.will.hivesolver.util.JsonUtil;
 
public class HiveJdbcClient {
  private static String driverName = "org.apache.hive.jdbc.HiveDriver";

  public static void main(String[] s) {
      String sql = "select count(1) as num,userid from jlc.invest_record group by userid limit 100";
      try {
          Class.forName(driverName);
      } catch (ClassNotFoundException e) {
          // TODO Auto-generated catch block
          e.printStackTrace();
          System.exit(1);
      }
      Connection con = null;
      Statement stmt = null;
      try {
          con = DriverManager.getConnection("jdbc:hive2://10.1.5.80:10000/default", "hdfs", "");
          stmt = con.createStatement();
          // show tables
//        String sql = "show tables ";
//        System.out.println("Running: " + sql);
//        ResultSet res = stmt.executeQuery(sql);
//        if (res.next()) {
//          System.out.println(res.getString(1));
//        }

          // explain select
          System.out.println("Running: " + sql);
          ResultSet res = stmt.executeQuery(sql);
          while (res.next()) {
              System.out.println(res.getInt(1) + "-->" + res.getString(2));
          }
      } catch (SQLException e) {
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
  }
  
  public static Set<String> get(String sql)  {
    try {
      Class.forName(driverName);
    } catch (ClassNotFoundException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
      System.exit(1);
    }
    Connection con = null;
    Statement stmt = null;
    try {
        con = DriverManager.getConnection("jdbc:hive2://10.1.5.80:10000/default", "hdfs", "");
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
 * @param json
 * @param mapper
 * @throws IOException
 * @throws JsonParseException
 * @throws JsonMappingException
 */
private static Set<String> getTbls(String json, ObjectMapper mapper)
        throws IOException, JsonParseException, JsonMappingException {
    Map<String, Object> map = mapper.readValue(json, Map.class);
    List<Map<String, String>> tbMap = (List<Map<String, String>>)map.get("input_tables");
    Set<String> tbls = new HashSet<String>();
    for (Map<String, String> mp : tbMap) {
        tbls.add(mp.get("tablename"));
    }
    return tbls;
}
}