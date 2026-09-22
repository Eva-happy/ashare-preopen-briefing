# 换 Cursor 账号后，如何延续 A 股开盘前早报

给以后任何一个打开本仓库的 Cursor 账号用。先读本文件，再读 `prompts/ashare-preopen-briefing.md`，按 `prompts/VERSION` 里的版本执行。

仓库地址：https://github.com/eva-happy/ashare-preopen-briefing

## 仓库里已经保存、换账号也能读到的

| 要延续的内容 | 位置 |
| --- | --- |
| 当前完整规范（含一至九条） | `prompts/ashare-preopen-briefing.md` |
| 贴进自动任务的正文 | `prompts/automation-dashboard-prompt.md` 里「开始复制」到「结束复制」 |
| 当前版本号 | `prompts/VERSION` |
| 每次改了什么 | `prompts/CHANGELOG.md` |
| 你最初贴出的一至七条（冻结，禁止改） | `prompts/archive/v0.2.0_2026-09-21_user-original-1-to-7/` |
| 之后每一版提示词快照 | `prompts/archive/v*/` |
| 给 Agent 的短指令 | `AGENTS.md`、`.cursor/rules/preopen-briefing.mdc` |
| 发布网页 | `.github/workflows/pages.yml`，只发布 `main` |
| 当日早报拉取请求自动合并 | `.github/workflows/merge-briefing.yml`、`scripts/briefing_pr_eligible.sh` |
| 更新索引和短链 | `python3 scripts/build_index.py` |
| 新版本提示词归档 | `python3 scripts/snapshot_prompt.py` |
| 已生成报告 | `archive/年/月/A股开盘前早报_YYYY-MM-DD_0830.html` 与 `r/YYYY-MM-DD_0830.html` |
| 最新跳转与目录 | `latest.html`、`index.html` |

`prompts/archive/` 只增不改。新版本用归档脚本追加目录。

## 挂在 Cursor 账号上、Git 带不走的

定时任务保存在创建它的那个 Cursor 账号里。另一个账号打开本仓库，能读到上面全部规则和历史报告，需要自己再建一条定时任务，并重新登录同花顺 iFinD。

原账号上这条任务目前仍启用：

| 项 | 值 |
| --- | --- |
| 名称 | A股开盘前多源晨报 |
| ID | `cbeb1ef9-b59d-11f1-bb68-864e54d14197` |
| 页面 | https://cursor.com/automations/cbeb1ef9-b59d-11f1-bb68-864e54d14197 |
| 日程 | `30 0 * * 1-5` |
| 对应时刻 | 北京时间周一至周五 08:30（中国无夏令时，全年如此） |
| 模型 | GPT。沿用 GPT，不要改成 Grok |
| 数据截止 | 当天 08:30（Asia/Shanghai）。晚于该时刻才出现的行情、公告、新闻不倒填 |

接口读不到仪表盘里正在运行的 Prompt 正文。仓库里的 `prompts/automation-dashboard-prompt.md` 是应当贴回去的全文。仪表盘以最后一次手工粘贴为准；若和 `prompts/VERSION` 不一致，以仓库这份为准，整段替换后再保存。

## 新账号重建定时任务

1. 新账号需要能往本仓库推送（GitHub 写权限），Pages 才能在合并后更新。
2. 在 Cursor 新建自动任务，仓库选 `eva-happy/ashare-preopen-briefing`，名称可用「A股开盘前多源晨报」。
3. 日程填 `30 0 * * 1-5`。模型选 GPT。
4. 接上同花顺 iFinD，并完成该账号的登录。生成时要能查到这些数据：

| 用途 | MCP 命名空间 |
| --- | --- |
| 指数、板块代码与行情 | `hexin-ifind-ds-index-mcp` |
| 公告、新闻 | `hexin-ifind-ds-news-mcp` |
| 宏观 EDB | `hexin-ifind-ds-edb-mcp` |
| 隔夜海外股市 | `hexin-ifind-ds-global-stock-mcp` |
| 原油、黄金、铜等期货 | `hexin-ifind-ds-futures-mcp` |
| 美债等债券 | `hexin-ifind-ds-bond-mcp` |
| 个股与两市成交 | `hexin-ifind-ds-stock-mcp` 或 `hexin-ifind-ds-mcp` |

5. 打开 `prompts/automation-dashboard-prompt.md`，只复制「开始复制」与「结束复制」之间的全文，贴进自动任务 Prompt 并保存。
6. 仓库 Settings → Actions → Workflow permissions 设为 Read and write，`.github/workflows/merge-briefing.yml` 才能把当天早报合并进 `main`。
7. Settings → Pages → Source 选 GitHub Actions。

原账号上的那条任务可以继续跑。两条一起开会在同一天各写一份报告，只保留一条启用。

## 一次运行要交出什么

交易日：

1. 不超过 500 字的摘要。
2. 知识星球文案：纯文本，标题加正文。用户自己上传 HTML 文件。文案不写链接，可写「完整内容见本期上传的 HTML 报告」，末句「仅供研究参考，不构成投资建议。」
3. 仓库相对路径，以及给用户自己核对的 Pages 地址（这段不进星球帖）。
4. 对话里一个 html 代码块，从 `<!doctype html>` 到 `</html>`，与保存的文件一致，标题用「报告 HTML 源码」。附件不能代替这段。
5. HTML 附件。

休市：短说明，加一版不带链接的星球短文案，不生成完整报告。

板块名称、代码、行情以同花顺 iFinD 为准。取不到写「未取得」。固定跟踪板块 29 个都要出现在事件矩阵里，08:30 前没有对应事件就标「今日暂无」。清单在提示词第四条，不要在本文件另抄一份以免两处漂移。

## 文件怎么进网页

```text
archive/年/月/A股开盘前早报_YYYY-MM-DD_0830.html
r/YYYY-MM-DD_0830.html
index.html
latest.html
```

生成或改完报告后运行 `python3 scripts/build_index.py`。

Pages 只认 `main`。当天早报若开了拉取请求，标题含北京时间当天日期，以及「早报」或 `preopen briefing`，且改动只在上面四类文件里，`merge-briefing.yml` 会标为可合并、Squash 合并，再触发「Deploy GitHub Pages」。改提示词、README 的拉取请求不会被这个工作流合并。

查看（给用户，不进星球帖）：

- 最新：https://eva-happy.github.io/ashare-preopen-briefing/latest.html
- 目录：https://eva-happy.github.io/ashare-preopen-briefing/
- 某一期：https://eva-happy.github.io/ashare-preopen-briefing/r/YYYY-MM-DD_0830.html

`latest.html` 用跳转指向最新一期。浏览器若仍显示旧报告，在地址后加当天日期，例如 `latest.html?20260922`。源码页在 `github.com/.../blob/main/r/...html`，那个页面是代码，不是给读者打开的报告。

## 已落在 main 上的报告（截至 2026-09-22）

- `r/2026-09-21_0830.html`
- `r/2026-09-22_0830.html`

以后新增日期以 `r/` 目录和 `latest.html` 为准。

## 改规则时

1. 只改 `prompts/ashare-preopen-briefing.md` 和 `prompts/automation-dashboard-prompt.md`。
2. 运行 `python3 scripts/snapshot_prompt.py --version 0.4.0 --slug short-english-name --notes "改了什么"`。已有归档目录时脚本会失败，这是故意的。
3. 把新的「开始复制」到「结束复制」整段贴回自动任务并保存。
4. 若仪表盘里还有仓库没有的句子，整段发回来再归档一版，不覆盖 `v0.2.0`。
