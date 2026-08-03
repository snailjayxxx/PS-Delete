# Joss AI Cleanup Core

本地运行的共享处理核心。Photoshop 插件通过 `127.0.0.1:18780` 调用；Lightroom Classic 插件通过命令行调用。

```bash
python -m pip install -r requirements.txt
python -m joss_ai_cleanup serve
```

配置示例：

```bash
python -m joss_ai_cleanup configure --provider gemini --api-key YOUR_KEY
python -m joss_ai_cleanup configure --provider openai --api-key YOUR_KEY
python -m joss_ai_cleanup configure --provider dashscope --api-key YOUR_KEY --workspace-id YOUR_WORKSPACE_ID
```
