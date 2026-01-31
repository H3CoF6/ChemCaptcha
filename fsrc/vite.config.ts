import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      // 这里的配置是为了让前端能访问 Python 后端，解决跨域问题
      '/api': {
        target: 'http://127.0.0.1:8000', // Python 服务的地址
        changeOrigin: true,
      }
    }
  }
})