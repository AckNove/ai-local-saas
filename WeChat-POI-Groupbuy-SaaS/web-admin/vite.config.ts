import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Web 管理后台构建配置（React 18 + Vite 5）。
// 后端 API 默认地址通过 .env 的 VITE_API_BASE 覆盖。
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
