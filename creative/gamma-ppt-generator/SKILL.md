---
name: gamma-ppt-generator
description: "录音文本 → Gamma PPT 自动生成器。将录音转录文本总结为专业投资报告大纲，通过 Gamma API 生成 PPT 并导出 PDF。触发场景：(1) 用户提供录音文本要生成 PPT (2) 需要制作投资报告/行业分析演示 (3) 调用 Gamma API 创建文档"
version: 1.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [ppt, gamma, presentation, investment-report]
    category: creative
---

# Gamma PPT Generator

将录音转录文本自动总结为 PPT 大纲并通过 Gamma API 生成专业投资报告。

## 依赖

```bash
pip3 install -r requirements.txt
```

## 环境变量

需要以下环境变量（在 `.env` 或 Claude Code 的 `settings.local.json` 中）：

| 变量 | 说明 |
|------|------|
| `LAOZHANG_API_KEY` | 老张 API 密钥 |
| `LAOZHANG_API_BASE` | 老张 API 地址 |
| `LAOZHANG_MODEL` | 模型名称 |
| `GAMMA_API_KEY` | Gamma API 密钥 |
| `GAMMA_API_BASE` | Gamma API 地址 |
| `GAMMA_THEME_ID` | Gamma 主题 ID |
| `DEFAULT_NUM_CARDS` | 默认卡片数 |
| `OUTPUT_LANGUAGE` | 输出语言 |

## 使用

```bash
python3 scripts/generate_ppt.py <录音文本文件路径>
```

## 输出

- `<文件名>-PPT大纲.md` — Markdown 大纲
- `<文件名>-PPT.pdf` — PDF 文件
- Gamma 在线链接
