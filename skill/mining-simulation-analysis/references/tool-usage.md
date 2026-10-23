# 本地工具

运行环境：Python 3.10 或更高版本，仅使用标准库，无需 API 密钥。输出写入工作目录，不写回技能资源目录。

## 单因素工况对比

输入 UTF-8 CSV，包含唯一 `case_id`、`status`，以及所选参数和响应列。只有 `status=completed` 参与数值比较；其它状态会被保留为未完成。此状态由提供者给出，脚本不会验证求解日志。

```bash
python scripts/compare_cases.py examples/cases.csv --baseline base --parameters stiffness lateral_ratio --metrics displacement --output /your-work/comparison.json
```

在计算前确认几何、边界、计算阶段、单位和响应定义可比，并列出所有可能变化的参数。脚本无法发现未输入的工况差异。

输出绝对差；恰好一个参数改变时还输出 `local_slopes=响应差/参数差` 和基准归一化弹性 `local_slopes×基准参数/基准响应`。基准参数或响应为零时弹性为 `null`。多参数变化只报告联合差异，不计算单因素归因或重要性排名。非数值或非有限值单独标记。

浮点比较按输入值直接进行。应先处理仅由显示精度造成的差异；不要为了得到单因素结论忽略真实变化。结果是有限差分，不是全局灵敏度，也不提供网格独立性或现场验证。

样例结果为合成数据；不得作为真实模拟结果引用。脚本不调用任何求解器。
