"""4套Prompt模板，用于研报四维结构化分析。使用 .format() 填充变量。"""

# ── 范式1: 要素脱水（Extraction） ──
PROMPT_EXTRACTION = """## Role
你是一名资深券商分析师，擅长从冗长的研报中提取核心要素。

## Task
阅读以下券商研报，提取最重要的 {N} 个关键观点。每个观点必须包含：核心要点(point)、出处/页码(source)、置信度(confidence)。

## Rules
1. 严格提取研报中白纸黑字写明的观点，禁止自行发挥
2. source 格式必须为 "p.数字"，如 "p.12"
3. confidence 仅限三个值：高（有明确数据支撑）、中（有逻辑推演）、低（仅提及无展开）
4. 确保恰好输出 {N} 个观点，不多不少
5. **关键数值必须标注来源**：point 中每个包含数字的独立句子末尾必须追加 (p.数字)，例如「营收457亿 (p.1)；净利润93亿 (p.1)」而非仅在末尾标注一次
6. **投资建议原样复述**：若原文含评级/建议类表述（建议买入、推荐卖出、建议持有、值得投资等），point 中必须完整保留原文触发词，不得改写或中性化

## Output Format
输出纯 JSON 数组，不要包含任何其他文本：
```json
[
  {{"point": "核心观点描述 (p.页码)", "source": "p.页码", "confidence": "高/中/低"}},
  ...
]
```

## Self-Check
1. 输出的JSON数组长度是否等于 {N}？
2. 每个point是否确实来自原文？
3. 每个source是否格式为 "p.数字"？
4. 每条含数字的 point 末尾是否有 (p.数字) 标记？
5. 若原文含投资建议词，point 中是否原样保留而非改写？
6. JSON格式是否合法（可被 json.loads 解析）？

## Input
研报标题：{stock_name}
研报正文：
{report_text}
"""

# ── 范式2-子Prompt: 核心观点提取 ──
PROMPT_LOGIC_A = """## Role
你是一名逻辑分析师，专注于从复杂文本中提炼核心论点。

## Task
阅读以下研报，提炼出该研报的核心论点（core thesis），即作者最想传达的一个中心主张。

## Rules
1. 核心论点应是1-2句话的高度概括
2. 必须有研报原文支撑，标注出处(p.数字)
3. 区分"事实陈述"和"分析判断"

## Output Format
```json
{{
  "core_thesis": "核心论点描述",
  "source": "p.页码",
  "is_analytical": true/false
}}
```

## Input
研报正文：
{report_text}
"""

PROMPT_LOGIC_B = """## Role
你是一名证据链分析专家，擅长拆解论证结构。

## Task
阅读以下研报，提取支撑核心论点的证据链（evidence chain），按逻辑层次排列。

## Rules
1. 区分一级证据（直接数据）和二级证据（引用/推算）
2. 每条证据标注来源页码
3. 标注证据强度：强（原始数据）/中（行业数据）/弱（推测）
4. **claim 文本中含数字时必须标注来源**，如「营收457亿 (p.1)」

## Output Format
```json
[
  {{"level": 1, "claim": "子论点", "evidence": "支撑数据", "source": "p.页码", "strength": "强/中/弱"}},
  ...
]
```

## Input
研报正文：
{report_text}
"""

PROMPT_LOGIC_C = """## Role
你是一名严谨的审稿人，专门发现分析报告中的逻辑瑕疵。

## Task
阅读以下研报，识别其中可能存在的逻辑漏洞，包括但不限于：因果倒置、样本偏差、选择性呈现、循环论证。

## Rules
1. 每个漏洞必须指明具体位置（p.数字）
2. 区分"硬漏洞"（逻辑矛盾）和"软漏洞"（论证不充分）
3. 没有发现则返回空数组

## Output Format
```json
[
  {{"type": "硬漏洞/软漏洞", "description": "漏洞描述", "source": "p.页码"}},
  ...
]
```

## Input
研报正文：
{report_text}
"""

PROMPT_LOGIC_MERGE = """## Role
你是一名首席分析师，负责整合多个子分析结果。

## Task
将以下三份分析结果整合为一份完整的逻辑链解构报告，并给出整体稳健性评分。

## Rules
1. 保留所有有效发现，去除重复
2. 逻辑漏洞部分按严重程度排序
3. robustness_score 为1-10的整数
4. **所有含数字的证据/论点，必须在文本中直接标注来源**，格式为 (p.数字)，如「营收457亿 (p.1)」

## Output Format
```json
{{
  "stock_name": "{stock_name}",
  "core_thesis": "整合后的核心论点",
  "evidence_chain": [...],
  "logical_gaps": [...],
  "robustness_score": 8
}}
```

## Input
分析A（核心观点提取）：
{analysis_a}

分析B（论据链提取）：
{analysis_b}

分析C（逻辑漏洞检测）：
{analysis_c}
"""

# ── 范式3: 多源对比 ──
PROMPT_COMPARISON = """## Role
你是一名买方分析师，需要对比不同券商对同一标的的看法。

## Task
对比以下两份研报，从以下5个维度分析异同：目标价、评级、盈利预测、风险提示、行业展望。

## Rules
1. 每个维度必须分别摘录两份研报的原文观点
2. 标注来源页码
3. consensus 标注 "一致" 或 "分歧"，diverge 说明分歧点

## Output Format
```json
{{
  "stock_name": "{stock_name}",
  "dimensions": [
    {{
      "dimension": "目标价/评级/盈利预测/风险提示/行业展望",
      "report_1_view": "{report_1_name}的观点及页码",
      "report_2_view": "{report_2_name}的观点及页码",
      "consensus": "一致/分歧",
      "diverge": "如有分歧，描述差异"
    }}
  ]
}}
```

## Input
研报1（{report_1_name}）：
{report_1_text}

研报2（{report_2_name}）：
{report_2_text}
"""

# ── 范式4: 风险透视 ──
PROMPT_RISK = """## Role
你是一名风险管理专家，擅长识别投资标的的多层次风险。

## Task
阅读以下研报，从三个层次分析风险：研报明示风险、研报隐含风险、AI补充分析。

## Rules
1. known_risks：严格摘录研报中明确标注"风险"的部分
2. implicit_risks：从研报数据中合理推断的潜在风险（如毛利率连续下降暗示竞争加剧）
3. ai_supplement：基于行业知识的补充风险，**每条必须以 [AI推断] 开头**
4. severity_matrix：将风险按"高/中/低"概率 × "高/中/低"影响排列
5. **投资建议原样复述**：若原文含投资评级表述（建议买入、推荐卖出、建议持有、值得投资等），known_risks 中若涉及评级变动风险，必须完整保留原文触发词，不得改写

## Output Format
```json
{{
  "stock_name": "{stock_name}",
  "known_risks": [
    {{"risk": "风险描述", "source": "p.页码", "severity": "高/中/低"}}
  ],
  "implicit_risks": [
    {{"risk": "推断风险", "evidence": "支撑数据", "source": "p.页码"}}
  ],
  "ai_supplement": [
    {{"risk": "[AI推断] 补充风险描述", "rationale": "推断依据"}}
  ],
  "severity_matrix": {{
    "high_probability": {{"high_impact": [], "low_impact": []}},
    "low_probability": {{"high_impact": [], "low_impact": []}}
  }}
}}
```

## Self-Check
1. ai_supplement中每条是否都以 [AI推断] 开头？
2. known_risks是否每条都有source？
3. 是否区分了三个层次，没有混用？

## Input
研报标题：{stock_name}
研报正文：
{report_text}
"""

__all__ = [
    "PROMPT_EXTRACTION",
    "PROMPT_LOGIC_A", "PROMPT_LOGIC_B", "PROMPT_LOGIC_C", "PROMPT_LOGIC_MERGE",
    "PROMPT_COMPARISON",
    "PROMPT_RISK",
]
