# 本地工具

运行环境：Python 3.10 或更高版本，仅使用标准库，无需 API 密钥。输出写入工作目录，不写回技能资源目录。

## 可编辑 SVG 关系示意

适合节点和连线式的巷道关系或测点布置概念图，不负责坐标投影、地质剖面、精确尺寸或 CAD 施工图。

```bash
python scripts/render_network.py examples/network.json --output /your-work/network.svg
```

JSON 包含 `title,width,height,nodes,edges`。节点提供唯一 `id`、`label` 和图面坐标 `x,y`，可用 `width,height` 调整框大小；连线提供 `from,to`，可选 `label` 与布尔型 `directed`。图面坐标以像素布局，坐标原点在左上角，不是现场工程坐标。箭头只在 `directed=true` 时出现，其含义由提供的资料决定。

生成的 SVG 含独立文本、节点和连线，可继续编辑；脚本自动加“非比例示意”声明。节点越出画布或引用不存在的端点会报错。长标签需要扩大节点或简化文字，脚本不自动排版避让。

使用浏览器或绘图工具渲染后检查遮挡、连线与文字。仅生成 XML 不代表图面检查通过。标签通过 XML 序列化转义，不作为 SVG 代码执行。

样例为虚构连接关系，仅展示输入格式；不能解释为真实巷道或风流网络。
