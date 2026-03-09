import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#f6f0e5",
        ink: "#121212",
        ember: "#c8572a",
        brass: "#ac7f2a",
        spruce: "#0d5d56",
        mist: "#dde5dd",
      },
      boxShadow: {
        panel: "0 20px 60px rgba(18, 18, 18, 0.12)",
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgba(18,18,18,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(18,18,18,0.06) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
} satisfies Config;

