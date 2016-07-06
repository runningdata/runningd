package com.will.hivesolver.service;

import java.io.File;
import java.io.IOException;
import java.util.*;

import javax.annotation.Resource;

import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.hadoop.hive.metastore.api.MetaException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.google.common.base.Joiner;
import com.will.hivesolver.HiveJdbcClient;
import com.will.hivesolver.dao.IETLDao;
import com.will.hivesolver.dao.ITblBloodDao;
import com.will.hivesolver.entity.ETL;
import com.will.hivesolver.entity.Node;
import com.will.hivesolver.entity.TblBlood;
import com.will.hivesolver.util.DateUtil;
import com.will.hivesolver.util.JsonUtil;
import com.will.hivesolver.util.ZipUtils;

@Service("etlService")
public class ETLService {

    private static Logger log = LoggerFactory.getLogger(ETLService.class);
    
    private final String AZKABAN_BASE_LOCATION = "/tmp/";
    
    private final String AZKABAN_SCRIPT_LOCATION = "/var/azkaban-metamap/";

    private final String TMP_SCRIPT_LOCATION = "/var/metamap-tmp/";

    Joiner joiner =  Joiner.on(",");

    @Resource(name = "etlDao")
    private IETLDao etlDao;

    @Resource(name = "tblBloodDao")
    private ITblBloodDao tblBloodDao;

    /**
     * 获取所有的ETL
     *
     * TODO: 权限  +  分页
     */
    public Object allETL() {
        return etlDao.selectAllValidETL();
    }

    /**
     * 新增一个ETL
     * @param etl
     */
    @Transactional
    public  void addETL(ETL etl) {
        // must after tbl blood analyse?
        etlDao.makePreviousInvalid(etl.getTblName());
        etlDao.insertSingleETL(etl);
        int etlId = etlDao.getETLByTblName(etl.getTblName()).get(0).getId();


        tblBloodDao.makePreviousInvalid(etl.getTblName());
        Set<String> parents = HiveJdbcClient.get(etl.getQuery());
        TblBlood blood = null;
        for (String parent : parents) {
            blood = new TblBlood();
            blood.setParentTbl(parent);
            blood.setRelatedEtlId(etlId);
            blood.setTblName(etl.getTblName());
            blood.setUtime(System.currentTimeMillis()/1000);
            tblBloodDao.insertOne(blood);
        }

    }

    public Set<TblBlood> getETLMermaid(int id) {
        List<TblBlood> selectAllValidETL = tblBloodDao.selectByETLId(id);
        Set<TblBlood> tblBloods = new HashSet<TblBlood>();
        if (selectAllValidETL.size() > 0) {
            TblBlood blood = selectAllValidETL.get(0);
            tblBloods.add(blood);

            // 找上游
            getParent(blood, tblBloods);

            // 找下游
            getChildren(tblBloods, blood);
        }
        return tblBloods;
    }

    public Set<TblBlood> getETLMermaid(String tbl_name) {
        List<TblBlood> selectAllValidETL = tblBloodDao.selectByTblName(tbl_name);
        Set<TblBlood> tblBloods = new HashSet<TblBlood>();
        if (selectAllValidETL.size() > 0) {
            TblBlood blood = selectAllValidETL.get(0);
            tblBloods.add(blood);

            // 找上游
            getParent(blood, tblBloods);

            // 找下游
            getChildren(tblBloods, blood);
        }
        return tblBloods;
    }

    /**
     * 返回当前所有有效的ETL
     * @return
     */
    public Node getETLTree(String tbl_name) {
        Node root = null;
        List<TblBlood> selectAllValidETL = tblBloodDao.selectByTblName(tbl_name);
        Map<String, Node> nodeCache = new HashMap<String, Node>();
        if (selectAllValidETL.size() > 0) {
            root = new Node();
            root.setName("root");
            
            TblBlood blood = selectAllValidETL.get(0);
            Node current = new Node();
            current.setCurrent(true);
            current.setName(blood.getTblName());
            nodeCache.put(blood.getTblName(), current);
            
            // 找上游
            getParent(blood, nodeCache);
            
            // 找下游
            getChildren(nodeCache, blood);
            
            int maxLevel = 0;
            for (Node node : nodeCache.values()) {
                if (maxLevel < node.getLevel()) {
                    maxLevel = node.getLevel();
                }
            }
            
            for (Node node : nodeCache.values()) {
                if (maxLevel == node.getLevel()) {
                    root.addChild( node);
                }
            }

            try {
                System.out.println("rrrr L >>" + JsonUtil.getMapperInstance(false).writeValueAsString(root));
                System.out.println(JsonUtil.getMapperInstance(false).writeValueAsString(current));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return root;
    }
    
    /**
     * 生成azkaban job文件
     * 
     * 1. 找出没有被任何其他ETL以来的叶子节点
     * 2. 遍历所有叶子节点，找到这个叶子节点的所有有效依赖，放入dependencies里，
     * 如果尚未生成该ETL的job文件
     * 3. 向上递归执行，直到没有dependency的节点，也就是最上一层节点就停止。
     * @return
     * @throws MetaException 
     * @throws ArchiveException 
     */
    public String generateAzkabanDAG() throws MetaException, ArchiveException {
        try {
            String serFolder = DateUtil.getTodayDateTime();
            List<TblBlood> leafBlood = tblBloodDao.selectAllLeaf();
            Set<String> doneBlood = new HashSet<String>();
            String serFolderLocation = AZKABAN_BASE_LOCATION + serFolder;
            if (leafBlood.size() > 0) {
                loadLeafBloods(leafBlood, doneBlood, serFolder);
            }
            TblBlood tbl = new TblBlood();
            tbl.setTblName("etl_done_" + serFolder);
            generateJobFile(tbl, leafBlood, serFolder);
            ZipUtils.addFilesToZip(new File(serFolderLocation), 
                    new File(serFolderLocation + ".zip"));
        } catch (IOException e) {
            log.error("error happends when generateAzkabanDAG");
            throw new MetaException("error happends when generateAzkabanDAG");
        }
        return null;
    }

    

    private void loadLeafBloods(List<TblBlood> leafBlood, Set<String> doneBlood, String serFolder) throws IOException {
        for (TblBlood leaf : leafBlood) {
            List<TblBlood> parentNode = tblBloodDao.selectParentByTblName(leaf.getTblName());
            if (!doneBlood.contains(leaf.getTblName())) {
                generateJobFile(leaf, parentNode, serFolder);
                doneBlood.add(leaf.getTblName());
            }
            loadLeafBloods(parentNode, doneBlood, serFolder);
        }
    }


    private void generateJobFile(TblBlood currentBlood,  List<TblBlood> parentNode, String serFolder) throws IOException {
        String jobName = currentBlood.getTblName();
        File file;
        String command;
        if (!jobName.startsWith("etl_done_")) {
            // 生成hql文件
            String hqlLocation = AZKABAN_SCRIPT_LOCATION + serFolder + "/" + jobName + ".hql";
            file = new File(hqlLocation);
            StringBuilder sb = new StringBuilder();
            List<ETL> currentETL = etlDao.getETLByTblName(jobName);
            if (!currentETL.isEmpty()) {
                ETL etl = currentETL.get(0);
                sb.append(etl.getPreSql()).append("\n");
                sb.append(etl.getQuery());
            }
            if (sb.length() > 1) {
                FileUtils.write(file, sb.toString(), "utf8", false);
            }
            command = "hive -f " + hqlLocation;
        } else {
            command = "echo " + jobName;
        }
        
        // 生成job文件
        String jobType = "command";
        String content;
        Set<String> dependencies = new HashSet<String>();
        for (TblBlood blood : parentNode) {
            dependencies.add(blood.getTblName());
        }
        String jobDependencies = joiner.join(dependencies);
        content = "# " + jobName + "\n"
                + "type=" + jobType +"\n"
                        + "command=" + command + "\n";
        if (StringUtils.isNotBlank(jobDependencies)) {
            content += "dependencies=" + jobDependencies +"\n";
        }
        file = new File(AZKABAN_BASE_LOCATION + serFolder + "/" + jobName + ".job");
        FileUtils.write(file, content, "utf8", false);
        System.out.println(">>>>>>>>>>>>>>>>>\n" + content);
    }


    /**
     * 当找不到任何子节点的时候迭代结束
     * @param nodeCache
     * @param blood
     */
    private void getChildren(Map<String, Node> nodeCache, TblBlood blood) {
        List<TblBlood> children = tblBloodDao.selectByParentTblName(blood.getTblName());
        if (children.size() > 0) {
            for (TblBlood tblBlood : children) {
                    Node c = new Node();
                    Node node = nodeCache.get(blood.getTblName());
                    node.addChild(c);
                    c.setLevel(node.getLevel() - 1);
                    c.setName(tblBlood.getTblName());
                    nodeCache.put(tblBlood.getTblName(), c);
                    getChildren(nodeCache, tblBlood);
            }
        }
    }


    /**
     * 当找不到任何父节点的时候结束
     * @param blood
     * @param nodeCache
     */
    private void getParent(TblBlood blood,
             Map<String, Node> nodeCache) {
        List<TblBlood> parent = tblBloodDao.selectByTblName(blood.getParentTbl());
        if (parent.size() > 0) {
            for (TblBlood tblBlood : parent) {
                Node p = new Node();
                Node node = nodeCache.get(blood.getTblName());
//                node.addParent(p);
                p.addChild(node);
                p.setLevel(node.getLevel() + 1);
                p.setName(tblBlood.getTblName());
                nodeCache.put(tblBlood.getTblName(), p);
                if (StringUtils.isNotBlank(tblBlood.getParentTbl())) {
                    getParent(tblBlood, nodeCache);
                }
            }
        }
    }



    /**
     * 当找不到任何父节点的时候结束
     * @param blood
     * @param tblBloods
     */
    private void getParent(TblBlood blood,
                           Set<TblBlood> tblBloods) {
        List<TblBlood> parent = tblBloodDao.selectByTblName(blood.getParentTbl());
        if (parent.size() > 0) {
            for (TblBlood tblBlood : parent) {
                tblBloods.add(tblBlood);
                if (StringUtils.isNotBlank(tblBlood.getParentTbl())) {
                    getParent(tblBlood, tblBloods);
                }
            }
        }
    }

    /**
     * 当找不到任何子节点的时候迭代结束
     * @param tblBloods
     * @param blood
     */
    private void getChildren(Set<TblBlood> tblBloods, TblBlood blood) {
        List<TblBlood> children = tblBloodDao.selectByParentTblName(blood.getTblName());
        if (children.size() > 0) {
            for (TblBlood tblBlood : children) {
                tblBloods.add(tblBlood);
                getChildren(tblBloods, tblBlood);
            }
        }
    }

    public ETL getETLById(int id) {
        return etlDao.getETLById(id).get(0);
    }

    public Object generateETLScript(int id) throws IOException {
        Map<String, Object> result = new HashMap<String, Object>();
        ETL etl = etlDao.getETLById(id).get(0);
        String location = TMP_SCRIPT_LOCATION + DateUtil.getDateTime(new Date(), "yyyyMMddHHmmss") + "-" + etl.getTblName() + ".sh";
                StringBuffer sb  = new StringBuffer();
        sb.append("# job for " + etl.getTblName() + "\n");
        sb.append("# author : " + etl.getAuthor() + "\n");
        sb.append("# create time : " + DateUtil.getDateTime(new Date(etl.getCtime()), "yyyyMMddHHmmss") + "\n");
        sb.append("# pre settings " +"\n");
        sb.append(etl.getPreSql() + "\n");
        sb.append(etl.getQuery());
        FileUtils.write(new File(location), sb.toString(), "utf8", false);
        result.put("message", "success");
        result.put("location", location);
        return result;
    }
}
