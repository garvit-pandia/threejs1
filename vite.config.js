import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5180,
    strictPort: true,
    watch: { usePolling: true },
  },
  preview: {
    port: 5181,
    strictPort: true,
  },
  build: { target: 'es2022' },
});
