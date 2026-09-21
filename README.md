# ashare-preopen-briefing

A股开盘前早报（HTML）。手机浏览器打开即可阅读，无需看源码。

## 直接阅读（推荐）

启用 GitHub Pages 后，用手机浏览器打开：

- 索引首页：https://eva-happy.github.io/ashare-preopen-briefing/
- 最新一期：https://eva-happy.github.io/ashare-preopen-briefing/latest.html

### 首次启用 Pages（只需一次）

1. 打开仓库 **Settings → Pages**
2. **Source** 选 **GitHub Actions**
3. 合并本仓库的 Pages workflow 到 `main` 后，Actions 会自动部署
4. 等待绿色勾后，打开上面的链接

> 当前仓库若为 **Private**：免费版 GitHub 不能对私有仓库开 Pages。可选：
> - 把仓库改为 **Public**，或
> - 使用 GitHub Pro / Team（支持私有仓库 Pages）

## 报告存放位置

```text
archive/年/月/A股开盘前早报_YYYY-MM-DD_HHMM.html
```

新增报告后，在仓库根目录运行：

```bash
python3 scripts/build_index.py
```

会自动更新 `index.html`（列表）和 `latest.html`（跳转到最新一期）。推送到 `main` 后 Pages 会自动刷新。
