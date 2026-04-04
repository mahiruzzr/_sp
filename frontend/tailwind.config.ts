import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#f4efe6",
        ink: "#161616",
        accent: "#0f766e",
        accentSoft: "#d9f3ef",
        panel: "#fffaf1",
        border: "#d8cfc2",
      },
      boxShadow: {
        paper: "0 24px 80px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;

