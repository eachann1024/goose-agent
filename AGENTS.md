# Goose Agent — 给助手的约定（压缩版）

- **中文优先**：所有用户可见文案必须有 `zh-Hans`；新增 `String(localized:)` / `Label` / `Text` / `Button` / `.help` / `LocalizedStringKey` 时同步写入 `Resources/Localizable.xcstrings`（en + zh-Hans），禁止界面残留英文（专有名词如 Agent、Mac、SSH、路径可保留）。
- **设置与弹窗尺寸**：共用 `SheetLayout` / Settings 最小宽高；改尺寸只改常量，勿各写死。
- **快捷键**：走 `AppShortcuts`；侧栏 hover 显示当前绑定；勿再写死 ⌘⌥ 组合。
- **构建与运行**：改完 `make build`；确认 `/Applications/Goose Agent.app` 已替换且正在运行的是新安装的应用。安装或重启失败不能只报编译成功，须处理失败并如实说明运行状态；编译通过与实际界面验证分别报告。

## 演示视频与仓库文件

- README 只保留一处 GitHub user-attachments 内联视频（单独一行的裸链接）；禁止添加「演示视频 / Watch the video / 旁白版」等文字链接，禁止链接仓库内 raw/blob 的 mp4。
- 禁止向仓库提交视频副本、封面图、poster、contact sheet、临时脚本或相关文档描述。

## 提交与推送

- 只在 `main` 上开发，不新建分支或 worktree；当前不在 `main` 时先告知用户。
- 每次改动完成后，先获取并合并远端最新 `main`（`git fetch origin`，再将 `origin/main` 合入本地），再提交推送；不得只 fetch 不合并，也不得先提交本次改动再同步。同步前妥善保留未提交工作，恢复后也要检查冲突。
- 有冲突就逐项理解并解决，保留双方有效改动；按影响面完成必要验收后，只原子提交本任务改动并推送 `main`，提交说明用英文。不得覆盖无关工作或强制推送。
- 推送若因远端新增提交被拒绝，重新同步、解决冲突并复核后重试；完成后确认本地提交已包含在远端，不能把仅本地提交当作已推送。
