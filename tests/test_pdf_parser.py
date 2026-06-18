"""PDF解析模块单元测试。"""

import os
import tempfile
import pytest
from src.pdf_parser import parse_pdf


class TestPdfParser:
    """PDF解析功能测试"""

    def test_file_not_exists(self):
        result = parse_pdf("/tmp/nonexistent_file_12345.pdf")
        assert result.startswith("[Error]")
        assert "不存在" in result

    def test_non_pdf_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello world")
            tmp_path = f.name
        try:
            result = parse_pdf(tmp_path)
            assert result.startswith("[Error]")
            assert "非PDF" in result or "不是有效" in result
        finally:
            os.unlink(tmp_path)

    def test_directory_not_file(self):
        result = parse_pdf("/tmp")
        assert result.startswith("[Error]")
        assert "不是文件" in result

    def test_empty_pdf(self):
        """测试空白PDF（仅含元数据，无文本内容）。"""
        import fitz
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp_path = f.name
        doc = fitz.open()
        doc.new_page()
        doc.save(tmp_path)
        doc.close()
        try:
            result = parse_pdf(tmp_path)
            # 空白PDF无文本：应在错误提示或空文本之间
            assert "未能提取" in result or result.strip() == ""
        finally:
            os.unlink(tmp_path)

    def test_pdf_with_text(self):
        """测试含英文文本的PDF。"""
        import fitz
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp_path = f.name
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), "Hello World Report Analysis", fontsize=14)
        doc.save(tmp_path)
        doc.close()
        try:
            result = parse_pdf(tmp_path)
            assert not result.startswith("[Error]")
            assert "[Page 1]" in result
            assert "Hello World" in result
        finally:
            os.unlink(tmp_path)
