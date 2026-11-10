# Goose Agent

- 私有维护的 macOS 应用。bundle identifier 保持 `dev.eachann.gooseagent`（本地数据与安装包兼容），Swift target/模块名保持 `GooseAgent`，除非任务明确要求修改；不加发布自动化、公开更新源或上游营销素材。
- 文案：用户可见文案都要有 `zh-Hans`，新增 `String(localized:)` / `Label` / `Text` / `Button` / `.help` / `LocalizedStringKey` 时同步写入 `Resources/Localizable.xcstrings`（en + zh-Hans）；界面不留英文，专有名词（Agent、Mac、SSH、路径）除外。
- 尺寸：设置与弹窗共用 `SheetLayout` / Settings 最小宽高，改尺寸只改常量。
- 快捷键：走 `AppShortcuts`，侧栏 hover 显示当前绑定，不写死组合键。
- 构建：改完执行 `make build`（需 Xcode 与 XcodeGen），确认 `/Applications/Goose Agent.app` 已替换且正在运行的是新版本；安装或重启失败要处理并如实说明，编译通过与界面验证分开报告。

## README 与仓库文件

- README 只保留一处 GitHub user-attachments 内联视频（单独一行的裸链接），不加「演示视频 / Watch the video」之类文字链接，不链接仓库内的 mp4。
- 不提交视频副本、封面图、poster、contact sheet、临时脚本及其说明文档。

## 提交与推送

- 改动验收后直接提交并推送 `main`，无需询问：先保留未提交工作，`git fetch origin` 并合入 `origin/main`，逐项解决冲突（保留双方有效改动），再只原子提交本任务改动，提交说明用英文。
- 推送被拒就重新同步、复核后重试，直到远端包含本次提交；不强制推送，不覆盖无关工作。当前不在 `main` 时先告知用户。
