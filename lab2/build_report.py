#!/usr/bin/env python3
"""Build LAB-02B report PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Preformatted, PageBreak)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
# Register a CJK-capable font for Chinese characters
for _f in ["/System/Library/Fonts/PingFang.ttc",
           "/System/Library/Fonts/STHeiti Medium.ttc",
           "/Library/Fonts/Arial Unicode.ttf"]:
    if os.path.exists(_f):
        try:
            pdfmetrics.registerFont(TTFont("CJK", _f))
            CJK_OK = True
            break
        except Exception:
            continue
else:
    CJK_OK = False
from PIL import Image as PILImage

def fit_image(path, max_w_cm=17, max_h_cm=11):
    iw, ih = PILImage.open(path).size
    ratio = iw / ih
    w = max_w_cm * cm
    h = w / ratio
    if h > max_h_cm * cm:
        h = max_h_cm * cm
        w = h * ratio
    return Image(path, width=w, height=h)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.pdf")

styles = getSampleStyleSheet()
h1 = styles["Heading1"]
h2 = styles["Heading2"]
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=11,
                      leading=15)
code = ParagraphStyle("code", parent=styles["Code"], fontSize=9, leading=11,
                      backColor=colors.whitesmoke, borderPadding=4,
                      leftIndent=4, rightIndent=4)

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)
story = []

story += [Paragraph("CSIE 2344, Spring 2026 — Laboratory 2 Report", h1),
          Spacer(1, 0.3*cm),
          Paragraph('Submitted by: <font name="CJK">黃泓諺</font> &nbsp;&nbsp; Student ID: R14922156', body),
          Spacer(1, 0.6*cm)]

# Part 1
story += [Paragraph("Part 1 (32 pts)", h1)]

story += [Paragraph("Q1. (12 pts) Module mult_fast", h2),
          Paragraph("The completed Verilog module mult_fast with proper indexes filled in:", body),
          Spacer(1, 0.2*cm)]

mult_fast_code = """// pipelined fast multiplier
module mult_fast(
    output reg[7:0] P,  // product
    input[3:0] A, B,    // multiplicand and multiplier
    input clk           // clock (posedge)
    );
    // stage 0 (input)
    reg[3:0] a_s0, b_s0;
    always @(posedge clk) begin
        a_s0 <= A;
        b_s0 <= B;
    end
    // stage 1
    wire[3:0] pp0 = a_s0 & {4{b_s0[0]}};
    wire[4:1] pp1 = a_s0 & {4{b_s0[1]}};
    wire[5:2] pp2 = a_s0 & {4{b_s0[2]}};
    wire[6:3] pp3 = a_s0 & {4{b_s0[3]}};
    reg[5:1] sum1;
    always @(pp0, pp1)
        sum1[5:1] <= #7 pp0[3:1] + pp1[4:1];   // 4-bit adder
    reg[7:3] sum3;
    always @(pp2, pp3)
        sum3[7:3] <= #7 pp2[5:3] + pp3[6:3];   // 4-bit adder
    reg[5:0] sum1_s1;
    reg[7:2] sum3_s1;
    always @(posedge clk) begin
        sum1_s1 <= {sum1, pp0[0]};
        sum3_s1 <= {sum3, pp2[2]};
    end
    // stage 2 (output)
    reg[7:2] sum2;
    always @(sum1_s1, sum3_s1)
        sum2[7:2] <= #8 sum1_s1[5:2] + sum3_s1[7:2];   // 6-bit adder
    always @(posedge clk) begin
        P <= {sum2, sum1_s1[1:0]};
    end
endmodule"""

story += [Preformatted(mult_fast_code, code), Spacer(1, 0.4*cm)]

story += [Paragraph("Q2. (12 pts) Waveform with lab2.sav (1750 ~ 1800 sec)", h2),
          fit_image(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots", "part1.png")),
          Spacer(1, 0.3*cm),
          Paragraph("The waveform shows the pipelined multiplier operating with a 10-tick clock cycle. "
                    "Each stage's signals (a_s0/b_s0, pp[0..3], sum1/sum3, sum1_s1/sum3_s1, sum2, P) "
                    "progress correctly through the three pipeline stages, and the output P matches "
                    "the reference P_ref, confirming functional correctness.", body),
          Spacer(1, 0.4*cm)]

story += [Paragraph("Q3. (8 pts) Latency", h2),
          Paragraph("Latency is the worst-case time from a steady input until the final-stage register "
                    "captures the corresponding product. Timing breakdown:", body),
          Spacer(1, 0.15*cm)]

latency_table = """t = 0    Input A, B becomes steady (just after the previous posedge clk).
t = 10   Stage-0 register latches A, B  → a_s0, b_s0.
t = 17   sum1, sum3 settle after the 4-bit adder delay (#7).
t = 20   Stage-1 register latches sum1_s1, sum3_s1.
t = 28   sum2 settles after the 6-bit adder delay (#8).
t = 30   Stage-2 register latches the final product P.
─────────────────────────────────────────────────────────────────
Total latency = 30 ticks (= 3 clock cycles)."""
story += [Preformatted(latency_table, code), Spacer(1, 0.2*cm),
          Paragraph("<b>Answer: 30 ticks.</b>", body)]

story += [PageBreak()]

# Part 2
story += [Paragraph("Part 2 (16 pts)", h1)]

story += [Paragraph("Q1. (8 pts) Minimum clock cycle", h2),
          Paragraph("The minimum clock period is bounded by the slowest combinational path between "
                    "consecutive pipeline registers:", body),
          Spacer(1, 0.15*cm)]

stage_table = """Stage 0 → Stage 1 : 4-bit adder delay  = 7 ticks
Stage 1 → Stage 2 : 6-bit adder delay  = 8 ticks   ← bottleneck

T_min = max(7, 8) = 8 ticks."""
story += [Preformatted(stage_table, code), Spacer(1, 0.2*cm),
          Paragraph("To realise this, mult_tb is modified so the clock half-period becomes 4 "
                    "(<code>#4 clock &lt;= ~clock;</code>), the input-update interval becomes 8 "
                    "(<code>#8</code>), and P_ref is delayed by two clock cycles "
                    "(<code>#16 A*B</code>). All 256 input combinations are exercised and P matches "
                    "P_ref throughout the simulation — no &quot;Product is wrong&quot; messages.", body),
          Spacer(1, 0.2*cm),
          Paragraph("<b>Answer: 8 ticks.</b>", body),
          Spacer(1, 0.4*cm)]

story += [Paragraph("Q2. (8 pts) Waveform with lab2.sav (1750 ~ 1800 sec)", h2),
          fit_image(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots", "part2.png")),
          Spacer(1, 0.3*cm),
          Paragraph("With the clock period reduced to 8 ticks, the waveform is denser: each 8-tick "
                    "period contains one full posedge/negedge cycle. Pipeline timing remains valid "
                    "because each stage's combinational delay (7 ticks for 4-bit adders, 8 ticks for "
                    "the 6-bit adder) fits inside the new clock period, and P continues to track "
                    "P_ref correctly.", body)]

doc.build(story)
print(f"wrote {OUT}")
