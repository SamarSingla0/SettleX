/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#0f172a",
          primary: "#047857",
          primaryHover: "#065f46",
          emerald: "#10b981",
          emeraldLight: "#ecfdf5",
          warning: "#f59e0b",
          danger: "#ef4444",
          dangerLight: "#fef2f2",
          grayBg: "#f8f9fb",
          cardBorder: "#e2e8f0",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}