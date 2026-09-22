# AGENTS.md

本仓库是 A 股开盘前早报（HTML）站点。

## 生成或改早报时

必须先阅读并严格执行 `prompts/ashare-preopen-briefing.md`。

该文件正文是自动任务原 Prompt（一至七条：交易日判断、iFinD、报告九段结构、29 个固定板块、HTML/附件/GitHub 交付）。第八条是排版与映射增量，第九条是知识星球分享文案，第十条是供收盘核验的当日判断基线，均不得覆盖原文。生成或修改收盘报告时还必须读取 `prompts/ashare-close-briefing.md`。

提示词版本见 `prompts/VERSION`。冻结的用户原文在 `prompts/archive/v0.2.0_2026-09-21_user-original-1-to-7/`，**禁止修改 archive/**。改提示词后运行：

```bash
python3 scripts/snapshot_prompt.py --version 0.4.0 --slug short-name --notes "改了什么"
```

仪表盘应粘贴的完整文本：`prompts/automation-dashboard-prompt.md`

生成后运行 `python3 scripts/build_index.py`。报告必须进入 `main`。若只能开拉取请求，同一轮合并进 `main`；`.github/workflows/merge-briefing.yml` 会兜底合并当日早报拉取请求。

对话交付顺序：① 不超过 500 字摘要 ② 知识星球分享文案（纯文本代码块，标题+正文，不要写链接；用户自己上传 HTML 文件）③ 仓库相对路径 ④ 附件 + 完整 HTML。休市日不生成完整报告，但仍要给短版星球文案。
