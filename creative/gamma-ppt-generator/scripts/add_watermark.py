#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF水印和尾页合并工具
- 为内容页添加水印（跳过封面和尾页）
- 合并尾页PDF
"""

import sys
import os
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 配置
WATERMARK_TEXT = "AI车库别墅"
WATERMARK_COLOR = (0.5, 0.5, 0.5)  # 灰色 (RGB)
WATERMARK_OPACITY = 0.5  # 50% 透明度
TAIL_PAGE_PATH = "/Users/sun/Desktop/claude-gamma/PDF尾页.pdf"

def register_chinese_font():
    """注册中文字体"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                return 'ChineseFont'
            except:
                continue
    return 'Helvetica'

def create_watermark(page_width, page_height, font_name):
    """创建水印PDF页面"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    c.saveState()
    c.setFillAlpha(WATERMARK_OPACITY)
    c.setFillColorRGB(*WATERMARK_COLOR)
    c.setFont(font_name, 50)

    c.translate(page_width / 2, page_height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, WATERMARK_TEXT)

    c.restoreState()
    c.save()

    buffer.seek(0)
    return PdfReader(buffer).pages[0]

def add_watermark_to_pdf(input_path, output_path):
    """为PDF添加水印并合并尾页"""

    print(f"正在处理: {input_path}")

    font_name = register_chinese_font()
    print(f"使用字体: {font_name}")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    total_pages = len(reader.pages)
    print(f"原始PDF共 {total_pages} 页")

    for i, page in enumerate(reader.pages):
        page_num = i + 1

        if page_num == 1:
            print(f"  第 {page_num} 页: 封面，跳过水印")
            writer.add_page(page)
        else:
            print(f"  第 {page_num} 页: 内容页，添加水印")

            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            watermark = create_watermark(page_width, page_height, font_name)
            page.merge_page(watermark)
            writer.add_page(page)

    if os.path.exists(TAIL_PAGE_PATH):
        print(f"正在添加尾页: {TAIL_PAGE_PATH}")
        tail_reader = PdfReader(TAIL_PAGE_PATH)
        for page in tail_reader.pages:
            writer.add_page(page)
        print(f"  尾页添加完成")
    else:
        print(f"警告: 尾页文件不存在 - {TAIL_PAGE_PATH}")

    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f"处理完成! 输出文件: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 add_watermark.py <PDF文件路径>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 - {input_path}")
        sys.exit(1)

    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}-final.pdf"

    add_watermark_to_pdf(input_path, output_path)

if __name__ == "__main__":
    main()
