/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        up: '#ef4444',
        down: '#22c55e',
        zone: {
          undervalued: '#22c55e',
          neutral: '#eab308',
          overvalued: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
