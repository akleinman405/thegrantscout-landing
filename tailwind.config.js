/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1e3a5f',
          dark: '#152b47',
          light: '#2d5a8e',
        },
        accent: {
          DEFAULT: '#d4a853',
          dark: '#b8923d',
          light: '#e6c680',
        },
        charcoal: '#2C3E50',
        'gray-medium': '#6C757D',
        success: '#28A745',
        error: '#DC3545',
        info: '#17A2B8',
        warning: '#FFC107',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        heading: ['var(--font-raleway)', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      boxShadow: {
        'card': '0 2px 12px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 8px 24px rgba(0, 0, 0, 0.12)',
        'button': '0 2px 8px rgba(212, 168, 83, 0.25)',
        'button-hover': '0 4px 12px rgba(212, 168, 83, 0.35)',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
      },
    },
  },
  plugins: [],
}
