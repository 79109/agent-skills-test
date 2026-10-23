# Agent Skills Test

**测试项目 / TEST PROJECT — 本仓库中的技能、脚本、模板、样例和压缩包均为测试文件。**

本项目用于测试 11 项矿业科研、教学与现场资料分析技能的目录结构、安装识别、调用流程和基础脚本功能。目前处于原型验证阶段，尚未完成真实业务环境中的端到端验证，不作为正式生产版本发布。

## 内容

- [`skill/`](skill/)：11 个独立技能文件夹，保留可安装的目录结构。
- [`skill-full.zip`](skill-full.zip)：上述技能文件的完整测试合集。
- 每项技能包含带 YAML 元信息的 `SKILL.md`、`agents/openai.yaml`、方法说明和可选模板。
- 其中 6 项技能包含 Python 脚本；脚本使用 Python 3.10+ 标准库。
- `examples/` 下的数据是合成测试样例，不是现场实测数据或推荐工程参数。

## 技能目录

| Skill | 测试方向 |
| --- | --- |
| [mining-experiment-protocol](skill/mining-experiment-protocol/) | 实验方案与试验布局 |
| [mining-simulation-analysis](skill/mining-simulation-analysis/) | 数值模拟方案与工况比较 |
| [mining-data-preparation](skill/mining-data-preparation/) | 数据质量检查与整理 |
| [mining-result-interpretation](skill/mining-result-interpretation/) | 结果解释与讨论 |
| [mining-diagram-assistant](skill/mining-diagram-assistant/) | 工程示意图整理 |
| [textbook-reader](skill/textbook-reader/) | 教材阅读与知识梳理 |
| [monograph-reader](skill/monograph-reader/) | 专著论证与研究脉络梳理 |
| [course-designer](skill/course-designer/) | 课程与教学活动设计 |
| [mining-field-record](skill/mining-field-record/) | 现场记录与证据文件整理 |
| [mining-field-monitor](skill/mining-field-monitor/) | 监测数据筛查与异常事件整理 |
| [mining-field-diagnosis](skill/mining-field-diagnosis/) | 现场问题诊断与复核建议 |

## 测试状态

已完成 11 项技能的 YAML 和本地资源链接检查，以及配套脚本的 14 项测试。以上结果仅覆盖当前测试输入和检查范围，不代表所有实际任务均已验证。

技能文件需要安装到支持 Agent Skills 的运行环境后使用。上传到 GitHub 或下载 ZIP 本身不会自动完成安装；脚本执行还需要对应环境提供 Python 和文件访问能力。

本仓库不连接现场设备，也不提供持续在线监测服务。分析输出用于测试和人工复核，不能直接替代现场操作规程、正式报警系统或专业工程审核。

---

**Test project and test files only.** This repository contains prototype skills, scripts, templates, and synthetic examples for evaluation. It has not been validated for production deployment.
