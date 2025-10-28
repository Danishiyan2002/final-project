export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#6b21a8', dark: '#4c1d95' },
        accent: '#14b8a6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Segoe UI', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
