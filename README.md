# Agent Skills Test

这是一个测试项目，仓库中的文件仅用于测试。

## 内容

- [`skill/`](skill/)：11 个独立技能文件夹，保留可安装的目录结构。
- [`skill-full.zip`](skill-full.zip)：上述技能文件的完整测试合集。
- 每项技能包含带 YAML 元信息的 `SKILL.md`、`agents/openai.yaml`、方法说明和可选模板。
- 其中 6 项技能包含 Python 脚本；脚本使用 Python 3.10+ 标准库。
- `examples/` 下的数据是合成测试样例。

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
