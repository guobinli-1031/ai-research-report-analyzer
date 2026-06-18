"""PDF解析模块，使用PyMuPDF(fitz)提取文本并注入页码标记。"""

import os
import fitz  # PyMuPDF


def parse_pdf(file_path: str) -> str:
    """解析PDF文件，提取文本并在每页前注入页码标记。

    Args:
        file_path: PDF文件的绝对路径

    Returns:
        带页码标记的完整文本字符串，或错误提示字符串
    """
    # 1. 文件存在性检查
    if not os.path.exists(file_path):
        return f"[Error] 文件不存在: {file_path}"

    # 2. 是否为文件
    if not os.path.isfile(file_path):
        return f"[Error] 路径不是文件: {file_path}"

    # 3. PDF格式检查（通过文件头魔数）
    try:
        with open(file_path, "rb") as f:
            header = f.read(5)
        if not header.startswith(b"%PDF"):
            return f"[Error] 非PDF文件或文件已损坏: {file_path}"
    except Exception as e:
        return f"[Error] 无法读取文件: {str(e)}"

    # 4. 打开PDF并提取文本
    try:
        doc = fitz.open(file_path)
    except fitz.FileDataError:
        return f"[Error] 文件不是有效的PDF格式: {file_path}"
    except Exception as e:
        return f"[Error] 打开PDF失败: {str(e)}"

    # 5. 检查是否加密
    if doc.is_encrypted:
        doc.close()
        return f"[Error] PDF已加密，无法提取文本: {file_path}"

    # 6. 逐页提取文本，注入页码标记
    pages_text = []
    has_text = False

    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                has_text = True
            pages_text.append(f"[Page {page_num + 1}]\n{text}")
    except Exception as e:
        doc.close()
        return f"[Error] PDF文本提取失败: {str(e)}"

    doc.close()

    # 7. 检查是否有可提取文本
    if not has_text:
        return "[Error] 未能提取到文本内容，PDF可能为扫描件（纯图片）"

    return "\n\n".join(pages_text)
