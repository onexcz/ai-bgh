# Client

  nuxt.config.ts

  - Configured Tailwind CSS module
  - Set up runtime config for API base URL (defaults to http://127.0.0.1:8000)
  - Disabled SSR for simplicity

  app.vue

  A complete single-page application with:

  Upload State:

  - Drag-and-drop PDF upload zone with hover effects
  - File validation (only PDFs allowed)
  - Loading indicator during file processing
  - Error handling with user-friendly messages

  Chat State:

  - Clean chat interface with message history
  - User messages (right-aligned, indigo background)
  - AI responses (left-aligned, white background)
  - Animated "thinking" indicator during AI processing
  - Fixed input form at the bottom
  - "Upload New Rulebook" button to reset session

  Features:

  - Smooth scrolling to latest messages
  - Disabled inputs during processing
  - Responsive design using Tailwind CSS
  - Session management with unique IDs
  - Error handling for both upload and chat operations

  To run the application:
  1. Navigate to the client directory: cd client
  2. Install dependencies: npm install
  3. Install Tailwind CSS module: npm install @nuxtjs/tailwindcss
  4. Run the development server: npm run dev

  The frontend will connect to your FastAPI backend at http://127.0.0.1:8000.