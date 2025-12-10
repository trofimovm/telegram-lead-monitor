Design System Guide

> Инструкция для Claude Code по воспроизведению дизайн-системы в новых проектах.
> Этот документ содержит все необходимые спецификации для создания идентичного визуального стиля.

---

## 1. Технологический стек

```
Frontend:     React 18 + TypeScript
Стилизация:   Tailwind CSS 3.3+
Компоненты:   Headless UI (unstyled, accessible)
Иконки:       Heroicons React 2.0
Build:        Vite или Create React App (craco)
```

### Установка зависимостей

```bash
npm install tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react
```

---

## 2. Tailwind Config

### 2.1 Полный файл tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
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
```

---

## 3. Базовые CSS стили (index.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import './styles/transitions.css';

/* ===========================================
   БАЗОВЫЕ СТИЛИ
   =========================================== */

/* Фикс overscroll для macOS/iOS - белый фон при оверскролле */
html {
  background-color: rgb(255, 255, 255);
}

html.dark {
  background-color: rgb(17, 24, 39); /* gray-900 */
}

body {
  margin: 0;
  background-color: rgb(255, 255, 255);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body.dark {
  background-color: rgb(17, 24, 39);
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* ===========================================
   MOBILE TOUCH TARGETS (WCAG AA)
   =========================================== */

/* Минимальный размер 44x44px для доступности */
.touch-target-44 {
  min-height: 44px;
  min-width: 44px;
}

/* Основные интерактивные элементы */
.touch-target-primary {
  min-height: 44px;
  padding: 0.75rem 1rem;
}

/* Компактные вторичные элементы */
.touch-target-compact {
  min-height: 36px;
  padding: 0.5rem 0.75rem;
}

/* На мобильных увеличиваем touch targets до 48px */
@media (max-width: 640px) {
  .touch-target-44 {
    min-height: 48px;
    min-width: 48px;
  }

  .touch-target-primary {
    min-height: 48px;
    padding: 0.875rem 1.25rem;
  }

  .touch-target-compact {
    min-height: 40px;
    padding: 0.625rem 1rem;
  }
}

/* ===========================================
   SCROLLBAR СТИЛИ
   =========================================== */

/* Скрытие scrollbar для каруселей */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Кастомный scrollbar - светлая тема */
* {
  scrollbar-width: thin;
  scrollbar-color: rgb(209, 213, 219) rgb(243, 244, 246); /* gray-300 thumb, gray-100 track */
}

*::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

*::-webkit-scrollbar-track {
  background: rgb(243, 244, 246); /* gray-100 */
  border-radius: 6px;
}

*::-webkit-scrollbar-thumb {
  background: rgb(209, 213, 219); /* gray-300 */
  border-radius: 6px;
  border: 2px solid rgb(243, 244, 246); /* padding effect */
}

*::-webkit-scrollbar-thumb:hover {
  background: rgb(156, 163, 175); /* gray-400 */
}

/* Кастомный scrollbar - темная тема */
.dark * {
  scrollbar-color: rgb(75, 85, 99) rgb(31, 41, 55); /* gray-600 thumb, gray-800 track */
}

.dark *::-webkit-scrollbar-track {
  background: rgb(31, 41, 55); /* gray-800 */
}

.dark *::-webkit-scrollbar-thumb {
  background: rgb(75, 85, 99); /* gray-600 */
  border: 2px solid rgb(31, 41, 55); /* gray-800 */
}

.dark *::-webkit-scrollbar-thumb:hover {
  background: rgb(107, 114, 128); /* gray-500 */
}
```

---

## 4. CSS Transitions (styles/transitions.css)

```css
/* ===========================================
   PAGE TRANSITIONS
   =========================================== */

/* Slide transitions для страниц */
.page-slide-enter {
  transform: translateX(100%);
}

.page-slide-enter-active {
  transform: translateX(0);
  transition: transform 300ms ease-out;
}

.page-slide-exit {
  transform: translateX(0);
}

.page-slide-exit-active {
  transform: translateX(-100%);
  transition: transform 300ms ease-out;
}

/* Fade transitions */
.page-fade-enter {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}

.page-fade-exit {
  opacity: 1;
  transform: translateY(0);
}

.page-fade-exit-active {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}

/* ===========================================
   MODAL TRANSITIONS
   =========================================== */

/* Modal slide up from bottom (mobile) */
.modal-slide-up-enter {
  transform: translateY(100%);
}

.modal-slide-up-enter-active {
  transform: translateY(0);
  transition: transform 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.modal-slide-up-exit {
  transform: translateY(0);
}

.modal-slide-up-exit-active {
  transform: translateY(100%);
  transition: transform 250ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* ===========================================
   BOTTOM SHEET
   =========================================== */

/* Overlay */
.bottom-sheet-overlay-enter {
  opacity: 0;
}

.bottom-sheet-overlay-enter-active {
  opacity: 1;
  transition: opacity 300ms ease-out;
}

.bottom-sheet-overlay-exit {
  opacity: 1;
}

.bottom-sheet-overlay-exit-active {
  opacity: 0;
  transition: opacity 200ms ease-in;
}

/* Panel */
.bottom-sheet-panel-enter {
  opacity: 0;
  transform: translateY(100%);
}

.bottom-sheet-panel-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 300ms ease-out, transform 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.bottom-sheet-panel-exit {
  opacity: 1;
  transform: translateY(0);
}

.bottom-sheet-panel-exit-active {
  opacity: 0;
  transform: translateY(100%);
  transition: opacity 200ms ease-in, transform 200ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* ===========================================
   LOADING STATES
   =========================================== */

.skeleton-pulse {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* ===========================================
   INTERACTIVE FEEDBACK
   =========================================== */

/* Pull to refresh */
.pull-to-refresh-indicator {
  transform: translateY(-100%);
  transition: transform 0.3s ease-out;
}

.pull-to-refresh-indicator.visible {
  transform: translateY(0);
}

/* Haptic feedback simulation */
.haptic-feedback {
  animation: haptic-feedback 150ms ease-out;
}

@keyframes haptic-feedback {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

/* Touch feedback для кнопок */
.touch-feedback:active {
  transform: scale(0.98);
  transition: transform 0.1s ease-out;
}

/* ===========================================
   MOBILE SCROLLING
   =========================================== */

@media (max-width: 640px) {
  html {
    scroll-behavior: smooth;
  }

  /* iOS momentum scrolling */
  .overflow-scroll {
    -webkit-overflow-scrolling: touch;
  }
}
```

---

## 5. UI Component Patterns

### 5.1 Кнопки

```tsx
// ==========================================
// PRIMARY CTA BUTTON (gradient)
// ==========================================
<button className="inline-flex items-center px-8 py-4 text-lg font-medium text-white
  bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg
  hover:shadow-xl transition-all duration-300 hover:scale-105
  focus:outline-none focus:ring-2 focus:ring-primary-500/50">
  <span>Get Started</span>
  <ArrowRightIcon className="ml-2 w-5 h-5" />
</button>

// ==========================================
// SECONDARY BUTTON
// ==========================================
<button className="inline-flex items-center px-8 py-4 text-lg font-medium
  text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800
  border border-gray-300 dark:border-gray-700 rounded-lg
  hover:shadow-lg transition-all duration-300
  focus:outline-none focus:ring-2 focus:ring-gray-500/50">
  Learn More
</button>

// ==========================================
// PRIMARY SOLID BUTTON (forms)
// ==========================================
<button className="w-full bg-gradient-to-r from-primary-500 to-primary-600
  hover:from-primary-600 hover:to-primary-700
  disabled:from-gray-400 disabled:to-gray-500
  text-white font-semibold py-3 px-6 rounded-xl
  shadow-lg hover:shadow-glow-sm disabled:shadow-none
  transform hover:scale-[1.02] disabled:scale-100
  transition-all duration-200
  focus:outline-none focus:ring-2 focus:ring-primary-500/50
  disabled:cursor-not-allowed">
  Submit
</button>

// ==========================================
// ICON BUTTON
// ==========================================
<button className="p-2 text-gray-500 dark:text-gray-400
  hover:text-gray-700 dark:hover:text-gray-200
  hover:bg-gray-100 dark:hover:bg-gray-700
  rounded-lg transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-primary-500/50">
  <CogIcon className="w-5 h-5" />
</button>

// ==========================================
// DANGER BUTTON
// ==========================================
<button className="px-4 py-2 bg-red-600 hover:bg-red-700
  text-white font-medium rounded-lg
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-red-500/50">
  Delete
</button>
```

### 5.2 Инпуты

```tsx
// ==========================================
// TEXT INPUT WITH ICON
// ==========================================
<div className="relative">
  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
    <EnvelopeIcon className="h-5 w-5 text-gray-400" />
  </div>
  <input
    type="email"
    className="pl-10 block w-full px-4 py-3
      bg-white/90 dark:bg-gray-800/90
      border border-gray-200 dark:border-gray-600
      rounded-xl text-gray-900 dark:text-white
      placeholder-gray-500 dark:placeholder-gray-400
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      transition-all duration-200
      hover:bg-white dark:hover:bg-gray-800"
    placeholder="Email address"
  />
</div>

// ==========================================
// SIMPLE INPUT
// ==========================================
<input
  type="text"
  className="block w-full px-4 py-3
    bg-white dark:bg-gray-800
    border border-gray-300 dark:border-gray-600
    rounded-lg text-gray-900 dark:text-white
    placeholder-gray-500 dark:placeholder-gray-400
    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
    transition-colors duration-200"
  placeholder="Enter text..."
/>

// ==========================================
// TEXTAREA
// ==========================================
<textarea
  rows={4}
  className="block w-full px-4 py-3
    bg-white dark:bg-gray-800
    border border-gray-300 dark:border-gray-600
    rounded-lg text-gray-900 dark:text-white
    placeholder-gray-500 dark:placeholder-gray-400
    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
    resize-none transition-colors duration-200"
  placeholder="Enter description..."
/>

// ==========================================
// SELECT
// ==========================================
<select className="block w-full px-4 py-3
  bg-white dark:bg-gray-800
  border border-gray-300 dark:border-gray-600
  rounded-lg text-gray-900 dark:text-white
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
  transition-colors duration-200">
  <option>Option 1</option>
  <option>Option 2</option>
</select>
```

### 5.3 Карточки

```tsx
// ==========================================
// FEATURE CARD С BLUR-ФОНОМ
// ==========================================
<div className="group relative h-full">
  {/* Blur gradient background */}
  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600
    rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity" />

  {/* Card content */}
  <div className="relative bg-white dark:bg-gray-800 p-8 rounded-2xl
    shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1
    h-full flex flex-col border border-gray-200 dark:border-gray-700">

    {/* Icon */}
    <div className="w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600
      rounded-xl flex items-center justify-center mb-6">
      <SparklesIcon className="w-8 h-8 text-white" />
    </div>

    <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
      Feature Title
    </h3>
    <p className="text-gray-600 dark:text-gray-400 flex-grow">
      Feature description goes here with details about the functionality.
    </p>
  </div>
</div>

// ==========================================
// SIMPLE CARD
// ==========================================
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm
  border border-gray-200 dark:border-gray-700 overflow-hidden">

  {/* Header */}
  <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900/50
    border-b border-gray-200 dark:border-gray-700">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
      Card Title
    </h3>
  </div>

  {/* Content */}
  <div className="p-6">
    <p className="text-gray-600 dark:text-gray-400">
      Card content goes here.
    </p>
  </div>
</div>

// ==========================================
// STATS CARD
// ==========================================
<div className="bg-white dark:bg-gray-800 rounded-xl p-6
  border border-gray-200 dark:border-gray-700 shadow-soft">
  <div className="flex items-center">
    <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
      <ChartBarIcon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
    </div>
    <div className="ml-4">
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Users</p>
      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">2,543</p>
    </div>
  </div>
</div>
```

### 5.4 Модальные окна

```tsx
// ==========================================
// MODAL DIALOG
// ==========================================
<div className="fixed inset-0 z-50 overflow-y-auto">
  {/* Backdrop */}
  <div className="fixed inset-0 bg-gray-500 dark:bg-gray-900
    bg-opacity-75 dark:bg-opacity-75 transition-opacity" />

  {/* Dialog container */}
  <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">

    {/* Dialog panel */}
    <div className="relative transform overflow-hidden rounded-lg
      bg-white dark:bg-gray-800 px-4 pb-4 pt-5 text-left
      shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">

      {/* Close button */}
      <div className="absolute right-0 top-0 pr-4 pt-4">
        <button className="rounded-md text-gray-400 hover:text-gray-500
          dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500">
          <XMarkIcon className="h-6 w-6" />
        </button>
      </div>

      {/* Content */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Modal Title
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Modal content goes here.
        </p>
      </div>

      {/* Actions */}
      <div className="mt-6 flex justify-end gap-3">
        <button className="px-4 py-2 text-gray-700 dark:text-gray-300
          hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
          Cancel
        </button>
        <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700
          text-white rounded-lg transition-colors">
          Confirm
        </button>
      </div>
    </div>
  </div>
</div>
```

### 5.5 Glassmorphism

```tsx
// ==========================================
// GLASS CARD (Auth forms, special sections)
// ==========================================
<div className="bg-white/70 dark:bg-gray-800/70
  backdrop-blur-md
  shadow-glass dark:shadow-glass-dark
  rounded-2xl
  border border-white/20 dark:border-gray-700/30
  p-8">
  Content with glass effect
</div>

// ==========================================
// GLASS NAVIGATION (on scroll)
// ==========================================
<nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
  scrolled
    ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-lg'
    : 'bg-transparent'
}`}>
  Navigation content
</nav>
```

---

## 6. Градиенты

### 6.1 Основные градиенты

```
Primary CTA:        from-blue-600 to-purple-600
Secondary CTA:      from-purple-600 to-pink-600
Hero text:          from-blue-600 via-purple-600 to-pink-600

Feature gradients:
  Feature 1:        from-blue-600 to-purple-600
  Feature 2:        from-purple-600 to-pink-600
  Feature 3:        from-pink-600 to-orange-600
  Feature 4:        from-green-600 to-teal-600
  Feature 5:        from-indigo-600 to-blue-600
  Feature 6:        from-yellow-600 to-red-600
```

### 6.2 Animated Gradient Text

```tsx
<span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600
  bg-clip-text text-transparent animate-gradient"
  style={{ backgroundSize: '200% auto' }}>
  Animated Gradient Text
</span>
```

### 6.3 Gradient Icon Container

```tsx
<div className="w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600
  rounded-xl flex items-center justify-center">
  <IconComponent className="w-8 h-8 text-white" />
</div>
```

---

## 7. Типографика

### 7.1 Заголовки

```tsx
// H1 - Hero (Landing pages)
<h1 className="text-5xl sm:text-6xl md:text-7xl font-bold leading-tight
  text-gray-900 dark:text-gray-100">
  Hero Title
</h1>

// H2 - Section headers
<h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
  Section Title
</h2>

// H3 - Subsection / Card titles
<h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3">
  Card Title
</h3>

// H4 - Item titles
<h4 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
  Item Title
</h4>

// H5 - Small titles
<h5 className="text-lg font-bold text-gray-900 dark:text-gray-100">
  Small Title
</h5>
```

### 7.2 Текст

```tsx
// Body text
<p className="text-base text-gray-600 dark:text-gray-400">
  Regular paragraph text
</p>

// Large text (subtitles)
<p className="text-xl text-gray-600 dark:text-gray-400">
  Large subtitle text
</p>

// Small text
<p className="text-sm text-gray-700 dark:text-gray-300">
  Small text
</p>

// Extra small (labels, badges)
<span className="text-xs text-gray-700 dark:text-gray-300">
  Label text
</span>
```

### 7.3 Цвета текста

| Назначение | Light Mode | Dark Mode |
|------------|-----------|-----------|
| Primary | `text-gray-900` | `dark:text-gray-100` |
| Secondary | `text-gray-700` | `dark:text-gray-300` |
| Tertiary | `text-gray-600` | `dark:text-gray-400` |
| Muted | `text-gray-400` | `dark:text-gray-500` |
| Link | `text-primary-600` | `dark:text-primary-400` |

---

## 8. Spacing & Layout

### 8.1 Container

```tsx
// Max-width container
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  Content
</div>
```

### 8.2 Секции

```tsx
// Standard section
<section className="py-20 px-4 sm:px-6 lg:px-8">
  <div className="max-w-7xl mx-auto">
    Content
  </div>
</section>

// Section with background
<section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
  <div className="max-w-7xl mx-auto">
    Content
  </div>
</section>
```

### 8.3 Grid система

```tsx
// 2 columns
<div className="grid md:grid-cols-2 gap-8">

// 3 columns
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">

// 4 columns
<div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">

// Auto-fit responsive
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
```

### 8.4 Spacing Guidelines

| Элемент | Значение | Tailwind |
|---------|----------|----------|
| Между элементами в группе | 8-12px | `gap-2`, `gap-3` |
| Padding карточки (small) | 24px | `p-6` |
| Padding карточки (large) | 32px | `p-8` |
| Margin заголовок → контент | 12-24px | `mb-3`, `mb-4`, `mb-6` |
| Между секциями | 48-64px | `mb-12`, `mb-16` |
| Section padding | 80px | `py-20` |

---

## 9. Border Radius

| Элемент | Размер | Tailwind |
|---------|--------|----------|
| Мелкие элементы | 6px | `rounded-md` |
| Кнопки, инпуты | 8px | `rounded-lg` |
| Карточки | 12px | `rounded-xl` |
| Большие блоки | 16px | `rounded-2xl` |
| Pills, badges | full | `rounded-full` |

---

## 10. Декоративные элементы

### 10.1 Blob анимации (фон)

```tsx
{/* Декоративные blob-элементы для фона */}
<div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500
  rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
<div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500
  rounded-full mix-blend-multiply filter blur-3xl opacity-20
  animate-blob animation-delay-2000" />
<div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500
  rounded-full mix-blend-multiply filter blur-3xl opacity-20
  animate-blob animation-delay-4000" />

{/* CSS в index.css или inline style */}
<style jsx>{`
  @keyframes blob {
    0% { transform: translate(0px, 0px) scale(1); }
    33% { transform: translate(30px, -50px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
    100% { transform: translate(0px, 0px) scale(1); }
  }
  .animate-blob { animation: blob 7s infinite; }
  .animation-delay-2000 { animation-delay: 2s; }
  .animation-delay-4000 { animation-delay: 4s; }
`}</style>
```

### 10.2 Gradient blur background

```tsx
{/* За карточкой или секцией */}
<div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600
  blur-2xl opacity-20" />
```

---

## 11. Темная тема

### 11.1 ThemeContext реализация

```tsx
// contexts/ThemeContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('theme') as Theme
    return saved || 'system'
  })

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const root = document.documentElement

    const applyTheme = (newTheme: 'light' | 'dark') => {
      root.classList.remove('light', 'dark')
      root.classList.add(newTheme)
      setResolvedTheme(newTheme)
    }

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      applyTheme(mediaQuery.matches ? 'dark' : 'light')

      const handler = (e: MediaQueryListEvent) => applyTheme(e.matches ? 'dark' : 'light')
      mediaQuery.addEventListener('change', handler)
      return () => mediaQuery.removeEventListener('change', handler)
    } else {
      applyTheme(theme)
    }
  }, [theme])

  useEffect(() => {
    localStorage.setItem('theme', theme)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) throw new Error('useTheme must be used within ThemeProvider')
  return context
}
```

### 11.2 Паттерны использования

```tsx
// ВСЕГДА указывай оба варианта:
className="bg-white dark:bg-gray-800"
className="text-gray-900 dark:text-gray-100"
className="border-gray-200 dark:border-gray-700"
className="hover:bg-gray-50 dark:hover:bg-gray-700"
className="placeholder-gray-500 dark:placeholder-gray-400"
```

---

## 12. Иконки

### 12.1 Heroicons

```tsx
// Outline icons (default)
import { UserIcon, HomeIcon, CogIcon } from '@heroicons/react/24/outline'

// Solid icons (active states)
import { UserIcon as UserIconSolid } from '@heroicons/react/24/solid'

// Mini icons (small UI)
import { ChevronDownIcon } from '@heroicons/react/20/solid'
```

### 12.2 Размеры

| Назначение | Размер | Tailwind |
|------------|--------|----------|
| Inline с текстом | 20px | `w-5 h-5` |
| Кнопки | 24px | `w-6 h-6` |
| Medium | 32px | `w-8 h-8` |
| Large | 40px | `w-10 h-10` |
| Feature icons | 48px | `w-12 h-12` |

---

## 13. Skeleton Loaders

```tsx
// ==========================================
// BASE SKELETON
// ==========================================
<div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded-md h-4 w-full" />

// ==========================================
// CARD SKELETON
// ==========================================
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm
  border border-gray-200 dark:border-gray-700 p-6">

  {/* Header */}
  <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-6 w-2/3 mb-4" />

  {/* Content lines */}
  <div className="space-y-2">
    <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-4 w-full" />
    <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-4 w-full" />
    <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-4 w-3/4" />
  </div>
</div>

// ==========================================
// TABLE ROW SKELETON
// ==========================================
<tr className="border-b border-gray-200 dark:border-gray-700">
  <td className="py-4 px-4">
    <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-4 w-24" />
  </td>
  <td className="py-4 px-4">
    <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-4 w-32" />
  </td>
  <td className="py-4 px-4">
    <div className="bg-gray-200 dark:bg-gray-700 animate-skeleton-pulse rounded h-4 w-20" />
  </td>
</tr>
```

---

## 14. Навигация

### 14.1 Sticky Navigation с blur при скролле

```tsx
const [scrolled, setScrolled] = useState(false)

useEffect(() => {
  const handleScroll = () => setScrolled(window.scrollY > 20)
  window.addEventListener('scroll', handleScroll)
  return () => window.removeEventListener('scroll', handleScroll)
}, [])

<nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
  scrolled
    ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-lg'
    : 'bg-transparent'
}`}>
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {/* Nav content */}
  </div>
</nav>
```

---

## 15. Breakpoints

| Breakpoint | Min Width | Описание |
|------------|-----------|----------|
| `sm:` | 640px | Большие телефоны |
| `md:` | 768px | Планшеты |
| `lg:` | 1024px | Ноутбуки |
| `xl:` | 1280px | Десктопы |
| `2xl:` | 1536px | Большие экраны |

---

## 16. Accessibility

### Touch Targets
- Минимум 44x44px (48x48px на мобильных)
- Используй классы `.touch-target-44`, `.touch-target-primary`

### Focus States
```tsx
focus:outline-none focus:ring-2 focus:ring-primary-500
focus:ring-primary-500/50 // с прозрачностью
```

### Screen Readers
```tsx
<span className="sr-only">Описание для screen reader</span>
```

### ARIA
```tsx
<button aria-label="Close modal" aria-expanded={isOpen}>
<nav aria-label="Main navigation">
<div role="dialog" aria-modal="true">
```

---

## 17. Чек-лист для нового проекта

### Настройка

- [ ] Установить Tailwind CSS 3.3+
- [ ] Скопировать `tailwind.config.js` с цветами и анимациями
- [ ] Создать `index.css` с базовыми стилями и scrollbar
- [ ] Создать `styles/transitions.css` для переходов
- [ ] Установить `@headlessui/react` и `@heroicons/react`

### Компоненты

- [ ] Создать `ThemeContext` для dark mode
- [ ] Создать `ToastContext` для уведомлений
- [ ] Создать Layout компонент
- [ ] Настроить path alias `@/` в tsconfig

### Стилизация

- [ ] Использовать паттерны кнопок из этого гайда
- [ ] Применять `dark:` классы везде
- [ ] Следовать spacing guidelines
- [ ] Тестировать touch targets на мобильных

### Проверка

- [ ] Проверить dark/light mode переключение
- [ ] Проверить все hover/focus состояния
- [ ] Проверить responsive на всех breakpoints
- [ ] Проверить accessibility (keyboard navigation, screen readers)

---

