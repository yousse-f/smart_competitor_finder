/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Smart Competitor Finder SaaS Brand Palette
        background: {
          DEFAULT: "#0D1117",
          secondary: "#1E293B",
        },
        surface: {
          DEFAULT: "#1E293B",
          hover: "#334155",
          active: "#475569",
        },
        primary: {
          50: "#E6F9FF",
          100: "#CCF3FF", 
          200: "#99E7FF",
          300: "#66DBFF",
          400: "#33CFFF",
          500: "#00B4D8",
          600: "#0090AC",
          700: "#006C81",
          800: "#004855",
          900: "#00242A",
        },
        secondary: {
          50: "#E6F8FF",
          100: "#CCF1FF",
          200: "#99E3FF", 
          300: "#66D5FF",
          400: "#38BDF8",
          500: "#0EA5E9",
          600: "#0284C7",
          700: "#0369A1",
          800: "#075985",
          900: "#0C4A6E",
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
