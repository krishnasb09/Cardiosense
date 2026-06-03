export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          ink: "#112031",
          blue: "#2563eb",
          cyan: "#0891b2",
          teal: "#0f766e",
          mint: "#d7f7ec",
          amber: "#f59e0b",
          rose: "#e11d48",
          cloud: "#f5f8fb"
        }
      },
      boxShadow: {
        soft: "0 18px 48px rgba(17, 32, 49, 0.08)"
      }
    }
  },
  plugins: [],
};
