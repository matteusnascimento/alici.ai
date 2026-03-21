import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}', '../tests/frontend/**/*.tsx'],
  theme: {
    extend: {
      colors: {
        ink: '#08111f',
        storm: '#11243b',
        cyan: '#6ee7f9',
        sand: '#f3ece1',
        gold: '#d8b56b',
        coral: '#ff8f70',
      },
      boxShadow: {
        soft: '0 20px 60px rgba(8, 17, 31, 0.12)',
      },
      fontFamily: {
        display: ['Sora', 'sans-serif'],
        body: ['Manrope', 'sans-serif'],
      },
      backgroundImage: {
        grid: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.09) 1px, transparent 0)',
      },
    },
  },
  plugins: [],
} satisfies Config;
