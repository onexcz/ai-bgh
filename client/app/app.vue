<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Upload State -->
    <div v-if="!sessionId" class="flex items-center justify-center min-h-screen p-4">
      <div class="max-w-md w-full">
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold text-gray-900 mb-2">Board Game Rule Assistant</h1>
          <p class="text-lg text-gray-600">Upload your game's rulebook PDF to get started</p>
        </div>

        <!-- File Upload Zone -->
        <div 
          @dragover.prevent
          @drop.prevent="handleDrop"
          @click="openFileDialog"
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-indigo-500 hover:bg-indigo-50"
          :class="{ 'border-indigo-500 bg-indigo-50': isDragging }"
          @dragenter.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            @change="handleFileSelect"
            class="hidden"
          />
          
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          
          <p class="text-gray-600 mb-2">
            Drag and drop your PDF here, or click to browse
          </p>
          <p class="text-sm text-gray-500">Only PDF files are supported</p>
        </div>

        <!-- Loading State -->
        <div v-if="isUploading" class="mt-8 text-center">
          <div class="inline-flex items-center">
            <svg class="animate-spin h-5 w-5 mr-3 text-indigo-600" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span class="text-lg text-gray-700">Analyzing Rules...</span>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="uploadError" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-700">{{ uploadError }}</p>
        </div>
      </div>
    </div>

    <!-- Chat State -->
    <div v-else class="flex flex-col h-screen">
      <!-- Header -->
      <div class="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
        <div class="max-w-4xl mx-auto flex items-center justify-between">
          <h1 class="text-xl font-semibold text-gray-900">Board Game Rule Assistant</h1>
          <button 
            @click="resetSession"
            class="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Upload New Rulebook
          </button>
        </div>
      </div>

      <!-- Chat History -->
      <div class="flex-1 overflow-y-auto px-4 py-6">
        <div class="max-w-4xl mx-auto space-y-4">
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="text-center text-gray-500 py-8">
            <p class="text-lg">Rulebook loaded! Ask me anything about the game rules.</p>
          </div>

          <!-- Messages -->
          <div v-for="(message, index) in messages" :key="index">
            <!-- User Message -->
            <div v-if="message.role === 'user'" class="flex justify-end">
              <div class="max-w-2xl bg-indigo-600 text-white rounded-lg px-4 py-2">
                <p class="whitespace-pre-wrap">{{ message.content }}</p>
              </div>
            </div>

            <!-- AI Message -->
            <div v-else class="flex justify-start">
              <div class="max-w-2xl bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm">
                <p class="whitespace-pre-wrap text-gray-800">{{ message.content }}</p>
              </div>
            </div>
          </div>

          <!-- Thinking Indicator -->
          <div v-if="isThinking" class="flex justify-start">
            <div class="bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm">
              <div class="flex items-center space-x-2">
                <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
                <span class="text-sm text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>

          <!-- Scroll Anchor -->
          <div ref="scrollAnchor"></div>
        </div>
      </div>

      <!-- Input Form -->
      <div class="bg-white border-t border-gray-200 px-4 py-4">
        <form @submit.prevent="sendMessage" class="max-w-4xl mx-auto">
          <div class="flex space-x-4">
            <input
              v-model="currentMessage"
              type="text"
              placeholder="Ask about the game rules..."
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              :disabled="isThinking"
            />
            <button
              type="submit"
              :disabled="!currentMessage.trim() || isThinking"
              class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

// Get API base URL from runtime config
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

// State management
const sessionId = ref(null)
const messages = ref([])
const currentMessage = ref('')
const isUploading = ref(false)
const isThinking = ref(false)
const uploadError = ref('')
const isDragging = ref(false)

// Refs for DOM elements
const fileInput = ref(null)
const scrollAnchor = ref(null)

// File handling functions
const openFileDialog = () => {
  fileInput.value?.click()
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = async (file) => {
  // Validate file type
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    uploadError.value = 'Please upload a PDF file'
    return
  }

  // Reset error and start upload
  uploadError.value = ''
  isUploading.value = true

  try {
    // Create FormData and append file
    const formData = new FormData()
    formData.append('file', file)

    // Upload file to backend
    const response = await fetch(`${apiBase}/upload`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    const data = await response.json()
    
    // Store session ID and transition to chat state
    sessionId.value = data.session_id
    
  } catch (error) {
    uploadError.value = error.message || 'Failed to upload file. Please try again.'
  } finally {
    isUploading.value = false
  }
}

// Chat functions
const sendMessage = async () => {
  const message = currentMessage.value.trim()
  if (!message || isThinking.value) return

  // Add user message to chat
  messages.value.push({
    role: 'user',
    content: message
  })

  // Clear input and set thinking state
  currentMessage.value = ''
  isThinking.value = true

  // Scroll to bottom
  await scrollToBottom()

  try {
    // Send message to backend
    const response = await fetch(`${apiBase}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: sessionId.value,
        query: message
      })
    })

    if (!response.ok) {
      throw new Error(`Chat failed: ${response.statusText}`)
    }

    const data = await response.json()
    
    // Add AI response to chat
    messages.value.push({
      role: 'assistant',
      content: data.result
    })
    
  } catch (error) {
    // Add error message to chat
    messages.value.push({
      role: 'assistant',
      content: `Sorry, I encountered an error: ${error.message}`
    })
  } finally {
    isThinking.value = false
    // Scroll to bottom after response
    await scrollToBottom()
  }
}

// Utility functions
const scrollToBottom = async () => {
  await nextTick()
  scrollAnchor.value?.scrollIntoView({ behavior: 'smooth' })
}

const resetSession = () => {
  if (confirm('Are you sure you want to upload a new rulebook? Current conversation will be lost.')) {
    sessionId.value = null
    messages.value = []
    currentMessage.value = ''
    uploadError.value = ''
  }
}
</script>

<style scoped>
/* Animation for thinking dots */
@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}
</style>
