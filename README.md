# PS-Delete / Joss AI Cleanup

面向 Photoshop 与 Lightroom Classic 的本地优先 AI 图片清理插件。两个插件分别开发，但共用一个安装在用户电脑上的处理核心和 API Provider 适配层。

## 当前版本：0.1.1

### Photoshop

- 读取当前像素选区和羽化蒙版。
- 自动增加 0%～50% 周边上下文。
- 仅把选区附近的图像交给 AI。
- 结果以带透明蒙版的新像素图层写回，不覆盖原图层。
- 支持人物、杂物、胶片灰尘、毛发、划痕、降噪和授权覆盖物清理。

### Lightroom Classic

- 对所选照片应用当前显影设置并渲染为 16 位 TIFF / ProPhoto RGB。
- 调用本地核心处理。
- 自动把结果导回目录，并与原照片堆叠。
- 支持批量处理和独立失败记录。

Lightroom Classic 没有 Photoshop 式像素选区，因此复杂的局部对象移除应优先使用 Photoshop 插件。

## AI 服务

当前包含：

- 阿里云百炼 / 万相
- 火山引擎方舟 / 豆包图像模型
- 百度千帆图像编辑
- Google Gemini 图像模型
- OpenAI GPT Image
- 自定义 OpenAI 兼容图像编辑接口

模型名、Base URL、Workspace ID 和 Endpoint ID 均可配置，避免将某个会变化的模型写死到插件流程中。

## 下载与安装

进入 GitHub Releases 下载：

- `Joss-AI-Cleanup-Core-macOS-Apple-Silicon-v0.1.1.zip` 或 `Joss-AI-Cleanup-Core-Windows-x64-v0.1.1.zip`
- `Joss-AI-Cleanup-PS-v0.1.1.ccx`
- `Joss-AI-Cleanup-LR-v0.1.1.zip`

安装顺序：

1. 安装并启动本地 Core。
2. 双击 PS `.ccx` 安装，或在 Lightroom Classic 增效工具管理器中添加 `.lrplugin`。
3. 在 PS 插件中保存 API Key；PS 与 LR 会共用该本地配置。

### Photoshop 错误代码 -4

请勿使用 v0.1.0 的 Photoshop CCX。该版本的 UXP Manifest 把 `host` 写成了仅适合开发加载的数组，会触发 Creative Cloud 的 Manifest Parse Failure（错误代码 -4）。v0.1.1 已改为 Adobe 分发要求的单个对象，并在 CI 中对源目录和打包后的 CCX 同时校验。

若 Creative Cloud 安装器仍有异常，可下载 `Joss-AI-Cleanup-PS-Developer-Load-v0.1.1.zip`，解压后用 Adobe UXP Developer Tool 添加其中的 `manifest.json` 并 Load。

> macOS 构建尚未进行 Apple Developer ID 签名和公证，首次运行可能需要在“系统设置 → 隐私与安全性”中允许。
>
> `.ccx` 为独立分发的 UXP 包，尚未经过 Adobe Marketplace 验证，安装时可能显示来源警告。

## 仓库结构

```text
PS/                         Photoshop UXP 插件
LR/JossAICleanup.lrplugin/ Lightroom Classic Lua 插件
core/                       本地 FastAPI / CLI 处理核心
scripts/                    Windows 与 macOS 安装、卸载和包校验脚本
.github/workflows/          自动测试、打包和 Release
```

## 本地开发

```bash
cd core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m joss_ai_cleanup serve
```

Photoshop 使用 Adobe UXP Developer Tool 加载 `PS/manifest.json`。Lightroom Classic 在增效工具管理器中添加 `LR/JossAICleanup.lrplugin`。

## 隐私与授权

- 不建设 SnailJOSS 云端中转。
- API Key 和任务配置只在用户电脑上保存。
- 图片只发送给用户主动选择的 AI 服务商。
- 默认只上传 Photoshop 选区附近的局部区域。
- 文字、Logo、日期戳等覆盖物清理要求用户确认拥有图片或已获得处理授权。

## 状态说明

0.1.1 是安装修复技术预览版。各服务商的图像模型、区域和账号权限可能不同；首次使用前应在插件中确认模型名、Workspace ID 或 Endpoint ID。自动 Release 会生成 SHA-256 校验文件。
