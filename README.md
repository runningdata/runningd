# RunningD ETL调度系统

## 项目简介

**RunningD** 是一个基于 Django 框架开发的分布式 ETL（数据抽取、转换、加载）调度系统。系统集成 Celery 实现强大的分布式任务调度、异步执行与定时任务能力，并结合 Redis 实现任务高效通信与状态管理，支持多数据源、多类型任务的灵活调度与监控。

---

## 核心功能

- **分布式任务调度**：支持大规模任务异步分发、并发处理。
- **ETL作业管理**：可自定义 ETL 流程，支持多种数据处理任务的编排和调度。
- **定时任务/周期任务**：内置 Celery Beat，可灵活设置任务周期与调度规则。
- **多队列/多worker支持**：任务根据类型分发到不同队列，实现资源隔离与弹性扩展。
- **任务监控与日志**：实时监控任务状态、执行历史与异常日志。
- **告警系统**：内置任务失败、超时等多维度告警（如邮件、微信等多渠道推送）。
- **权限与认证**：集成 CAS 单点登录，完善的权限控制体系。
- **Web管理界面**：友好的可视化管理与操作界面。

---

## 模块结构与路径说明

| 模块名              | 路径                                      | 说明                                 |
|-------------------|-----------------------------------------|------------------------------------|
| 公共组件           | `metamap_django/will_common`            | 通用工具、基础模型、Redis、Celery工具等      |
| ETL调度主模块       | `metamap_django/metamap`                | 核心ETL调度逻辑、任务管理、调度API           |
| 数据质量管理        | `metamap_django/dqms`                   | 数据质量检测相关任务、规则和调度              |
| 运行监控与告警      | `metamap_django/running_alert`          | 任务监控、异常检测、告警任务与推送             |
| Celery配置         | `metamap_django/*/celery.py`            | 各模块Celery实例初始化                    |
| Celery任务路由&配置 | `metamap_django/*/config/celery_conf.py`| Celery参数、队列、路由等细粒度配置            |
| 脚本与运维工具      | `metamap_django/bin`                     | 各类Celery worker/beat启动、管理脚本         |
| 配置文件            | `metamap_django/*/config/prod.py`        | 各模块运行时配置                          |
| 认证与权限           | `metamap_django/cas`                     | CAS 单点登录与权限控制                   |
| 其他                | `metamap_django/`（根目录）               | Django主配置、管理脚本、静态文件等           |

---

## 技术架构选型

- **后端框架**：Django (Python)
- **任务调度&异步执行**：Celery
- **消息队列/中间件**：Redis
- **定时调度**：Celery Beat + djcelery
- **Web服务**：Django Admin + 自定义前端
- **数据库**：可配置（如 MySQL、PostgreSQL 等，依赖 settings）
- **监控&告警**：自有实现，支持邮件、微信等多渠道推送
- **认证**：CAS 单点登录
- **其他**：kombu、rest_framework、djcelery 等

---

## 快速启动

1. **依赖安装**

   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   
   设置 `METAMAP_HOME`、数据库、Redis等相关环境变量。

3. **初始化数据库**
   
   ```bash
   python manage.py migrate
   ```

4. **启动Celery Worker与Beat**

   ```bash
   sh bin/celery_start.sh start
   sh bin/celery_beat.sh start
   ```

5. **启动Django服务**

   ```bash
   python manage.py runserver
   ```

---

## 典型使用场景

- 多数据源ETL调度与自动化批量处理
- 大数据平台定时任务调度与结果监控
- 数据质量自动检测与告警
- 异常任务的自动重试和告警推送

---

## 贡献

欢迎提交 Issue 或 Pull Request 参与改进。如需企业级定制或技术支持，请联系项目维护者。

---

## 安全提示

请勿在公开仓库或脚本中暴露敏感账号密码等信息（如 `AZKABAN_PWD` 等），如发现请及时修正并更换相关密码！

---

## License

本项目遵循 Apache 2.0 许可证。
