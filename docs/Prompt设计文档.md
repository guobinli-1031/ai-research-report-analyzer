# Prompt设计文档

## 设计原则

每套Prompt遵循统一的六段式结构：
1. **Role** — 角色定义，设定专业背景
2. **Task** — 任务描述，明确输出目标
3. **Rules** — 约束规则，边界条件
4. **Output Format** — 输出格式，JSON Schema
5. **Self-Check** — 自检清单（范式1/4独有）
6. **Input** — 输入数据，变量占位符

## 范式1 Prompt（要素脱水）

**Role**: 资深券商分析师，擅长从研报提取核心要素
**Task**: 提取最重要的{N}个关键观点，含point/source/confidence
**Rules**: 严格提取原文，source格式p.数字，confidence三档（高/中/低），恰好{N}个
**Output Format**: JSON数组，元素含point/source/confidence
**Self-Check**: N值检查、JSON格式检查、source格式检查
**Input**: {report_text}, {stock_name}, {N}

## 范式2 Prompt（逻辑链解构）

Multi-Agent模式，4个子Prompt：

### 子Prompt A — 核心观点提取
**Role**: 逻辑分析师
**Task**: 提炼核心论点，1-2句话
**Output**: JSON含core_thesis/source/is_analytical

### 子Prompt B — 论据链提取
**Role**: 证据链分析专家
**Task**: 提取支撑论点的证据链，按逻辑层次排列
**Output**: JSON数组，每条含level/claim/evidence/source/strength

### 子Prompt C — 逻辑漏洞检测
**Role**: 审稿人
**Task**: 识别因果倒置/样本偏差/选择性呈现/循环论证
**Output**: JSON数组，每条含type/description/source

### 合并Prompt
**Role**: 首席分析师
**Task**: 整合三份分析，给出robustness_score(1-10)
**Output**: JSON含core_thesis/evidence_chain/logical_gaps/robustness_score

## 范式3 Prompt（多源对比）

**Role**: 买方分析师
**Task**: 5维度对比（目标价/评级/盈利预测/风险提示/行业展望）
**Output**: JSON含dimensions数组，每项含report_1_view/report_2_view/consensus/diverge

## 范式4 Prompt（风险透视）

**Role**: 风险管理专家
**Task**: 三层风险分析（明示/隐含/AI补充）
**Output**: JSON含known_risks/implicit_risks/ai_supplement/severity_matrix
**Self-Check**: [AI推断]标注检查、source完整性检查、层次区分检查
