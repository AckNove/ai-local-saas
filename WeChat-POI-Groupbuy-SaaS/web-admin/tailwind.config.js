/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#07c160', // 微信绿
          dark: '#06a050',
        },
      },
    },
  },
  plugins: [],
}
