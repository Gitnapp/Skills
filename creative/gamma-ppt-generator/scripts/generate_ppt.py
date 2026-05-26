#!/usr/bin/env python3
"""
录音文本转PPT自动化工具
功能：
1. 使用老张API调用Claude模型总结录音文本
2. 生成Gamma PPT大纲并保存为MD文件
3. 使用Gamma API生成PPT并保存为PDF
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 配置
LAOZHANG_API_KEY = os.getenv('LAOZHANG_API_KEY')
LAOZHANG_API_BASE = os.getenv('LAOZHANG_API_BASE')
LAOZHANG_MODEL = os.getenv('LAOZHANG_MODEL')
GAMMA_API_KEY = os.getenv('GAMMA_API_KEY')
GAMMA_API_BASE = os.getenv('GAMMA_API_BASE', 'https://public-api.gamma.app/v1.0')
GAMMA_THEME_ID = os.getenv('GAMMA_THEME_ID')


def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        sys.exit(1)


def summarize_with_laozhang_api(transcript_text, prompt_text, transcript_filename):
    """使用老张API调用Claude模型总结录音文本（使用流式输出避免超时）"""
    print("\n📝 步骤1: 使用老张API总结录音文本...", flush=True)

    # 构建完整的提示词
    full_prompt = f"""{prompt_text}

---

**录音文件名**: {transcript_filename}

**录音转录文本**:

{transcript_text}

---

请严格按照上述要求，生成详细的Gamma文档PPT大纲。
"""

    print(f"   API地址: {LAOZHANG_API_BASE}")
    print(f"   使用模型: {LAOZHANG_MODEL}")
    print(f"   文本长度: {len(transcript_text)} 字符")

    # 连接不稳定检测配置
    max_retries = 2  # 最多重试2次（共3次尝试）
    connection_errors = 0  # 连接错误计数
    max_connection_errors = 1  # 允许的最大连接错误次数，超过则判定为网络不稳定

    for attempt in range(max_retries + 1):
        try:
            # 初始化OpenAI客户端（兼容老张API）
            import httpx
            client = OpenAI(
                api_key=LAOZHANG_API_KEY,
                base_url=LAOZHANG_API_BASE,
                timeout=httpx.Timeout(600.0, connect=30.0),  # 10分钟总超时，30秒连接超时
                max_retries=0  # 我们自己处理重试
            )

            print(f"   正在调用API... (尝试 {attempt + 1}/{max_retries + 1})")
            print(f"   使用流式输出模式...")

            # 使用流式输出调用API
            stream = client.chat.completions.create(
                model=LAOZHANG_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                stream=True  # 启用流式输出
            )

            # 收集流式响应
            summary_parts = []
            char_count = 0
            last_progress_report = 0
            no_data_count = 0  # 连续无数据计数

            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        summary_parts.append(delta.content)
                        char_count += len(delta.content)
                        no_data_count = 0  # 重置无数据计数
                        # 每5000字符报告一次进度
                        if char_count - last_progress_report >= 5000:
                            print(f"   已接收 {char_count} 字符...", flush=True)
                            last_progress_report = char_count

            summary = ''.join(summary_parts)

            # 检查是否收到有效响应
            if len(summary) < 100:
                print(f"❌ API返回内容过短（{len(summary)}字符），可能连接中断")
                print("   请检查网络连接后重试")
                sys.exit(1)

            print(f"✅ 总结完成，生成内容长度: {len(summary)} 字符", flush=True)
            return summary

        except (httpx.ConnectError, httpx.ConnectTimeout, ConnectionError, TimeoutError) as e:
            # 连接类错误 - 网络不稳定
            connection_errors += 1
            error_type = type(e).__name__
            print(f"   ❌ 连接错误 [{connection_errors}/{max_connection_errors + 1}]: {error_type}")

            if connection_errors > max_connection_errors:
                print(f"\n{'='*50}")
                print(f"❌ 网络连接不稳定，已中断运行")
                print(f"   错误类型: {error_type}")
                print(f"   请检查网络连接后重新运行程序")
                print(f"{'='*50}")
                sys.exit(1)
            else:
                print(f"   等待 5 秒后重试...")
                time.sleep(5)

        except (httpx.ReadTimeout, httpx.WriteTimeout) as e:
            # 读写超时 - 可能是API响应慢或网络不稳
            error_type = type(e).__name__
            print(f"\n{'='*50}")
            print(f"❌ API响应超时，已中断运行")
            print(f"   错误类型: {error_type}")
            print(f"   可能原因: 网络不稳定或API服务器繁忙")
            print(f"   请稍后重新运行程序")
            print(f"{'='*50}")
            sys.exit(1)

        except Exception as e:
            error_type = type(e).__name__
            print(f"   ⚠️ 尝试 {attempt + 1} 失败: {error_type}: {e}")

            # 检查是否是SSL或网络相关错误
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['ssl', 'connection', 'timeout', 'network', 'socket']):
                print(f"\n{'='*50}")
                print(f"❌ 网络连接不稳定，已中断运行")
                print(f"   错误详情: {e}")
                print(f"   请检查网络连接后重新运行程序")
                print(f"{'='*50}")
                sys.exit(1)

            if attempt < max_retries:
                print(f"   等待 5 秒后重试...")
                time.sleep(5)
            else:
                print(f"❌ API调用失败")
                import traceback
                traceback.print_exc()
                sys.exit(1)


def save_outline(outline_text, transcript_filename):
    """保存PPT大纲为MD文件"""
    print("\n💾 步骤2: 保存PPT大纲...", flush=True)

    # 从录音文件名提取基础名称
    base_name = Path(transcript_filename).stem
    # 移除可能的"-转文本结果"后缀
    base_name = base_name.replace('-转文本结果', '').replace('转文本结果', '')

    # 生成输出文件名
    output_filename = f"{base_name}-gamma outline.md"
    output_path = Path(__file__).parent / output_filename

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(outline_text)
        print(f"✅ 大纲已保存: {output_path}", flush=True)
        return str(output_path), base_name
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        sys.exit(1)


def create_gamma_ppt(outline_text, base_name):
    """使用Gamma API生成PPT"""
    print("\n🎨 步骤3: 使用Gamma API生成PPT...", flush=True)

    # Gamma API配置
    gamma_api_base = GAMMA_API_BASE
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": GAMMA_API_KEY
    }

    # 配色和排版说明
    additional_instructions = """
配色方案：
- 全文统一使用专业投资蓝色主题
- 主色：深蓝色(#2C5282)用于标题
- 辅色：浅蓝色(#4299E1)用于强调
- 背景：白色+浅蓝灰
- 严禁使用红、粉、紫、绿、橙等杂色

生成图表规范：
- 确保文字排版和图表格局排版尽可能对齐，如果是以列为排列，图表上下高度要和文字对齐，如果图表较大较长，可采用横板排版排2排，即图表上排，文字下排
- 图表不要有大面积空白，不使用大图表，必要的时候使用小图表

排版规范：
- 避免大面积空白，内容充实
- 每页内容占75-85%页面空间
- 标题清晰：大标题28-32pt，小标题18-22pt，正文12-14pt
- 行距1.5倍，段落间距适中
- 表格用蓝色表头，数据行浅色交替

整体风格：
- 专业投资报告风格，简洁现代
- 确保视觉统一性和专业性
"""

    # 构建请求数据 - 使用正确的Gamma API格式
    request_data = {
        "textMode": "generate",  # 生成模式
        "inputText": outline_text,
        "format": "document",  # 创建文档
        "exportAs": "pdf",  # 导出为PDF
        "imageOptions": {"source": "noImages"},  # 不生成图片
        "themeId": GAMMA_THEME_ID,
        "additionalInstructions": additional_instructions,
        "textOptions": {
            "language": "zh-cn"  # 中文
        }
    }

    try:
        # 1. 创建文档
        print("   正在创建Gamma文档...")
        create_url = f"{gamma_api_base}/generations"
        print(f"   请求URL: {create_url}")
        print(f"   大纲长度: {len(outline_text)} 字符")

        # 创建文档请求（不重试，连接失败直接退出）
        try:
            response = requests.post(create_url, headers=headers, json=request_data, timeout=120)  # 2分钟超时
        except requests.exceptions.ConnectTimeout:
            print(f"\n{'='*50}")
            print(f"❌ Gamma API 连接超时，已中断运行")
            print(f"   请检查网络连接后重新运行程序")
            print(f"{'='*50}")
            sys.exit(1)
        except requests.exceptions.ConnectionError as e:
            print(f"\n{'='*50}")
            print(f"❌ Gamma API 连接失败，已中断运行")
            print(f"   错误详情: {e}")
            print(f"   请检查网络连接后重新运行程序")
            print(f"{'='*50}")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print(f"\n{'='*50}")
            print(f"❌ Gamma API 请求超时，已中断运行")
            print(f"   请稍后重新运行程序")
            print(f"{'='*50}")
            sys.exit(1)

        if response.status_code not in [200, 201, 202]:
            print(f"❌ 创建文档失败: {response.status_code}")
            print(f"   响应: {response.text}")
            sys.exit(1)

        result = response.json()
        print(f"   API响应: {result}")  # 调试信息
        generation_id = result.get('generationId') or result.get('id')  # 尝试两个字段
        web_url = result.get('webUrl')

        if not generation_id:
            print(f"❌ 未获取到生成ID")
            print(f"   完整响应: {result}")
            sys.exit(1)

        print(f"✅ 文档创建成功")
        print(f"   生成ID: {generation_id}")
        if web_url:
            print(f"   网页链接: {web_url}")

        # 2. 等待文档生成完成（无时间限制，每30秒报告一次）
        print("   等待文档生成完成...", flush=True)
        start_time = time.time()
        gamma_url = web_url
        pdf_url = None
        consecutive_errors = 0  # 连续错误计数
        max_consecutive_errors = 2  # 最大连续错误次数
        last_report_time = 0  # 上次报告时间

        while True:  # 无限循环直到完成
            get_url = f"{gamma_api_base}/generations/{generation_id}"

            try:
                status_response = requests.get(get_url, headers=headers, timeout=30)  # 30秒超时
                consecutive_errors = 0  # 成功后重置错误计数
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                consecutive_errors += 1
                error_type = type(e).__name__
                print(f"   ❌ 轮询错误 [{consecutive_errors}/{max_consecutive_errors}]: {error_type}")

                if consecutive_errors >= max_consecutive_errors:
                    print(f"\n{'='*50}")
                    print(f"❌ 网络连接不稳定，已中断运行")
                    print(f"   Gamma文档可能仍在生成中")
                    print(f"   请访问网页查看: {web_url}")
                    print(f"{'='*50}")
                    sys.exit(1)

                time.sleep(5)
                continue

            if status_response.status_code == 200:
                doc_status = status_response.json()
                status = doc_status.get('status')

                if status == 'completed':
                    print("✅ 文档生成完成", flush=True)
                    # 获取实际的gamma URL和PDF URL
                    gamma_url = doc_status.get('gammaUrl') or web_url
                    pdf_url = doc_status.get('exportUrl')  # 直接从响应中获取exportUrl

                    if pdf_url:
                        print(f"   找到PDF导出链接")
                    break
                elif status == 'failed':
                    print(f"❌ 文档生成失败: {doc_status.get('error', '未知错误')}")
                    sys.exit(1)
                else:
                    elapsed = int(time.time() - start_time)
                    # 每30秒报告一次状态
                    if elapsed - last_report_time >= 30:
                        print(f"⏳ 当前状态: {status}，已等待 {elapsed} 秒...", flush=True)
                        last_report_time = elapsed
                    time.sleep(5)
            else:
                print(f"   查询状态失败 (HTTP {status_response.status_code})，继续等待...", flush=True)
                time.sleep(5)

        # 3. 下载PDF
        if pdf_url:
            print("   正在下载PDF...")
            try:
                pdf_response = requests.get(pdf_url, timeout=120)  # 2分钟超时

                if pdf_response.status_code == 200:
                    # 保存PDF
                    pdf_filename = f"{base_name}-PPT.pdf"
                    pdf_path = Path(__file__).parent / pdf_filename

                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_response.content)

                    print(f"✅ PDF已保存: {pdf_path}")
                    return gamma_url, str(pdf_path)
                else:
                    print(f"❌ 下载PDF失败: {pdf_response.status_code}")
                    print(f"   PDF链接: {pdf_url}")
                    sys.exit(1)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                error_type = type(e).__name__
                print(f"\n{'='*50}")
                print(f"❌ 下载PDF时网络错误，已中断运行")
                print(f"   错误类型: {error_type}")
                print(f"   PDF链接: {pdf_url}")
                print(f"   请手动下载或检查网络后重试")
                print(f"{'='*50}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ 下载PDF时出错: {e}")
                print(f"   PDF链接: {pdf_url}")
                sys.exit(1)
        else:
            print("   未找到PDF导出链接")
            print(f"\n✅ PPT生成成功!")
            print(f"   在线查看: {gamma_url}")
            print(f"\n   请手动访问上述链接，然后:")
            print(f"   1. 点击右上角的 'Export' 或'导出'")
            print(f"   2. 选择 'PDF' 格式")
            print(f"   3. 下载PDF文件")
            return gamma_url, None

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 生成PPT失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main(transcript_file_path):
    """主函数"""
    print("=" * 60)
    print("🚀 录音文本转PPT自动化工具")
    print("=" * 60)

    # 检查文件是否存在
    if not os.path.exists(transcript_file_path):
        print(f"❌ 文件不存在: {transcript_file_path}")
        sys.exit(1)

    # 获取文件名
    transcript_filename = os.path.basename(transcript_file_path)
    print(f"\n📄 输入文件: {transcript_filename}")

    # 提取基础名称用于检查大纲文件
    base_name = Path(transcript_filename).stem
    base_name = base_name.replace('-转文本结果', '').replace('转文本结果', '')
    outline_filename = f"{base_name}-gamma outline.md"
    outline_path = Path(__file__).parent / outline_filename

    # 检查大纲文件是否已存在
    if outline_path.exists():
        print(f"\n✅ 发现已存在的大纲文件: {outline_path}")
        print("   跳过API调用,直接使用现有大纲")
        outline = read_file(str(outline_path))
    else:
        # 读取录音文本
        transcript_text = read_file(transcript_file_path)

        # 读取Prompt模板
        prompt_file = Path(__file__).parent / "Gamma文档专用PPT大纲生成Prompt.md"
        if not prompt_file.exists():
            print(f"❌ Prompt文件不存在: {prompt_file}")
            sys.exit(1)
        prompt_text = read_file(str(prompt_file))

        # 步骤1: 使用老张API总结
        outline = summarize_with_laozhang_api(transcript_text, prompt_text, transcript_filename)

        # 步骤2: 保存大纲
        outline_path, base_name = save_outline(outline, transcript_filename)

    # 步骤3: 生成PPT
    web_url, pdf_path = create_gamma_ppt(outline, base_name)

    # 完成
    print("\n" + "=" * 60)
    print("✅ 所有步骤完成！")
    print("=" * 60)
    print(f"\n📋 生成的文件:")
    print(f"   - PPT大纲: {outline_path}")
    if pdf_path:
        print(f"   - PPT PDF: {pdf_path}")
    print(f"\n🌐 在线查看: {web_url}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python generate_ppt.py <录音文本文件路径>")
        print("\n示例:")
        print('  python generate_ppt.py "ai车开别墅讨论第一期-转文本结果.txt"')
        sys.exit(1)

    transcript_file = sys.argv[1]
    main(transcript_file)
