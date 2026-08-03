# Changelog

## 0.1.1 - 2026-08-04

- 修复 Photoshop CCX 安装时报错代码 -4（Manifest Parse Failure）。
- 将 UXP Manifest 的 `host` 从开发模式数组改为可分发 CCX 要求的单个对象。
- 新增 Photoshop 源目录与打包后 CCX 的自动结构校验。
- 打包时确保 `manifest.json` 位于 CCX 根目录，并移除跨平台 ZIP 扩展属性。
- Release 增加 Developer Load ZIP，作为 Creative Cloud 安装器异常时的备用加载方式。
- Release 工作流改为从 `VERSION` 动态读取版本并核对 Release PR 标题。

## 0.1.0 - 2026-08-04

- 建立 Photoshop UXP 与 Lightroom Classic Lua 双插件结构。
- Photoshop 支持读取当前选区、上下文扩张、AI 编辑和透明新图层写回。
- Lightroom Classic 支持批量渲染 TIFF、调用本地核心、导回目录并与原图堆叠。
- 新增 OpenAI、Gemini、阿里百炼、火山方舟、百度千帆和 OpenAI 兼容接口适配层。
- 新增 macOS / Windows 本地核心安装脚本。
- 新增 GitHub Actions 自动构建插件包、本地核心和 Release。
