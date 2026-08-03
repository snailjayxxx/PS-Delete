# Photoshop 插件

## 安装

1. 先安装并启动 Release 中对应系统的 `JossAICleanupCore`。
2. 双击 Release 中的 `.ccx` 文件，通过 Creative Cloud 安装。
3. Photoshop 中打开 `插件 → Joss AI Cleanup`。
4. 在插件 API 设置中保存至少一个服务的 API Key。

## 使用

1. 使用套索、对象选择或快速选择工具建立选区。
2. 在插件中选择处理类型和 AI 服务。
3. 点击“开始处理并创建新图层”。
4. 结果只写入新图层；原图层不会被覆盖。

## 开发加载

使用 Adobe UXP Developer Tool 添加本目录的 `manifest.json`，然后 Load。
