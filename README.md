# ashare-preopen-briefing

A股开盘前早报（HTML）。目标：复制一条链接，在微信等 App 里直接打开成网页，而不是源码。

## 重要结论

GitHub 仓库里点文件 →「分享」，发出去的是 **源码页**，其他 App 打开仍是代码。  
要「像网页一样打开」，必须分享 **GitHub Pages 链接**（下面这种）：

- 最新一期：https://eva-happy.github.io/ashare-preopen-briefing/latest.html
- 索引首页：https://eva-happy.github.io/ashare-preopen-briefing/
- 某一期（英文短链，方便复制）：https://eva-happy.github.io/ashare-preopen-briefing/r/2026-09-21_0830.html

## 手机分享到微信等 App

1. 把仓库设为 **Public**（别人才能打开；Private 即使自己能看，对方通常打不开）
2. 启用 Pages：Settings → Pages → Source 选 **GitHub Actions**，合并后等部署成功
3. 复制上面的 `latest.html` 或 `r/日期_时间.html` 链接
4. 粘贴到微信 / 浏览器 / 备忘录 → 点开即为排版报告

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
```

## 自动任务提示词

定时生成由 Cursor 自动任务 **「A股开盘前多源晨报」** 执行：

https://cursor.com/automations/cbeb1ef9-b59d-11f1-bb68-864e54d14197

完整规范在仓库内，**在原十段早报功能上增量修订**，不是另写一套。修改报告要求时先改文件，再把短版贴回自动任务 Prompt：

- 完整规范：[`prompts/ashare-preopen-briefing.md`](prompts/ashare-preopen-briefing.md)
- 仪表盘粘贴文本：[`prompts/automation-dashboard-prompt.md`](prompts/automation-dashboard-prompt.md)

当前接口读不到自动任务 Prompt 正文，保存仪表盘仍需在上述链接里手动替换一次。

新增报告后运行：

```bash
python3 scripts/build_index.py
```

会自动：

- 更新 `index.html`（列表 + 每期分享链接）
- 更新 `latest.html`（跳转最新一期）
- 生成英文短链副本 `r/YYYY-MM-DD_HHMM.html`（方便分享，避免中文文件名在 App 里乱码）
