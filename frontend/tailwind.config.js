/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
      colors: {
        // Risk rating colors
        risk: {
          low: {
            light: '#22c55e',    // green-500
            dark: '#4ade80',     // green-400
          },
          medium: {
            light: '#f59e0b',    // amber-500
            dark: '#fbbf24',     // amber-400
          },
          high: {
            light: '#ef4444',    // red-500
            dark: '#f87171',     // red-400
          },
        },
      },
      spacing: {
        // Touch-friendly spacing for mobile
        'touch': '44px',
      },
    },
  },
  plugins: [],
}
