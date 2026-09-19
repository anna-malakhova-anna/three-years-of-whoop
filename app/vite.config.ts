import { fileURLToPath, URL } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The pipeline writes its JSON output to ../public/data (repo root), so the
// data lives in one place regardless of whether it's read by pipeline
// consumers or served by this app. `base: './'` keeps asset/data URLs
// relative, so the build works unmodified under a GitHub Pages project path
// (username.github.io/repo/) without hardcoding the repo name here.
export default defineConfig({
  plugins: [react()],
  base: './',
  publicDir: fileURLToPath(new URL('../public', import.meta.url)),
})
