from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import os

# 查找系统中文字体
font_paths = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
font_path = None
for fp in font_paths:
    if os.path.exists(fp):
        font_path = fp
        break

if not font_path:
    # 回退到 reportlab 内置
    print("No CJK font found, creating English-only sample")
    font_path = None

c = canvas.Canvas("samples/catl_sample_g3.pdf", pagesize=A4)
width, height = A4
y = height - 40
line_height = 14

lines = [
    "Research Report - CATL (300750)",
    "",
    "Investment Rating: Overweight  Target Price: 320.00 CNY",
    "",
    "1. Company Overview",
    "CATL is the world's largest EV battery manufacturer.",
    "Global market share: 37%.",
    "",
    "2. Financial Performance",
    "Revenue 2025: 456.8 billion CNY, YoY +15.2%.",
    "Net profit: 58.3 billion CNY, YoY +21.4%.",
    "",
    "Wind数据显示，2025年全球动力电池装机量894GWh，同比增长28%。",
    "Bloomberg数据，CATL海外收入超1200亿元。",
    "据中国汽车动力电池产业创新联盟统计，CATL国内市占率45%。",
    "Choice数据显示，2026Q1锂电产业链毛利率中位数18.7%。",
    "同花顺iFinD统计，近三个月42家机构给予买入或增持评级。",
    "东方财富终端显示融资余额环比增长12%。",
    "根据上海有色网数据，碳酸锂现货价年初至今上涨34%。",
    "",
    "3. Risk Factors",
    "Competition from BYD (20% domestic share).",
    "Lithium price volatility.",
    "EU anti-subsidy investigation.",
    "Customer concentration: Top 3 contribute 52% of revenue.",
    "",
    "4. Recommendation",
    "We recommend buying on dips at current levels.",
    "建议买入，目标价320元。",
    "The stock is worth investing at current levels.",
    "",
    "Disclaimer: For reference only, not investment advice.",
]

if font_path:
    pdfmetrics.registerFont(TTFont('CJK', font_path))
    c.setFont('CJK', 10)
else:
    c.setFont('Helvetica', 10)
    # Filter out Chinese lines
    lines = [l for l in lines if all(ord(ch) < 128 for ch in l)]

for line in lines:
    if y < 50:
        c.showPage()
        y = height - 40
        if font_path:
            c.setFont('CJK', 10)
        else:
            c.setFont('Helvetica', 10)
    c.drawString(40, y, line)
    y -= line_height

c.save()
print("Sample PDF created: samples/catl_sample_g3.pdf")
