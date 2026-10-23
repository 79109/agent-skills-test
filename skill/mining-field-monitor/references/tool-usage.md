# 本地工具

运行环境：Python 3.10 或更高版本，仅使用标准库，无需 API 密钥。输出写入工作目录，不写回技能资源目录。

## 给定阈值的事件筛查

这是基础离线筛查工具，支持统一单位下的上限 `gt`（大于）或 `ge`（大于等于）。它不实现动态基线、变化点算法、正式预警系统或自动现场处置。

输入 UTF-8 CSV 含 `point_id,timestamp,value`，可附 `unit`。时间使用带偏移的 ISO 8601；有单位列时所有行必须与 `--unit` 一致。一次运行只处理同一种指标与单位，不将压力和位移混在一起。

```bash
python scripts/detect_events.py examples/monitoring.csv --threshold 10 --operator gt --max-gap-seconds 90 --min-span-seconds 120 --unit mm --rule-id demo-only --output /your-work/events.json
```

以上数值仅用于合成样例，不能当作现场阈值。真实执行需提供阈值和连续性规则的依据。

`--max-gap-seconds` 是允许相邻观测被计入同一采样序列的最大间隔；超过间隔、缺测、冲突重复或非超限观测都会结束当前序列。同点同刻的重复一律作为歧义打断，不静默挑选记录。

输出包含事件起止观测、峰值、采样数、采样跨度、原始记录序号和结束原因。`sampled_span_met` 只表示采样序列跨度达到参数要求；它不证明两个观测之间持续超限。`point_exceedance_only` 表示观测点超限但跨度不足。

缺测点以 `unavailable` 呈现。缺口与重复出现在独立的质量问题列表。无效时间会使本次运行失败，避免不知道它位于何处却将序列连起来。错误需先解决或明确隔离，再重新分析。
