/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'scribe-bg': '#fdfbf7', // Calming off-white
                'scribe-primary': '#4a90e2',
                'scribe-secondary': '#8b5cf6',
            },
            fontFamily: {
                'sans': ['Inter', 'system-ui', 'sans-serif'],
                'dyslexic': ['OpenDyslexic', 'Comic Sans MS', 'sans-serif'], // For dyslexic users
            }
        },
    },
    plugins: [],
}
