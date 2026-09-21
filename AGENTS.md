# AGENTS.md

本仓库是 A 股开盘前早报（HTML）站点。

## 生成或改早报时

必须先阅读并严格执行：

- `prompts/ashare-preopen-briefing.md`（完整生成规范）
- `prompts/automation-dashboard-prompt.md`（自动任务仪表盘应粘贴的提示词）

自动任务名称：**A股开盘前多源晨报**  
https://cursor.com/automations/cbeb1ef9-b59d-11f1-bb68-864e54d14197

核心修订（相对 2026-09-21 第一版纯文字稿）：

1. 每个板块一张外框卡片，不要散装纯文字并排
2. 每个板块都要有数据解读
3. 隔夜外盘把数值和单位写在同一格，并写解读
4. 公告事件必须映射到板块
5. 催化矩阵覆盖全部 29 个固定板块，没有事件就标「今日暂无」

生成后运行 `python3 scripts/build_index.py`。
