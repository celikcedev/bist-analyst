import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // TradingView dark theme colors
        'tv-dark': {
          bg: '#131722',
          surface: '#1E222D',
          border: '#2A2E39',
          text: '#D1D4DC',
          textMuted: '#787B86',
          primary: '#2962FF',
          success: '#089981',
          danger: '#F23645',
        },
      },
    },
  },
  plugins: [],
};
export default config;
