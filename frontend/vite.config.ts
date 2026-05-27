import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/account': 'http://127.0.0.1:8000',
      '/billing': 'http://127.0.0.1:8000',
      '/business': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/integrations': 'http://127.0.0.1:8000',
      '/jobs': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000',
      '/omnichannel': 'http://127.0.0.1:8000',
      '/studio': 'http://127.0.0.1:8000',
      '/webhooks': 'http://127.0.0.1:8000',
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['lucide-react'],
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    globals: true,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    poolOptions: {
      threads: {
        minThreads: 1,
        maxThreads: 1,
      },
    },
  },
});
