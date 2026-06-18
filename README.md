# AI研报解读助手 (Research Report Analyzer)

基于 DeepSeek 大语言模型的券商研报四维结构化分析工具。输入 PDF 研报，输出包含要素脱水、逻辑链解构、多源对比、风险透视的完整 Markdown 报告。

## 架构

```
PDF → [pdf_parser.py] → 文本
  → [prompts.py] 4套Prompt模板
    → 范式1: 要素脱水 (单次LLM)
    → 范式2: 逻辑链解构 (Multi-Agent)
    → 范式3: 多源对比 (双PDF)
    → 范式4: 风险透视 (三层分析)
  → [guardrail.py] 6条合规规则
  → Markdown 报告
```

## 安装

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

## 使用

```bash
# 全模式分析
python -m src.analyzer report.pdf

# 指定模式
python -m src.analyzer report.pdf --mode extraction
python -m src.analyzer report.pdf --mode logic
python -m src.analyzer report.pdf --mode risk

# 多源对比（需两份PDF）
python -m src.analyzer report1.pdf --mode comparison --pdf2 report2.pdf

# 输出到文件
python -m src.analyzer report.pdf -o output.md
```

## 四种分析范式

| 范式 | 名称 | 模式 | 说明 |
|------|------|------|------|
| 1 | 要素脱水 | extraction | 提取N个关键观点，标注出处和置信度 |
| 2 | 逻辑链解构 | logic | Multi-Agent：论点→证据链→漏洞→整合 |
| 3 | 多源对比 | comparison | 5维度对比两份研报的异同 |
| 4 | 风险透视 | risk | 明示风险/隐含风险/AI补充风险三层分析 |

## Guardrail 合规规则

| 规则 | 名称 | 功能 |
|------|------|------|
| G1 | 投资建议检查 | 替换直接建议措辞 |
| G2 | 编造数据检查 | 空值填充"未披露" |
| G3 | 外部引用检查 | 移除Wind/同花顺等外部数据源引用 |
| G4 | 来源标注检查 | 数据未标(p.X)时记录违规 |
| G5 | AI推断标注 | 强制[AI推断]前缀 |
| G6 | 免责声明 | 缺失时自动追加 |

## 技术栈

- Python 3.10+
- PyMuPDF (PDF解析)
- DeepSeek API (兼容OpenAI SDK)
- pytest (测试)

## 测试

```bash
pytest tests/ -v
```

## License

MIT
