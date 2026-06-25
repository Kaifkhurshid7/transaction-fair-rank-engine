export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        gradient: {
          from: '#667eea',
          to: '#764ba2',
        }
      },
      backdropBlur: {
        glass: '10px',
      }
    },
  },
  plugins: [],
}
