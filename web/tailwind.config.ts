import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: "#0f1115", light: "#1a1d24", lighter: "#242832" },
        accent: { DEFAULT: "#3b82f6", hover: "#2563eb" },
      },
    },
  },
  plugins: [],
};
export default config;
