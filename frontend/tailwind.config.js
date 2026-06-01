/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#090d16",       // Deep Space Black/Blue
          card: "#111827",     // Gray-900
          border: "#1f2937",   // Gray-800
          text: "#f3f4f6",     // Gray-100
          muted: "#9ca3af",    // Gray-400
          primary: "#6366f1",  // Indigo-500
          secondary: "#0ea5e9",// Sky-500
          critical: "#f43f5e", // Rose-500
          high: "#f97316",     // Orange-500
          medium: "#eab308",   // Yellow-500
          low: "#3b82f6"       // Blue-500
        }
      }
    },
  },
  plugins: [],
}
