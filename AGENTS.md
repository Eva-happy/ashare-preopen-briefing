# AGENTS.md

本仓库是 A 股开盘前早报（HTML）站点。

## 生成或改早报时

必须先阅读并严格执行 `prompts/ashare-preopen-briefing.md`。

该文件正文是自动任务原 Prompt（一至七条：交易日判断、iFinD、报告九段结构、29 个固定板块、HTML/附件/GitHub 交付）。第八条才是后来加上的排版与映射增量，第九条是知识星球分享文案，均不得覆盖原文。

仪表盘应粘贴的完整文本：`prompts/automation-dashboard-prompt.md`

生成后运行 `python3 scripts/build_index.py`。

对话交付顺序：① 不超过 500 字摘要 ② 知识星球分享文案（纯文本代码块，标题+正文，链接只用 GitHub Pages）③ 仓库相对路径 ④ 附件 + 完整 HTML。休市日不生成完整报告，但仍要给短版星球文案。
