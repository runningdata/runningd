package com.will.hivesolver.service;

import java.io.File;
import java.io.IOException;
import java.util.*;

import javax.annotation.Resource;

import com.will.hivesolver.entity.Execution;
import com.will.hivesolver.repositories.ETLRepository;
import com.will.hivesolver.repositories.ExecutionRepository;
import com.will.hivesolver.repositories.TblBloodRepository;
import com.will.hivesolver.util.*;
import com.will.hivesolver.util.enums.ExecutionStatusEnum;
import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.hadoop.hive.metastore.api.MetaException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.google.common.base.Joiner;
import com.will.hivesolver.HiveJdbcClient;
import com.will.hivesolver.dao.IETLDao;
import com.will.hivesolver.dao.ITblBloodDao;
import com.will.hivesolver.entity.ETL;
import com.will.hivesolver.entity.Node;
import com.will.hivesolver.entity.TblBlood;

import static com.will.hivesolver.util.ETLConsts.AZKABAN_BASE_LOCATION;
import static com.will.hivesolver.util.ETLConsts.AZKABAN_SCRIPT_LOCATION;
import static com.will.hivesolver.util.ETLConsts.TMP_SCRIPT_LOCATION;

@Service("etlService")
public class ETLService {

    private static Logger log = LoggerFactory.getLogger(ETLService.class);

    Joiner joiner = Joiner.on(",");

    @Resource(name = "etlDao")
    private IETLDao etlDao;

    @Resource(name = "tblBloodDao")
    private ITblBloodDao tblBloodDao;

    @Resource
    private TblBloodRepository tblBloodRepository;

    @Resource
    private ETLRepository etlRepository;

    @Resource
    private ExecutionRepository executionRepository;

    @Resource
    HiveJdbcClient hiveJdbcClient;

    @Autowired
    ThreadPoolTaskExecutor threadPool;

    /**
     * 获取所有的ETL
     * <p>
     * TODO: 权限  +  分页
     */
    public Object allETL() {
        return etlDao.selectAllValidETL();
    }

    /**
     * 新增一个ETL
     *
     * @param etl
     */
    @Transactional
    public void addETL(ETL etl) throws Exception {
        // must after tbl blood analyse?
        etlRepository.makePreviousInvalid(etl.getTblName());
        etlRepository.save(etl);
        int etlId = etlRepository.getETLByTblName(etl.getTblName()).get(0).getId();


        tblBloodRepository.makePreviousInvalid(etl.getTblName());
        Set<String> parents = hiveJdbcClient.get(etl.getQuery());
        TblBlood blood = null;
        for (String parent : parents) {
            blood = new TblBlood();
            blood.setParentTbl(parent);
            blood.setRelatedEtlId(etlId);
            blood.setTblName(etl.getTblName());
            blood.setUtime(new Date());
            tblBloodRepository.save(blood);
        }

    }

    public Set<TblBlood> getETLMermaid(int id) {
        List<TblBlood> selectAllValidETL = tblBloodDao.selectByRelETLId(id);
        Set<TblBlood> tblBloods = new HashSet<TblBlood>();
        if (selectAllValidETL.size() > 0) {
            for (TblBlood blood : selectAllValidETL) {
                tblBloods.add(blood);

                // 找上游
                getMermaidParent(blood, tblBloods);

                // 找下游
                getMermaidChildren(tblBloods, blood);
            }
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
            getMermaidParent(blood, tblBloods);

            // 找下游
            getMermaidChildren(tblBloods, blood);
        }
        return tblBloods;
    }

    /**
     * 返回当前所有有效的ETL
     *
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
                    root.addChild(node);
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
     * <p>
     * 1. 找出没有被任何其他ETL以来的叶子节点
     * 2. 遍历所有叶子节点，找到这个叶子节点的所有有效依赖，放入dependencies里，
     * 如果尚未生成该ETL的job文件
     * 3. 向上递归执行，直到没有dependency的节点，也就是最上一层节点就停止。
     *
     * @return
     * @throws MetaException
     * @throws ArchiveException
     */
    public String generateAzkabanDAG() throws Exception {
        String serFolder = DateUtil.getTodayDateTime();
        List<TblBlood> leafBlood = tblBloodDao.selectAllLeaf();
        Set<String> doneBlood = new HashSet<String>();
        String serFolderLocation =  AZKABAN_BASE_LOCATION + serFolder;
        if (leafBlood.size() > 0) {
            loadLeafBloods(leafBlood, doneBlood, serFolder);
        }
        TblBlood tbl = new TblBlood();
        tbl.setTblName("etl_done_" + serFolder);
        generateJobFile(tbl, leafBlood, serFolder);
        ZipUtils.addFilesToZip(new File(serFolderLocation),
                new File(serFolderLocation + ".zip"));
        return serFolder;
    }


    private void loadLeafBloods(List<TblBlood> leafBlood, Set<String> doneBlood, String serFolder) throws Exception {
        for (TblBlood leaf : leafBlood) {
            List<TblBlood> parentNode = tblBloodDao.selectParentByTblName(leaf.getTblName());
            if (!doneBlood.contains(leaf.getTblName())) {
                generateJobFile(leaf, parentNode, serFolder);
                doneBlood.add(leaf.getTblName());
            }
            loadLeafBloods(parentNode, doneBlood, serFolder);
        }
    }


    private void generateJobFile(TblBlood currentBlood, List<TblBlood> parentNode, String serFolder) throws Exception {
        String jobName = currentBlood.getTblName();
        File file;
        String command;
        if (!jobName.startsWith("etl_done_")) {
            // 生成hql文件
            String hqlLocation = AZKABAN_SCRIPT_LOCATION + serFolder + "/" + jobName + ".hql";
            List<ETL> currentETL = etlDao.getETLByTblName(jobName);
            if (!currentETL.isEmpty()) {
                buildHqlFile(currentETL.get(0), hqlLocation);
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
                + "type=" + jobType + "\n"
                + "command=" + command + "\n";
        if (StringUtils.isNotBlank(jobDependencies)) {
            content += "dependencies=" + jobDependencies + "\n";
        }
        file = new File(AZKABAN_BASE_LOCATION + serFolder + "/" + jobName + ".job");
        FileUtils.write(file, content, "utf8", false);
        log.debug(">>>>>>>>>>>>>>>>>\n" + content);
    }


    /**
     * 当找不到任何子节点的时候迭代结束
     *
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
     *
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
     *
     * @param blood
     * @param tblBloods
     */
    private void getMermaidParent(TblBlood blood,
                                  Set<TblBlood> tblBloods) {
        List<TblBlood> parent = tblBloodDao.selectByTblName(blood.getParentTbl());
        if (parent.size() > 0) {
            for (TblBlood tblBlood : parent) {
                tblBloods.add(tblBlood);
                if (StringUtils.isNotBlank(tblBlood.getParentTbl())) {
                    getMermaidParent(tblBlood, tblBloods);
                }
            }
        }
    }

    /**
     * 当找不到任何子节点的时候迭代结束
     *
     * @param tblBloods
     * @param blood
     */
    private void getMermaidChildren(Set<TblBlood> tblBloods, TblBlood blood) {
        List<TblBlood> children = tblBloodDao.selectByParentTblName(blood.getTblName());
        if (children.size() > 0) {
            for (TblBlood tblBlood : children) {
                tblBloods.add(tblBlood);
                getMermaidChildren(tblBloods, tblBlood);
            }
        }
    }

    public ETL getETLById(int id) {
        return etlDao.getETLById(id).get(0);
    }

    public ETL getETLBId(int id) {
        return etlRepository.findOne(id);
    }

    @Transactional
    public Object execETLScript(int id) throws Exception {
        Map<String, Object> result = new HashMap<String, Object>();
        ETL etl = etlDao.getETLById(id).get(0);
        String scriptLocation = TMP_SCRIPT_LOCATION + DateUtil.getDateTime(new Date(), "yyyyMMddHHmmss") + "-" + etl.getTblName().replace("@","__") + ".hql";


        /**
         * Build the hql file.
         */
        String renderELTemplate = buildHqlFile(etl, scriptLocation);

        // create log file
        String logLocation = scriptLocation + ".log";
        FileUtils.writeStringToFile(new File(logLocation), renderELTemplate, "utf8", true);

        Execution exec = new Execution();
        exec.setJobId(etl.getId());
        exec.setStatus(ExecutionStatusEnum.SUBMIITED.get());
        exec.setLogLocation(logLocation);
        executionRepository.save(exec);
        // execution start
        threadPool.submit(new ETLTask(scriptLocation, exec));

        result.put("message", "success");
        result.put("exec", exec.getId());
        return result;
    }

    private String buildHqlFile(ETL etl, String scriptLocation) throws Exception {
        StringBuffer sb = new StringBuffer();
        sb.append("-- job for " + etl.getTblName() + "\n");
        sb.append("-- author : " + etl.getAuthor() + "\n");
        Date ctime = etl.getCtime();
        if (ctime != null) {
            sb.append("-- create time : " + DateUtil.getDateTime(ctime, "yyyyMMddHHmmss") + "\n");
        } else {
            sb.append("-- cannot find ctime");
        }
        sb.append("-- pre settings " + "\n");
        sb.append(etl.getPreSql() + "\n");
        sb.append(etl.getQuery());
        String renderELTemplate = SPELUtils.getRenderELTemplate(sb.toString());
        log.info("executing script: \n" + renderELTemplate);
        // save the hql file
        FileUtils.write(new File(scriptLocation), renderELTemplate, "utf8", false);
        return renderELTemplate;
    }


    public Execution getExecutionById(int id) {
        return executionRepository.findOne(id);
    }

    public Map<String, Object> getExecutionListByETLId(int id) {
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("execs", executionRepository.findByJobId(id));
        result.put("etl", etlRepository.findOne(id));
        return result;
    }

}
