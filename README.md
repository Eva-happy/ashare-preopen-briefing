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

新增报告后运行：

```bash
python3 scripts/build_index.py
```

会自动：

- 更新 `index.html`（列表 + 每期分享链接）
- 更新 `latest.html`（跳转最新一期）
- 生成英文短链副本 `r/YYYY-MM-DD_HHMM.html`（方便分享，避免中文文件名在 App 里乱码）

## 早报自动进入 main

GitHub Pages 只发布 `main`。定时任务如果只开草稿拉取请求，短链会 404。

`.github/workflows/merge-briefing.yml` 会在拉取请求出现时检查：

- 标题含北京时间当天日期，以及「早报」或 `preopen briefing`
- 改动只在 `archive/*.html`、`r/*.html`、`index.html`、`latest.html`

符合就标为可合并、Squash 合并进 `main`，再触发「Deploy GitHub Pages」。其他拉取请求不会动。

这个工作流要先在 `main` 上，下一次早报才会自动合并。仓库 Actions 权限需要是 Read and write。
