/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef6ff",
          100: "#d9eaff",
          200: "#bcdcff",
          300: "#8ec6ff",
          400: "#59a6ff",
          500: "#2f84ff",
          600: "#1763f5",
          700: "#114de1",
          800: "#143fb6",
          900: "#16388f",
        },
      },
    },
  },
  plugins: [],
};
