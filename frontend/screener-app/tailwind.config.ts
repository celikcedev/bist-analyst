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
        // Enhanced TradingView dark theme with vibrant accents
        'tv-dark': {
          bg: '#0D1117',           // Darker, richer background
          surface: '#161B22',      // Elevated surface
          card: '#1C2128',         // Card surface
          border: '#30363D',       // Subtle borders
          text: '#E6EDF3',         // Brighter text
          textMuted: '#8B949E',    // Muted text
          primary: '#2F81F7',      // Vibrant blue
          secondary: '#8957E5',    // Purple accent
          success: '#3FB950',      // Green
          warning: '#F0883E',      // Orange
          danger: '#F85149',       // Red
          info: '#58A6FF',         // Light blue
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #2F81F7 0%, #1E5FD9 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #8957E5 0%, #6E3FC0 100%)',
        'gradient-success': 'linear-gradient(135deg, #3FB950 0%, #2E8B40 100%)',
        'gradient-card': 'linear-gradient(135deg, rgba(47, 129, 247, 0.05) 0%, rgba(137, 87, 229, 0.05) 100%)',
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(47, 129, 247, 0.15)',
        'glow-md': '0 0 20px rgba(47, 129, 247, 0.2)',
        'glow-lg': '0 0 30px rgba(47, 129, 247, 0.25)',
      },
    },
  },
  plugins: [],
};
export default config;
