/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',  // Основной синий
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',  // Темный фон
          950: '#030712',  // Очень темный фон
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'gradient-x': 'gradient-x 3s ease infinite',
        'gradient-slow': 'gradient-slow 15s ease-in-out infinite',
        'gradient': 'gradient 6s ease infinite',
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'skeleton-pulse': 'skeleton-pulse 2s ease-in-out infinite',
        'skeleton-wave': 'skeleton-wave 1.5s ease-in-out infinite',
        'ai-glow': 'ai-glow 3s ease-in-out infinite',
        'ai-sparkle': 'ai-sparkle 2s linear infinite',
        'shimmer': 'shimmer 2s ease-in-out infinite',
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
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'gradient-x': {
          '0%, 100%': {
            'background-position': '0% 50%',
          },
          '50%': {
            'background-position': '100% 50%',
          },
        },
        'gradient-slow': {
          '0%, 100%': {
            'background-position': '0% 50%',
          },
          '25%': {
            'background-position': '100% 50%',
          },
          '50%': {
            'background-position': '50% 100%',
          },
          '75%': {
            'background-position': '0% 50%',
          },
        },
        fadeInUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.3)' },
          '100%': { boxShadow: '0 0 30px rgba(59, 130, 246, 0.6)' },
        },
        gradient: {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center',
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center',
          },
        },
        'skeleton-pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 }
        },
        'skeleton-wave': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' }
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' }
        },
        'ai-glow': {
          '0%, 100%': {
            filter: 'brightness(1) blur(0px)',
            transform: 'scale(1)'
          },
          '50%': {
            filter: 'brightness(1.2) blur(1px)',
            transform: 'scale(1.05)'
          }
        },
        'ai-sparkle': {
          '0%': {
            transform: 'rotate(0deg) scale(1)',
            opacity: 1
          },
          '25%': {
            transform: 'rotate(90deg) scale(1.1)',
            opacity: 0.8
          },
          '50%': {
            transform: 'rotate(180deg) scale(1.2)',
            opacity: 1
          },
          '75%': {
            transform: 'rotate(270deg) scale(1.1)',
            opacity: 0.8
          },
          '100%': {
            transform: 'rotate(360deg) scale(1)',
            opacity: 1
          }
        },
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'strong': '0 10px 40px -10px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.6)',
        'glow-sm': '0 0 20px rgba(59, 130, 246, 0.3)',
        'glow-md': '0 0 30px rgba(59, 130, 246, 0.5)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
