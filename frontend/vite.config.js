import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'

// Builds the SPA into the app and emits the served HTML page.
// Output: ../public/frontend       -> served at /assets/compliance_manager/frontend/
// Page:   ../www/compliance.html    -> served at /compliance
export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true, // dev: proxy /api, /assets, /app... to the Frappe server
      lucideIcons: true, // required: frappe-ui's own components import ~icons/lucide/*
      jinjaBootData: true, // inject boot info + csrf_token into the page
      frontendRoute: '/compliance',
      buildConfig: {
        outDir: path.resolve(__dirname, '../compliance_manager/public/frontend'),
        indexHtmlPath: path.resolve(__dirname, '../compliance_manager/www/compliance.html'),
        baseUrl: '/assets/compliance_manager/frontend/',
        emptyOutDir: true,
        sourcemap: false,
      },
    }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  optimizeDeps: {
    include: ['feather-icons'],
  },
})
