# Lightroom Classic 插件

## 安装

1. 安装 Release 中对应系统的 Joss AI Cleanup Core。
2. 解压 `Joss-AI-Cleanup-LR-v0.1.0.zip`。
3. Lightroom Classic 打开 `文件 → 增效工具管理器`。
4. 点击“添加”，选择 `JossAICleanup.lrplugin` 文件夹。

也可以把该文件夹复制到：

- macOS：`~/Library/Application Support/Adobe/Lightroom/Modules/`
- Windows：`%APPDATA%\Adobe\Lightroom\Modules\`

## 使用

1. 在图库中选择照片。
2. 打开 `图库 → 增效工具附加功能 → 使用 Joss AI Cleanup 处理所选照片`。
3. 选择服务、处理类型和输出位置。
4. 插件导出 16 位 TIFF，调用本地核心，再把结果导回并与原图堆叠。

Lightroom Classic 不提供 Photoshop 式像素选区，因此第一版更适合胶片灰尘、划痕、降噪和整图轻度清理。复杂物体移除请使用 PS 插件。
