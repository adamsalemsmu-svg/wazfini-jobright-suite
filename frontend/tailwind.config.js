/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef6ff",
          100: "#d9eaff",
          200: "#b7d5ff",
          300: "#8fbcff",
          400: "#5e9bff",
          500: "#397fff",
          600: "#1f63e6",
          700: "#184db4",
          800: "#143f8e",
          900: "#123671",
          950: "#0c2347",
        },
      },
    },
  },
  plugins: [],
}
