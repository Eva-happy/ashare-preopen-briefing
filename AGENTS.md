# AGENTS.md

本仓库是 A 股开盘前早报（HTML）站点。

## 生成或改早报时

必须先阅读并严格执行 `prompts/ashare-preopen-briefing.md`。

该文件正文是自动任务原 Prompt（一至七条：交易日判断、iFinD、报告九段结构、29 个固定板块、HTML/附件/GitHub 交付）。第八条才是后来加上的排版与映射增量，不得覆盖原文。

仪表盘应粘贴的完整文本：`prompts/automation-dashboard-prompt.md`

生成后运行 `python3 scripts/build_index.py`。
