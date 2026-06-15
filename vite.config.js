import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'node:path'

// Static multi-page marketing site, deployed to GitHub Pages on the
// nectardocs.com apex (custom domain → base '/'). Each top-level page is a
// separate HTML entry so Vite emits clean /tos and /privacy outputs.
export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        index: resolve(import.meta.dirname, 'index.html'),
        tos: resolve(import.meta.dirname, 'tos.html'),
        privacy: resolve(import.meta.dirname, 'privacy.html'),
      },
    },
  },
})
