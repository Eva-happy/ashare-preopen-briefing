# 提示词怎么做版本管理

自动任务仪表盘**只保存当前一份 Prompt**，改完就盖掉，这里读不到正文，也没有仪表盘历史。  
真正能留住旧版的是 **Git 提交** 和 **`prompts/archive/` 冻结件**。

## 三份角色，不要混用

| 文件 | 角色 |
| --- | --- |
| `prompts/ashare-preopen-briefing.md` | 当前完整规范（永远最新） |
| `prompts/automation-dashboard-prompt.md` | 当前粘贴进自动任务的文本 |
| `prompts/ashare-close-briefing.md` | 收盘自动任务叠加规范（早晚对照等） |
| `prompts/archive/v*/` | 冻结快照，**禁止改内容** |
| `prompts/archive/v0.2.0_2026-09-21_user-original-1-to-7/` | 你贴出来的原文一至七条，作为对照原件 |

`prompts/VERSION` 记录当前版本号。变更写在 `prompts/CHANGELOG.md`。

## 怕贴的不是仪表盘最新版时

1. 打开自动任务「A股开盘前多源晨报」→ 复制 Prompt 全文。
2. 和冻结件 `v0.2.0_..._user-original-1-to-7` 对比。
3. 若仪表盘还有仓库没有的句子，把全文发回来，会再归档一版，**不会覆盖 v0.2.0**。

## 以后改规则

1. 只改当前 `prompts/*.md` 工作副本，不要改已有 `archive/`。
2. 运行：

```bash
python3 scripts/snapshot_prompt.py --version 0.4.0 --slug short-english-name --notes "改了什么"
```

3. 把仪表盘文件「开始复制」到「结束复制」整段贴回自动任务并保存。

归档脚本遇到已有目录会直接失败，防止把旧提示词盖掉。
