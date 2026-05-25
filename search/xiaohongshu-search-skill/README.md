# 小红书搜索 & 正文解析 Skill

无需 Hermes 安装即可使用：

```bash
cd ~/Desktop/eric-skills/cat-search/xiaohongshu-search-skill
python3 scripts/xhs.py search "关键词" --limit 10
python3 scripts/xhs.py detail <note_id>
```

安装到 Hermes：

```bash
mkdir -p ~/.hermes/skills/research/xiaohongshu-search
cp -R ~/Desktop/eric-skills/cat-search/xiaohongshu-search-skill/* ~/.hermes/skills/research/xiaohongshu-search/
```
