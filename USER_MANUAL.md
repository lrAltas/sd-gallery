# SD Gallery 使用手册

## 简介

此项目提供一个简洁的图片画廊，用于在浏览器中查看 Stable Diffusion 的输出目录（`output`）下的历史生成图片。
项目采用前后端分离：后端使用 `FastAPI` 提供目录与图片接口，前端使用 `Vue 3 + Vite` 实现预览、放大、下载等功能。前后端位于同级目录（`backend/` 与 `frontend/`）。

---

## 目录结构（示例）

- `backend/` — FastAPI 后端代码
- `frontend/` — Vite + Vue 前端代码
- `USER_MANUAL.md` — 本手册

---

## 运行前准备

- 系统要求：Linux / macOS / Windows（推荐 Linux 服务器）
- Python 3.8+（用于后端）、Node.js 16+（用于前端）
- 确保后端运行用户对目标 `output` 目录有读取权限

---

## 后端（开发）运行方法

1. 进入后端目录并安装依赖：

```bash
cd backend
python3 -m pip install -r requirements.txt
```

2. 指定要浏览的根目录（即你的 `output` 文件夹），可以使用环境变量 `BASE_DIR`：

```bash
# 替换为你的输出目录路径
export BASE_DIR="/path/to/your/output"
```

3. 启动服务（开发模式）：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. API 说明（常用）：

- `GET /api/folders?path=rel/path` — 列出 `BASE_DIR/rel/path` 下的子文件夹和图片文件名
- `GET /api/image?path=rel/path/to/image.png` — 返回图片二进制流
- `GET /api/image?path=...&download=true` — 强制下载图片

注意：后端默认使用 `BASE_DIR` 环境变量作为根目录；如果未设置则使用启动目录（不推荐）。路径在后端会被解析并拒绝越界访问。

---

## 后端依赖与安装（详细）

建议在独立虚拟环境中安装后端依赖，步骤（在 `backend` 目录下）：

```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境（Unix / macOS）
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
# python -m venv .venv
# .\.venv\Scripts\Activate.ps1

# 升级 pip 并安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt
```

常见系统依赖（Debian/Ubuntu），用于确保 Pillow 能够处理常见图像格式及加速：

```bash
sudo apt update
sudo apt install -y build-essential libjpeg-dev zlib1g-dev libpng-dev libopenjp2-7 libtiff5 libwebp-dev libgl1-mesa-glx
```

说明：`requirements.txt` 已包含 `fastapi` 与 `uvicorn[standard]`。如果你希望后端直接进行图片处理（生成缩略图、转码等），可能还需要额外的 Python 包（例如 `Pillow`、`python-magic` 等），可以通过 `pip install Pillow` 添加。

如果你更倾向用 Docker，请告知我，我可以为后端生成一个简单的 `Dockerfile` 与 `docker-compose.yml` 示例。


## 前端（开发）运行方法

1. 进入前端目录并安装依赖：

```bash
cd frontend
npm install
```

2. 可选：设置后端地址（如果后端不在 `http://localhost:8000`）：在 `frontend` 下创建 `.env` 文件，写入：

```
VITE_API_BASE=http://your-backend-host:8000
```

3. 启动开发服务器：

```bash
npm run dev
```

4. 在浏览器打开 Vite 提供的地址（通常是 `http://localhost:5173`）。

提示：如果前后端同机并且你希望在前端使用相对 `/api` 转发以避免额外配置，可在 `vite.config.js` 中配置 `server.proxy` 指向后端（示例见下）。

---

## 在同级目录运行（前后端在同一台机器的同级目录）

假设项目结构如下：

```
project-root/
├─ backend/
├─ frontend/
```

推荐在一台机器上分别启动后端与前端进程（或在生产把前端 build 后由 Nginx 提供静态文件）。运行顺序不限，但请确保前端配置的 `VITE_API_BASE` 指向正在运行的后端地址（例如 `http://localhost:8000`）。

若希望通过 Vite 直接代理 API（开发便捷），在 `frontend/vite.config.js` 中添加：

```js
// vite.config.js (示例)
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

使用代理后可在前端代码中直接请求 `/api/...`，无需设置 `VITE_API_BASE`。

---

## 更换后端根目录（即切换 `output` 目录）

后端通过 `BASE_DIR` 环境变量确定根目录。更换方式有几种：

- 临时（当前 shell 会话）：

```bash
export BASE_DIR="/new/path/to/output"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- 永久（systemd 服务示例）：在 systemd unit 文件中设置 `Environment=BASE_DIR=/new/path`。

- Docker：在 `docker run -e BASE_DIR=/new/path ...` 或 `docker-compose.yml` 中设置环境变量，并把目录挂载到容器内。

注意：更改后端 `BASE_DIR` 后，前端仍使用相对路径（`path` 参数）访问；无需更改前端代码，除非后端地址或端口发生变化。

---

## 生产部署建议（简要）

- 后端：使用 ASGI 服务器（例如 `uvicorn` 或 `gunicorn` + Uvicorn worker），并在前面放置 Nginx 做反向代理与 TLS。
- 前端：运行 `npm run build` 后，将 `dist/` 中静态文件交给 Nginx 服务，或与后端一起由 Nginx 托管。
- 将 `BASE_DIR` 设置为图片所在目录的绝对路径，并确保 Nginx/后端进程有读取权限。

示例 Nginx 配置片段（反代后端并提供前端静态）：

```
server {
  listen 80;
  server_name your.domain;

  location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  location / {
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;
  }
}
```

---

## 常见问题与排查

- 无法查看图片：检查 `BASE_DIR` 是否正确，后端进程是否有读取权限。
- 前端请求失败（CORS）：确保后端启用了允许来自前端的 CORS，开发环境当前已允许所有来源。
- 图片不更新：确认 SD 生成器写入目录权限，或刷新前端页面，后端仅返回文件名，前端直接请求图片 URL。

---

## 我想要更多定制

- 若需缩略图支持、懒加载或按日期/模型分组视图，我可以继续帮你实现。

---

文件位置： [USER_MANUAL.md](USER_MANUAL.md)
