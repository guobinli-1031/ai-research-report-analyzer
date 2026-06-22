"""合规规则引擎：6条Guardrail规则的独立检查和串联执行。"""

import json
import re
from typing import Any


# ── G1: 投资建议检查 ──
G1_PATTERNS = {
    "建议买入": "研报评级为买入",
    "建议卖出": "研报评级为卖出",
    "推荐买入": "研报评级为买入",
    "推荐卖出": "研报评级为卖出",
    "强烈推荐": "研报给予推荐评级",
    "建议持有": "研报评级为持有",
    "建议加仓": "研报评级为增持",
    "建议减仓": "研报评级为减持",
    "值得投资": "研报认为具有投资价值",
    "应该买入": "研报评级为买入",
    "应该卖出": "研报评级为卖出",
}


def check_g1(text: str) -> tuple[str, list[str]]:
    """G1: 投资建议关键词替换。

    Returns:
        (替换后的文本, 违规项列表)
    """
    violations = []
    result = text
    for keyword, replacement in G1_PATTERNS.items():
        if keyword in result:
            violations.append(f"G1-投资建议: 检测到「{keyword}」→ 替换为「{replacement}」")
            result = result.replace(keyword, replacement)
    return result, violations


# ── G2: 编造数据检查 ──
def check_g2(data: Any) -> tuple[Any, list[str]]:
    """G2: 检查JSON中各字段是否为空，空值替换为「未披露」。

    Args:
        data: 可以是JSON字符串、dict或list

    Returns:
        (处理后的数据, 违规列表)
    """
    violations = []

    def _fill_empty(obj):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if v is None or v == "" or v == []:
                    violations.append(f"G2-编造数据: 字段「{k}」为空 → 替换为「未披露」")
                    result[k] = "未披露"
                else:
                    result[k] = _fill_empty(v)
            return result
        elif isinstance(obj, list):
            return [_fill_empty(item) for item in obj]
        else:
            return obj

    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            cleaned = _fill_empty(parsed)
            return json.dumps(cleaned, ensure_ascii=False, indent=2), violations
        except json.JSONDecodeError:
            return data, violations
    else:
        return _fill_empty(data), violations


# ── G3: 外部引用检查 ──
G3_PATTERNS = [
    r"Wind数据[^，。；.\n]*[，。；.\n]",
    r"同花顺[^，。；.\n]*[，。；.\n]",
    r"东方财富[^，。；.\n]*[，。；.\n]",
    r"Choice[^，。；.\n]*[，。；.\n]",
    r"Bloomberg[^，。；.\n]*[，。；.\n]",
    r"据[^，。；.\n]*统计[^，。；.\n]*[，。；.\n]",
    r"根据[^，。；.\n]*数据[^，。；.\n]*[，。；.\n]",
]


def check_g3(text: str) -> tuple[str, list[str]]:
    """G3: 外部引用检查，移除含外部数据源的句子。

    Returns:
        (处理后的文本, 违规列表)
    """
    violations = []
    result = text
    for pattern in G3_PATTERNS:
        matches = re.findall(pattern, result)
        for match in matches:
            violations.append(f"G3-外部引用: 检测到「{match.strip()}」→ 已移除")
            result = result.replace(match, "[已移除外部引用] ")
    return result, violations


# ── G4: 来源标注检查 ──
G4_PATTERN = re.compile(r"\(p\.\d+\)")


def check_g4(text: str) -> tuple[str, list[str]]:
    """G4: 检查关键数据是否有来源标注。

    Returns:
        (原始文本, 违规列表) — 不修改文本，仅记录违规
    """
    violations = []

    # 检查含数字的句子（可能是关键数据）
    data_sentences = re.findall(r"[^。；\n]*\d+[^。；\n]*[。；\n]?", text)
    for sentence in data_sentences:
        # 跳过已有来源标注的句子
        if G4_PATTERN.search(sentence):
            continue
        # 跳过非数据性数字（如年份、百分比等描述性内容）
        if re.search(r"p\.\d+|Page \d+|第[一二三四五六七八九十\d]+页", sentence):
            continue
        # 含实质性数字但无来源标注
        if re.search(r"\d+\.?\d*[万亿千百]?[元美元％%倍年]", sentence):
            violations.append(f"G4-来源标注: 关键数据未标注来源 → 「{sentence.strip()[:60]}...」")

    return text, violations


# ── G5: AI推断标注检查 ──
def check_g5(data: Any) -> tuple[Any, list[str]]:
    """G5: 检查ai_supplement部分每项是否有[AI推断]标注。

    Args:
        data: 可以是JSON字符串或dict

    Returns:
        (原始数据, 违规列表)
    """
    violations = []
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return data, violations

    ai_supplement = data.get("ai_supplement", []) if isinstance(data, dict) else []
    for i, item in enumerate(ai_supplement):
        if isinstance(item, dict):
            risk_text = item.get("risk", "")
            if not str(risk_text).startswith("[AI推断]"):
                violations.append(f"G5-AI推断: 第{i+1}项缺少[AI推断]标注")

    return data, violations


# ── G6: 免责声明检查 ──
DISCLAIMER = """\n\n---\n本报告由AI自动生成，仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。AI分析结果可能存在偏差或遗漏，请以原始研报及官方披露信息为准。"""


def check_g6(text: str) -> tuple[str, list[str]]:
    """G6: 检查末尾是否有免责声明，缺失则追加。

    Returns:
        (处理后的文本, 违规列表)
    """
    violations = []
    if "本报告由AI自动生成" not in text:
        violations.append("G6-免责声明: 缺失免责声明 → 已自动追加")
        text = text + DISCLAIMER
    return text, violations


# ── 串联执行 ──
def run_all(text: str) -> dict:
    """串联执行G1→G6全部规则。

    Args:
        text: 原始报告文本

    Returns:
        {"cleaned_text": str, "violations": list[str]}
    """
    all_violations = []
    current = text

    # G1: 投资建议
    current, v = check_g1(current)
    all_violations.extend(v)

    # G2: 编造数据（对JSON部分）
    current, v = check_g2(current)
    all_violations.extend(v)

    # G3: 外部引用
    current, v = check_g3(current)
    all_violations.extend(v)

    # G4: 来源标注
    _, v = check_g4(current)
    all_violations.extend(v)

    # G5: AI推断标注
    _, v = check_g5(current)
    all_violations.extend(v)

    # G6: 免责声明
    current, v = check_g6(current)
    all_violations.extend(v)

    return {
        "cleaned_text": current,
        "violations": all_violations,
    }
