# Photoshop 插件

## 安装

1. 先安装并启动 Release 中对应系统的 `Joss AI Cleanup Core`。
2. 下载 **v0.1.1 或更高版本**的 Photoshop `.ccx`。
3. 双击 `.ccx`，通过 Creative Cloud 安装。
4. Photoshop 中打开 `插件 → Joss AI Cleanup`。
5. 在插件 API 设置中保存至少一个服务的 API Key。

> 请勿使用 v0.1.0 的 CCX。该版本的 Manifest 使用了仅适合开发加载的 `host` 数组，会导致 Creative Cloud 报错代码 -4。

## Creative Cloud 仍无法安装时

Release 同时提供 `Joss-AI-Cleanup-PS-Developer-Load-v*.zip`：

1. 在 Creative Cloud 中安装并打开 **Adobe UXP Developer Tool**。
2. 解压 Developer Load ZIP。
3. 在 UXP Developer Tool 中点击 **Add Plugin**。
4. 选择解压目录里的 `manifest.json`。
5. 启动 Photoshop，然后点击 **Load**。

该方式属于开发加载，用于区分“插件代码问题”和“Creative Cloud 安装器问题”。

## 使用

1. 使用套索、对象选择或快速选择工具建立选区。
2. 在插件中选择处理类型和 AI 服务。
3. 点击“开始处理并创建新图层”。
4. 结果只写入新图层；原图层不会被覆盖。

## 开发加载

使用 Adobe UXP Developer Tool 添加本目录的 `manifest.json`，然后 Load。
