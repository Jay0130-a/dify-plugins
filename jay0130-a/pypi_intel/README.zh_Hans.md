# PyPI 依赖情报（中文说明）

无需任何 API Key 即可查询 Python 包情报：在 Agent 添加、锁定或升级依赖之前，先确认版本、维护活跃度与已知漏洞。

## 工具一览

| 工具 | 作用 |
|---|---|
| `pypi_package_info` | 最新版本、简介、许可证、requires-python、主页、是否被撤回、发布次数、上传时间、声明的依赖 |
| `pypi_release_history` | 近期发布记录与上传时间（最新在前），可选包含预发布 |
| `pypi_downloads` | 近一日 / 近一周 / 近一月下载量（来自 pypistats.org） |
| `pypi_vulnerabilities` | 在 OSV 中查询指定版本（或最新版本）的已知漏洞，含严重程度与修复版本 |

## 配置

无需任何配置。插件只访问三个公开接口：

- `pypi.org` —— 官方 PyPI JSON API（元数据与发布记录）
- `pypistats.org` —— 公开下载统计
- `api.osv.dev` —— 开源漏洞数据库（只读查询）

全部为查询操作：不发布、不修改、不安装、不做依赖解析，也不存储任何数据。

## 使用示例

> 「我要在项目里加 requests，先确认下最新版本和有没有已知漏洞。」

Agent 会调用 `pypi_package_info(package="requests")` 与 `pypi_vulnerabilities(package="requests")`，然后汇总版本、许可证与漏洞修复建议。

> 「pydantic 和 dataclasses-json 选哪个？看下维护活跃度和使用量。」

对两个包分别调用 `pypi_release_history(package=..., limit=5)` 与 `pypi_downloads(package=...)`。
