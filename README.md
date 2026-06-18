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

## Quick Start

```bash
# 1. 克隆仓库
git clone https://github.com/guobinli-1031/ai-research-report-analyzer.git
cd ai-research-report-analyzer

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API Key
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key

# 4. 运行分析
python -m src.analyzer report.pdf --mode extraction -o output.md
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

## Example Output

### 范式1：要素脱水 (Extraction)

以福耀玻璃研报为样本，提取关键观点：

```json
{
  "viewpoints": [
    {
      "claim": "福耀玻璃全球市占率35%，国内68%",
      "confidence": "高",
      "source": "p.3",
      "rating": "研报评级为增持（中信证券）"
    },
    {
      "claim": "2025年营收457.87亿（+12.3%），净利润93.12亿（+8.7%）",
      "confidence": "高",
      "source": "p.1"
    },
    {
      "claim": "ASP从144元提升至152元（+5.6%），产品结构持续升级",
      "confidence": "高",
      "source": "p.2"
    },
    {
      "claim": "北美市占率有望从18%提升至25%，受益竞争对手退出",
      "confidence": "中",
      "source": "p.4"
    },
    {
      "claim": "高附加值产品占比升至49%，带动毛利率环比改善0.8pct",
      "confidence": "高",
      "source": "p.3"
    }
  ]
}
```

### 范式4：风险透视 (Risk Lens)

| 层次 | 风险 | 严重度 | 来源 |
|------|------|--------|------|
| 已知 | 继任风险：曹德旺辞职，曹辉接任 | 中 | p.5 |
| 已知 | 原材料成本压力（PVB膜、浮法玻璃）| 高 | p.5 |
| 隐含 | Q1净利润-15.68% vs 营收+5.08%，成本端承压 | 高 | p.1 |
| AI补充 | [AI推断] 中美贸易摩擦升级可能导致关税成本增加 | 中 | — |
| AI补充 | [AI推断] 新能源车增速放缓影响汽车玻璃需求 | 低 | — |

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
