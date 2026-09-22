# ashare-preopen-briefing

A股开盘前早报（HTML）。目标：复制一条链接，在微信等 App 里直接打开成网页，而不是源码。

## 重要结论

GitHub 仓库里点文件 →「分享」，发出去的是 **源码页**，其他 App 打开仍是代码。  
要「像网页一样打开」，必须分享 **GitHub Pages 链接**（下面这种）：

- 最新早报：https://eva-happy.github.io/ashare-preopen-briefing/latest.html
- 最新收盘报告：https://eva-happy.github.io/ashare-preopen-briefing/latest-close.html
- 索引首页：https://eva-happy.github.io/ashare-preopen-briefing/
- 某一期（英文短链，方便复制）：https://eva-happy.github.io/ashare-preopen-briefing/r/2026-09-21_0830.html

## 手机分享到微信等 App

1. 把仓库设为 **Public**（别人才能打开；Private 即使自己能看，对方通常打不开）
2. 启用 Pages：Settings → Pages → Source 选 **GitHub Actions**，合并后等部署成功
3. 复制上面的 `latest.html` 或 `r/日期_时间.html` 链接
4. 粘贴到微信 / 浏览器 / 备忘录 → 点开即为排版报告。知识星球请上传 HTML 文件，不要把链接当帖文。

不要分享：

- `github.com/.../blob/...html`（源码页）
- `raw.githubusercontent.com/...`（常被当成纯文本）

## 首次启用 Pages（一次）

1. Settings → Pages → Source = **GitHub Actions**
2. 合并本仓库 Pages 相关改动到 `main`
3. Actions 出现绿色勾后，打开上面的链接验证

## 报告存放与更新索引

```text
archive/年/月/A股开盘前早报_YYYY-MM-DD_HHMM.html
archive/年/月/A股收盘报告_YYYY-MM-DD_1510.html
```

## 收盘报告

收盘报告与开盘前早报是**两条分开的自动任务**。结构对齐「A股开盘前多源晨报」的一至九条（九段结构、同一套 29 个板块、排版、知识星球文案），并额外对照同日早报。

- 完整规范：[`prompts/ashare-close-briefing.md`](prompts/ashare-close-briefing.md)
- 仪表盘粘贴文本：[`prompts/close-automation-dashboard-prompt.md`](prompts/close-automation-dashboard-prompt.md)
- 版本：[`prompts/close-VERSION`](prompts/close-VERSION)

建议新建自动任务，名称「A股收盘报告」，日程 `20 7 * * 1-5`（北京时间工作日 15:20），模型用 GPT，接上同花顺 iFinD。不要把收盘提示词贴进「A股开盘前多源晨报」。`latest.html` 仍然只打开最新早报；收盘报告用 `latest-close.html`。

## 本机归档（早盘 / 收盘）

Windows 本机目录：`D:\Eva-personal\A股开盘前早报归档`

仓库里的工具箱：[`local-archive/`](local-archive/)。在仓库中双击 `local-archive/安装到本机归档目录.bat`，会：

- 创建 `早盘\` 和 `收盘\`
- 把已有早报 HTML 放进 `早盘\`
- 复制三个 BAT：`整理归档.bat`、`生成早盘报告.bat`、`生成收盘报告.bat`

之后在本机目录双击「生成收盘报告.bat」，会从 GitHub Pages 下载完整收盘 HTML 并打开。需要 Python 3。收盘自动任务 15:20 跑完并进入 `main` 之前，这个 BAT 不会编造报告。

## 自动任务提示词

定时生成由 Cursor 自动任务 **「A股开盘前多源晨报」** 执行：

https://cursor.com/automations/cbeb1ef9-b59d-11f1-bb68-864e54d14197

完整规范在仓库内，**正文是原自动任务 Prompt，第八条才是排版增量，第九条是知识星球分享文案**。当前版本见 [`prompts/VERSION`](prompts/VERSION)，变更见 [`prompts/CHANGELOG.md`](prompts/CHANGELOG.md)，旧版冻结在 [`prompts/archive/`](prompts/archive/)。用法见 [`prompts/README.md`](prompts/README.md)。

修改要求时先改当前文件，再运行 `python3 scripts/snapshot_prompt.py` 追加归档（不会覆盖旧目录），最后把 `prompts/automation-dashboard-prompt.md` 整段贴回自动任务 Prompt：

- 完整规范：[`prompts/ashare-preopen-briefing.md`](prompts/ashare-preopen-briefing.md)
- 仪表盘粘贴文本：[`prompts/automation-dashboard-prompt.md`](prompts/automation-dashboard-prompt.md)

当前接口读不到自动任务 Prompt 正文，保存仪表盘仍需在上述链接里手动替换一次。

自动任务对话必须额外输出一份**知识星球分享文案**（标题 + 正文，纯文本可复制）。星球里上传 HTML 文件，文案不要写链接。规则见提示词第九条。

早报若只开了拉取请求，Pages 不会更新。`.github/workflows/merge-briefing.yml` 会把「标题含当天日期和早报、且只改报告文件」的拉取请求合并进 `main`，并触发 Pages 部署。

新增报告后运行：

```bash
python3 scripts/build_index.py
```

会自动：

- 更新 `index.html`（列表 + 每期分享链接，区分早报和收盘报告）
- 更新 `latest.html`（只跳最新早报）和 `latest-close.html`（只跳最新收盘报告）
- 生成英文短链副本 `r/YYYY-MM-DD_HHMM.html`（方便分享，避免中文文件名在 App 里乱码）

## 早报自动进入 main

GitHub Pages 只发布 `main`。定时任务如果只开草稿拉取请求，短链会 404。

`.github/workflows/merge-briefing.yml` 会在拉取请求出现时检查：

- 标题含北京时间当天日期，以及「早报」「收盘」或对应的英文 briefing 字样
- 改动只在 `archive/*.html`、`r/*.html`、`index.html`、`latest.html`、`latest-close.html`

符合就标为可合并、Squash 合并进 `main`，再触发「Deploy GitHub Pages」。其他拉取请求不会动。

这个工作流要先在 `main` 上，下一次早报才会自动合并。仓库 Actions 权限需要是 Read and write。
