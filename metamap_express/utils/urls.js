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
  editETL: {
    name: 'test etl edit route',
    path: '/etl/getETL',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  },
  bloodDAG: {
    name: 'bloodDAG',
    path: '/etl/getMermaidById',
    mock_data: mockPath + '/part_time/chart.json',
    ifMock: false
  }
};
