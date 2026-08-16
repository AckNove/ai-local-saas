import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// 前端构建配置：
// - build.outDir = dist，产物由后端 FastAPI 以 StaticFiles 托管
// - dev 时把 /api 代理到后端（http://127.0.0.1:8000），便于联调
// - 配置 @ 别名指向 src，便于模块化引用（与 tsconfig paths 对齐）
// 生产部署时前端与后端同源（FastAPI 同时托管 /api 与前端），无需跨域。
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
