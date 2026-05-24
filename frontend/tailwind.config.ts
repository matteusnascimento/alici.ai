import type { Config } from 'tailwindcss';

const accentColor = 'rgb(var(--accent-rgb) / <alpha-value>)';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}', '../tests/frontend/**/*.tsx'],
  theme: {
    extend: {
      colors: {
        ink: 'rgb(var(--axi-ink-rgb) / <alpha-value>)',
        storm: 'rgb(var(--axi-storm-rgb) / <alpha-value>)',
        cyan: {
          DEFAULT: accentColor,
          50: accentColor,
          100: accentColor,
          200: accentColor,
          300: accentColor,
          400: accentColor,
          500: accentColor,
          600: accentColor,
          700: accentColor,
          800: accentColor,
          900: accentColor,
          950: accentColor,
        },
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
