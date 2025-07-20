You are an expert Frontend Developer specializing in building modern, responsive web applications with Nuxt.js. Your task is to create a complete, single-page web application that serves as the user interface for the Board Game Rule Assistant.

The application will interact with a pre-existing FastAPI backend.

### **Core Requirements:**

1. **Framework:** Use **Nuxt 4**.
2. **Styling:** Use **Tailwind CSS** for all styling. The UI must be clean, modern, and responsive.
3. **State Management:** Use Nuxt's built-in composable for all reactive state.
4. **API Communication:** Assume the backend is running at `http://127.0.0.1:8000`.

### **Backend API Endpoints:**

You will need to interact with the following two endpoints:

1. **`POST /upload`**
   * **Request:** `FormData` containing the PDF file.
   * **Success Response (JSON):** `{ "session_id": "some-unique-id" }`

2. **`POST /chat`**
   * **Request (JSON):** `{ "session_id": "the-id-from-upload", "query": "user's question" }`
   * **Success Response (JSON):** `{ "result": "the-ai-generated-answer" }`

### **User Interface (UI) and User Experience (UX) Flow:**

The application should have two main states: **"Upload State"** and **"Chat State"**.

1. **Initial View (Upload State):**
   * Display a welcoming message and a clear call-to-action to upload a board game rulebook PDF.
   * Implement a file input component. A styled drag-and-drop zone is highly preferred.
   * When a file is selected/dropped, immediately send it to the `POST /upload` backend endpoint.
   * While the file is uploading and being processed, display a prominent loading indicator (e.g., a spinner with the text "Analyzing Rules..."). The UI should be disabled during this time.
   * Upon receiving a successful response with a `session_id`, store the ID in the application's state and transition to the "Chat State".
   * If there is an error during upload, display a user-friendly error message.

2. **Main View (Chat State):**
   * This view should only become visible after a PDF has been successfully processed.
   * **Chat History:** A main content area that displays the conversation. User messages should be aligned to one side (e.g., right), and AI responses to the other (e.g., left).
   * **Message Input:** A fixed input form at the bottom of the screen containing a text input field and a "Send" button.
   * When the user submits a question:
     * Add the user's message to the chat history immediately.
     * Show a "thinking..." indicator in the chat history to signify the AI is working.
     * Send the `session_id` and the user's `query` to the `POST /chat` endpoint.
     * Once the response is received, replace the "thinking..." indicator with the AI's answer.
     * If there is an error, display it appropriately in the chat history.

### **Code Structure and Best Practices:**

* Implement the entire application within the `app.vue` file for simplicity.
* Use Vue 3's `<script setup>` syntax.
* Create reusable composables if necessary, but it's not required for this single-file implementation.
* Add comments to explain the logic for state management, API calls, and the UI flow.
* Provide the necessary setup for Tailwind CSS in the `nuxt.config.ts` file.

Please generate the complete code for `app.vue` and `nuxt.config.ts`.