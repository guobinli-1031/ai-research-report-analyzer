from fpdf import FPDF

class ChinesePDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = ChinesePDF()
pdf.add_page()
pdf.set_font("Helvetica", "", 12)

content = """Research Report - Fuyao Glass (600660)

Investment Rating: Buy  Target Price: 65.00 CNY

1. Company Overview
Fuyao Glass Industry Group Co., Ltd. is the world's largest automotive glass manufacturer, with a global market share of 35% and domestic market share of 68%.

2. Financial Highlights (2025 Full Year)
- Revenue: 45.787 billion CNY, YoY +12.3%
- Net Profit: 9.312 billion CNY, YoY +8.7%
- ROE: 18.5%
- PE (TTM): 14.71x, significantly below industry average of 55.96x
- Dividend Yield: 4.15%

3. Q1 2026 Performance
- Revenue: 10.413 billion CNY, YoY +5.08%
- Net Profit: 1.712 billion CNY, YoY -15.68%
- Revenue growth continued but profit declined due to rising raw material costs and R&D investment

4. Competitive Advantages
- Absolute market leader in automotive glass globally
- High value-added products now account for 54.2% of revenue (up 5.44pct YoY)
- New order bookings of 4.62 billion CNY, scheduled through Q1 2027
- Vertical integration reduces cost volatility

5. Risk Factors
- Succession risk: Cao Dewang resigned, Cao Hui to take over as Chairman in Oct 2025
- Auto industry cyclical downturn may reduce demand
- Raw material cost pressure (PVB film, float glass)
- Exchange rate fluctuation on overseas revenue (over 40% from overseas)

6. Valuation
At current price of ~50 CNY, the stock trades at 14.71x TTM PE, a 74% discount to industry average. Historical PE band suggests support at 13x. With normalized earnings recovery expected in H2 2026, we see 30%+ upside potential to our target of 65 CNY.

We recommend buying on weakness with a 12-month target of 65 CNY. The stock is worth investing at current levels.

Disclaimer: This report is for reference only and does not constitute investment advice.
"""

pdf.multi_cell(0, 6, content)
pdf.output("samples/fuyao_sample_en.pdf")
print("Sample PDF created: samples/fuyao_sample_en.pdf")
