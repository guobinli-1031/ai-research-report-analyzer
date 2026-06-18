"""主调度器：CLI入口，串联PDF解析→LLM分析→Guardrail→输出报告。"""

import argparse
import json
import sys

from src.pdf_parser import parse_pdf
from src.llm_client import chat, chat_multi
from src.guardrail import run_all
from src.prompts import (
    PROMPT_EXTRACTION,
    PROMPT_LOGIC_A, PROMPT_LOGIC_B, PROMPT_LOGIC_C, PROMPT_LOGIC_MERGE,
    PROMPT_COMPARISON,
    PROMPT_RISK,
)


def _extract_stock_name(pdf_path: str) -> str:
    """从文件路径提取标的名称。"""
    import os
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    return name


def run_extraction(report_text: str, stock_name: str, n: int = 5) -> str:
    """范式1: 要素脱水。"""
    prompt = PROMPT_EXTRACTION.format(report_text=report_text, stock_name=stock_name, N=n)
    result = chat(prompt)
    guardrail_result = run_all(result)
    header = f"# 研报要素脱水 — {stock_name}\n\n"
    footer = _format_violations(guardrail_result["violations"])
    return header + guardrail_result["cleaned_text"] + footer


def run_logic(report_text: str, stock_name: str) -> str:
    """范式2: 逻辑链解构（Multi-Agent）。"""
    sub_prompts = [
        PROMPT_LOGIC_A.format(report_text=report_text),
        PROMPT_LOGIC_B.format(report_text=report_text),
        PROMPT_LOGIC_C.format(report_text=report_text),
    ]
    results = chat_multi(sub_prompts)
    analysis_a, analysis_b, analysis_c = results

    merge_prompt = PROMPT_LOGIC_MERGE.format(
        stock_name=stock_name,
        analysis_a=analysis_a,
        analysis_b=analysis_b,
        analysis_c=analysis_c,
    )
    merged = chat(merge_prompt)
    guardrail_result = run_all(merged)
    header = f"# 逻辑链解构 — {stock_name}\n\n"
    footer = _format_violations(guardrail_result["violations"])
    return header + guardrail_result["cleaned_text"] + footer


def run_comparison(
    report_1_text: str, report_1_name: str,
    report_2_text: str, report_2_name: str,
    stock_name: str
) -> str:
    """范式3: 多源对比。"""
    prompt = PROMPT_COMPARISON.format(
        stock_name=stock_name,
        report_1_name=report_1_name,
        report_1_text=report_1_text,
        report_2_name=report_2_name,
        report_2_text=report_2_text,
    )
    result = chat(prompt)
    guardrail_result = run_all(result)
    header = f"# 多源对比 — {stock_name}\n\n"
    footer = _format_violations(guardrail_result["violations"])
    return header + guardrail_result["cleaned_text"] + footer


def run_risk(report_text: str, stock_name: str) -> str:
    """范式4: 风险透视。"""
    prompt = PROMPT_RISK.format(report_text=report_text, stock_name=stock_name)
    result = chat(prompt)
    guardrail_result = run_all(result)
    header = f"# 风险透视 — {stock_name}\n\n"
    footer = _format_violations(guardrail_result["violations"])
    return header + guardrail_result["cleaned_text"] + footer


def _format_violations(violations: list[str]) -> str:
    """格式化Guardrail违规记录。"""
    if not violations:
        return ""
    lines = ["\n\n---\n## Guardrail 违规记录\n"]
    for v in violations:
        lines.append(f"- {v}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="AI研报解读助手 (RRA) — 四维结构化分析",
    )
    parser.add_argument("pdf_path", nargs="?", help="PDF文件路径")
    parser.add_argument("--mode", default="all",
                        choices=["all", "extraction", "logic", "comparison", "risk"],
                        help="分析模式（默认 all）")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径（默认 stdout）")
    parser.add_argument("--n", type=int, default=5, help="范式1提取关键点数量（默认 5）")
    parser.add_argument("--pdf2", default=None, help="范式3对比模式需要的第二份PDF路径")
    args = parser.parse_args()

    if not args.pdf_path:
        parser.print_help()
        sys.exit(1)

    # 解析PDF
    sys.stderr.write(f"[RRA] 解析PDF: {args.pdf_path}\n")
    report_text = parse_pdf(args.pdf_path)
    if report_text.startswith("[Error]"):
        sys.stderr.write(f"[RRA] 错误: {report_text}\n")
        sys.exit(1)

    stock_name = _extract_stock_name(args.pdf_path)
    sys.stderr.write(f"[RRA] 标的: {stock_name}  模式: {args.mode}\n")

    output_parts = []

    # 范式1
    if args.mode in ("all", "extraction"):
        sys.stderr.write("[RRA] 执行范式1: 要素脱水\n")
        output_parts.append(run_extraction(report_text, stock_name, args.n))

    # 范式2
    if args.mode in ("all", "logic"):
        sys.stderr.write("[RRA] 执行范式2: 逻辑链解构\n")
        output_parts.append(run_logic(report_text, stock_name))

    # 范式3
    if args.mode in ("all", "comparison"):
        if args.pdf2:
            report_2_text = parse_pdf(args.pdf2)
            if report_2_text.startswith("[Error]"):
                sys.stderr.write(f"[RRA] 第二份PDF错误: {report_2_text}\n")
            else:
                sys.stderr.write("[RRA] 执行范式3: 多源对比\n")
                r1_name = _extract_stock_name(args.pdf_path) + "_1"
                r2_name = _extract_stock_name(args.pdf2) + "_2"
                output_parts.append(run_comparison(report_text, r1_name, report_2_text, r2_name, stock_name))
        else:
            sys.stderr.write("[RRA] 范式3需要--pdf2参数，已跳过\n")

    # 范式4
    if args.mode in ("all", "risk"):
        sys.stderr.write("[RRA] 执行范式4: 风险透视\n")
        output_parts.append(run_risk(report_text, stock_name))

    # 合并输出
    full_report = "\n\n".join(output_parts)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(full_report)
        sys.stderr.write(f"[RRA] 报告已写入: {args.output}\n")
    else:
        print(full_report)


if __name__ == "__main__":
    main()
