# AGENTS.md

本仓库是 A 股开盘前早报（HTML）站点。

换 Cursor 账号或新会话要延续定时任务时，先读 `prompts/CONTINUITY.md`（日程、模型、iFinD、交付顺序、哪些东西在 Git 里、哪些要在新账号重建）。

## 生成或改早报时

必须先阅读并严格执行 `prompts/ashare-preopen-briefing.md`。

该文件正文是自动任务原 Prompt（一至七条：交易日判断、iFinD、报告九段结构、29 个固定板块、HTML/附件/GitHub 交付）。第八条才是后来加上的排版与映射增量，第九条是知识星球分享文案，均不得覆盖原文。

提示词版本见 `prompts/VERSION`。冻结的用户原文在 `prompts/archive/v0.2.0_2026-09-21_user-original-1-to-7/`，**禁止修改 archive/**。改提示词后运行：

```bash
python3 scripts/snapshot_prompt.py --version 0.4.0 --slug short-name --notes "改了什么"
```

仪表盘应粘贴的完整文本：`prompts/automation-dashboard-prompt.md`

生成后运行 `python3 scripts/build_index.py`。报告必须进入 `main`。若只能开拉取请求，同一轮合并进 `main`；`.github/workflows/merge-briefing.yml` 会兜底合并当日早报拉取请求。

对话交付顺序：① 不超过 500 字摘要 ② 知识星球分享文案（纯文本代码块，标题+正文，不要写链接；用户自己上传 HTML 文件）③ 仓库相对路径 ④ 一个完整 html 代码块，从 `<!doctype html>` 到 `</html>`，供一键复制，禁止用附件或「已写入仓库」代替 ⑤ 附件。休市日不生成完整报告，但仍要给短版星球文案。

## 生成或改收盘报告时

必须先阅读并严格执行 `prompts/ashare-close-briefing.md`。不要把它和早报提示词混成一份，也不要贴进「A股开盘前多源晨报」。

收盘提示词与早报对齐：同样是一至七条九段 + 第八条排版 + 第九条知识星球文案。数据截止北京时间 15:10。第五条写**当日**复盘，第六条检索窗是当日 08:30 至 15:10，并对照同日早报里指向当天的判断。

文件名：`archive/年/月/A股收盘报告_YYYY-MM-DD_1510.html`。仪表盘粘贴：`prompts/close-automation-dashboard-prompt.md`。版本见 `prompts/close-VERSION`。生成后同样运行 `python3 scripts/build_index.py`。`latest.html` 仍跳最新早报，收盘走 `latest-close.html`。建议日程 `20 7 * * 1-5`（北京时间工作日 15:20），模型用 GPT。

本机 Windows 归档目录是 `D:\Eva-personal\A股开盘前早报归档`，早盘和收盘分开放。工具在 `local-archive/`。双击 `生成收盘报告.bat` 会把最新收盘 HTML 存进 `收盘\`。
