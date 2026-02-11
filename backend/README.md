# SD Gallery Backend

这是用于为前端提供图片与目录的简单 FastAPI 服务。

运行方法（示例）：

```bash
# 设置要浏览的输出根目录，例如：
export BASE_DIR="/path/to/your/output"
# 启动 uvicorn（开发模式）：
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API:
- `GET /api/folders?path=relative/path` 列出该相对路径下的子文件夹与图片文件名
- `GET /api/image?path=relative/path/to/image.png` 直接返回图片流
- `GET /api/image?path=...&download=true` 下载图片（Content-Disposition header）
