"""Guardrail规则单元测试 — 8个用例（GT1-GT8）。"""

import json
import pytest
from src.guardrail import (
    check_g1, check_g2, check_g3, check_g4, check_g5, check_g6, run_all,
)


class TestG1InvestmentAdvice:
    """GT1: 投资建议关键词替换"""

    def test_replace_advice_buy(self):
        text = "我们建议买入该股票"
        result, violations = check_g1(text)
        assert "建议买入" not in result
        assert "研报评级为买入" in result
        assert len(violations) == 1

    def test_multiple_keywords(self):
        text = "强烈推荐该标的，建议加仓至重仓"
        result, violations = check_g1(text)
        assert "强烈推荐" not in result
        assert "建议加仓" not in result
        assert len(violations) == 2


class TestG2FabricatedData:
    """GT2-GT3: 编造数据检查"""

    def test_replace_null(self):
        data = '{"revenue": null, "profit": "", "name": "ABC"}'
        result, violations = check_g2(data)
        parsed = json.loads(result) if isinstance(result, str) else result
        assert parsed["revenue"] == "未披露"
        assert parsed["profit"] == "未披露"
        assert parsed["name"] == "ABC"

    def test_replace_empty_string(self):
        data = '{"eps": "", "pe": 15}'
        result, violations = check_g2(data)
        parsed = json.loads(result) if isinstance(result, str) else result
        assert parsed["eps"] == "未披露"


class TestG3ExternalReference:
    """GT4: 外部引用检查"""

    def test_remove_wind_reference(self):
        text = "根据Wind数据，该公司营收增长15%。行业前景良好。"
        result, violations = check_g3(text)
        assert "Wind数据" not in result
        assert "[已移除外部引用]" in result
        assert "行业前景良好" in result
        assert len(violations) >= 1

    def test_remove_bloomberg_reference(self):
        text = "Bloomberg终端显示该股估值偏低。"
        result, violations = check_g3(text)
        assert "Bloomberg" not in result
        assert "[已移除外部引用]" in result


class TestG4SourceAnnotation:
    """GT5: 来源标注检查"""

    def test_detect_missing_source(self):
        text = "营收同比增长25.3%。净利润提升至38.5%。"
        _, violations = check_g4(text)
        # 两处含数字的句子都没有(p.X)标注
        assert len(violations) >= 1


class TestG5AISupplement:
    """GT6-GT7: AI推断标注检查"""

    def test_missing_ai_tag(self):
        data = {
            "stock_name": "ABC",
            "ai_supplement": [
                {"risk": "行业政策风险", "rationale": "近期政策收紧"},
            ]
        }
        _, violations = check_g5(data)
        assert len(violations) == 1
        assert "缺少[AI推断]" in violations[0]

    def test_correct_ai_tag(self):
        data = {
            "stock_name": "ABC",
            "ai_supplement": [
                {"risk": "[AI推断] 宏观环境可能影响出口业务", "rationale": "贸易摩擦加剧"},
            ]
        }
        _, violations = check_g5(data)
        assert len(violations) == 0


class TestG6Disclaimer:
    """GT8: 免责声明检查"""

    def test_missing_disclaimer(self):
        text = "这是一份完整的分析报告。以上分析仅供参考。"
        result, violations = check_g6(text)
        assert "本报告由AI自动生成" in result
        assert len(violations) == 1

    def test_existing_disclaimer(self):
        text = "报告正文\n\n本报告由AI自动生成，仅供参考。"
        result, violations = check_g6(text)
        assert len(violations) == 0


class TestRunAll:
    """集成测试：验证run_all串联执行"""

    def test_run_all_basic(self):
        text = "建议买入该股，根据Wind数据，营收增长20%。"
        result = run_all(text)
        assert "建议买入" not in result["cleaned_text"]
        assert "[已移除外部引用]" in result["cleaned_text"]
        assert "本报告由AI自动生成" in result["cleaned_text"]
        assert len(result["violations"]) >= 3  # G1+G3+G6
