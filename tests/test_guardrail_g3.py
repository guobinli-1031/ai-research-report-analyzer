"""G3 外部引用检测专项测试"""
import pytest
from src.guardrail import run_all, check_g3


class TestG3ExternalReference:
    """G3: 外部引用检测与移除"""

    def test_g3_wind_reference(self):
        """G3应移除Wind数据引用，保留正文数据"""
        text = "根据Wind数据，2025年行业营收增速为8.3%。公司营收增速12.3%，优于行业。"
        cleaned, violations = check_g3(text)
        assert "Wind" not in cleaned, f"Wind未被移除: {cleaned}"
        assert "8.3%" in cleaned, "应保留8.3%数据"
        assert "12.3%" in cleaned, "应保留12.3%数据"
        assert len(violations) >= 1

    def test_g3_tonghuashun_reference(self):
        """G3应移除同花顺引用"""
        text = "同花顺iFinD数据显示，该股近5日主力净流入1.2亿元。"
        cleaned, violations = check_g3(text)
        assert "同花顺" not in cleaned, f"同花顺未被移除: {cleaned}"
        assert "1.2亿" in cleaned, "应保留1.2亿数据"
        assert len(violations) >= 1

    def test_g3_eastmoney_reference(self):
        """G3应移除东方财富引用"""
        text = "东方财富Choice数据显示，北向资金今日净买入3.5亿。"
        cleaned, violations = check_g3(text)
        assert "东方财富" not in cleaned, f"东方财富未被移除: {cleaned}"
        assert "3.5亿" in cleaned, "应保留3.5亿数据"
        assert len(violations) >= 1

    def test_g3_no_external_ref(self):
        """正常文本不应触发G3"""
        text = "公司2025年实现营收457.87亿元，同比增长12.3%。"
        cleaned, violations = check_g3(text)
        assert text == cleaned, "无外部引用时文本不应被修改"
        assert len(violations) == 0, "不应有任何违规记录"

    def test_g3_run_all_integration(self):
        """G3在run_all中应正确串联执行，数据若由其他分句提供应保留"""
        text = "根据Wind数据，2025年行业营收增速为8.3%。公司营收增速12.3%，优于行业。"
        result = run_all(text)
        assert "Wind" not in result["cleaned_text"]
        assert "12.3%" in result["cleaned_text"]  # 第二句无外部引用，数据保留
        # 验证违规记录中包含G3
        g3_violations = [v for v in result["violations"] if v.startswith("G3-")]
        assert len(g3_violations) >= 1
