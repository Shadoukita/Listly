import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  // vue-i18n compiles translation strings to functions at runtime. By default
  // it does that with `new Function()`, which the app's Content-Security-Policy
  // (script-src 'self', set in backend/app.py) blocks — that left the app on a
  // black screen. Turning JIT compilation on switches it to an AST interpreter
  // that needs no code generation. Both flags must be real booleans or
  // vue-i18n's own bootstrap resets them to false.
  define: {
    __INTLIFY_JIT_COMPILATION__: true,
    __INTLIFY_DROP_MESSAGE_COMPILER__: false,
  },
  build: {
    // Vite's modulepreload polyfill is injected as an INLINE <script>, which
    // would force 'unsafe-inline' into the Content-Security-Policy set in
    // backend/app.py. It is only a preload optimisation, so drop it and keep
    // script-src strict.
    modulePreload: { polyfill: false },
  },
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: false,   // use our public/site.webmanifest
      includeAssets: ['favicon.svg', 'favicon-*.png', 'apple-touch-icon.png'],
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 300 },
              networkTimeoutSeconds: 10,
            },
          },
        ],
      },
    }),
  ],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/uploads': 'http://localhost:5000',
    },
  },
})
