# Frontend (Vite + Vue)

运行步骤（开发）：

1. 安装依赖

```bash
cd frontend
npm install
```

2. 指定后端地址（可选，默认 `http://localhost:8000`）

在项目根创建 `.env`，写入：

```
VITE_API_BASE=http://localhost:8000
```

3. 启动开发服务器

```bash
npm run dev
```

然后打开浏览器访问 `http://localhost:5173`（vite 默认端口）。
# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).
