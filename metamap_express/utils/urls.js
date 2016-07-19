/**
 * 向后台请求的URL统一管理
 *
 *
 *
 */
'use strict';
var test = false;
var basePath = '/metamap';
var targetBasePath = '/target';
var mockPath = 'configs/data';

module.exports = {
    /*** 通用 ***/
  getEmployeeInfo: {
    name: '根据uid角色',
    path: '/org/getEmployeeInfo'
  },
  partTimeGetChart: {
    name: '获取兼职报表chart',
    path: '/parttime/salary/chart',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  editMeta: {
    name: '获取需要编辑的Meta',
    path: '/meta/get',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  addMeta: {
    name: '添加新版本的Meta, 或者更新已有的Meta',
    path: '/meta/save',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  allMeta: {
    name: '获取所有有效的Meta',
    path: '/meta/getAll',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  addETL: {
    name: '添加新版本的ETL',
    path: '/etl/save',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  allETL: {
    name: '获取所有有效的ETL',
    path: '/etl/getAll',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  editETL: {
    name: '获取需要编辑的ETL',
    path: '/etl/getETL',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  bloodDAG: {
    name: '血统DAG',
    path: '/etl/getMermaidById',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  bloodDAGByName: {
    name: '血统DAG',
    path: '/etl/getMermaid',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  execETLScript: {
    name: '生成ETL脚本文件到临时目录',
    path: '/etl/execETLScript',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  

  searchCol: {
    name: '根据col名称搜相关col信息',
    path: '/hivemeta/search',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },getTableInfo: {
    name: '获取col所在table的信息',
    path: '/hivemeta/tblinfo',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },


  executionList: {
    name: '某个ETL的执行记录',
    path: '/jobs/execList',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  getExecution: {
    name: '获取正在执行的信息',
    path: '/jobs/getExec',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  }
};
