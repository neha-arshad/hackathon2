'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '../api-client'
import { API_BASE_URL } from '../api.config'
import { aiAgentClient } from '../api-client'

interface Task {
  id: number
  title: string
  description: string
  completed: boolean
  priority: string
  created_at: string
}

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string; // Store as string to avoid hydration issues
}

// Helper function to generate fallback responses when backend is not available
const generateFallbackResponse = (userMessage: string): string => {
  const lowerMsg = userMessage.toLowerCase();

  if (lowerMsg.includes('hello') || lowerMsg.includes('hi') || lowerMsg.includes('hey')) {
    return "Hello! I'm your AI assistant for managing your todo list. I'm currently unable to connect to my backend services, but I'm here to help you!";
  } else if (lowerMsg.includes('add') || lowerMsg.includes('create') || lowerMsg.includes('new task')) {
    return "I understand you want to add a task. I've noted that you want to: " + userMessage.substring(userMessage.indexOf('add') + 3).trim() + ". However, I'm currently unable to connect to the backend to save this task. Please make sure the backend services are running.";
  } else if (lowerMsg.includes('list') || lowerMsg.includes('show') || lowerMsg.includes('my tasks')) {
    return "I'm unable to retrieve your tasks right now because the backend services are not available. Please check that the backend is running on http://localhost:8000.";
  } else if (lowerMsg.includes('complete') || lowerMsg.includes('done') || lowerMsg.includes('finish')) {
    return "I understand you want to mark a task as complete, but I'm unable to connect to the backend to update your tasks. Please make sure the backend services are running.";
  } else if (lowerMsg.includes('delete') || lowerMsg.includes('remove')) {
    return "I understand you want to delete a task, but I'm unable to connect to the backend to remove tasks. Please check that the backend is running.";
  } else {
    return "I'm currently unable to connect to my backend services. Please make sure the AI agent server is running on http://localhost:8001 and the main backend is running on http://localhost:8000. I can still chat with you, but I can't manage your tasks until the services are available.";
  }
};

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('medium')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCompleted, setFilterCompleted] = useState<string>('all') // 'all', 'completed', 'pending'
  const [filterPriority, setFilterPriority] = useState<string>('all') // 'all', 'low', 'medium', 'high'
  const [sortBy, setSortBy] = useState<'created_at' | 'priority'>('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const router = useRouter()

  // Chatbot state
  const [chatOpen, setChatOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your AI assistant for managing your todo list. How can I help you today?',
      role: 'assistant',
      timestamp: new Date().toISOString(),
    }
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Check if user is authenticated
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/auth/login')
    } else {
      fetchTasks()
    }
  }, [])

  const fetchTasks = async () => {
    try {
      const response = await apiClient.get('/tasks')
      setTasks(response.data)
      setLoading(false)
      setError('') // Clear any previous errors
    } catch (err: any) {
      setLoading(false)
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError('Authentication failed. Please log in again.')
        localStorage.removeItem('token')
        router.push('/auth/login')
      } else if (err.response?.status === 404) {
        setError('Tasks endpoint not found. Please check if the backend is running.')
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to the backend. Please make sure the server is running.')
      } else {
        setError(err.response?.data?.detail || 'Failed to load tasks')
      }
      console.error('Error fetching tasks:', err)
    }
  }

  // Apply filters and sorting
  useEffect(() => {
    let result = [...tasks]

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(task =>
        task.title.toLowerCase().includes(term) ||
        task.description.toLowerCase().includes(term)
      )
    }

    // Apply completion filter
    if (filterCompleted !== 'all') {
      const completed = filterCompleted === 'completed'
      result = result.filter(task => task.completed === completed)
    }

    // Apply priority filter
    if (filterPriority !== 'all') {
      result = result.filter(task => task.priority === filterPriority)
    }

    // Apply sorting
    result.sort((a, b) => {
      if (sortBy === 'created_at') {
        const dateA = new Date(a.created_at).getTime()
        const dateB = new Date(b.created_at).getTime()
        return sortOrder === 'asc' ? dateA - dateB : dateB - dateA
      } else if (sortBy === 'priority') {
        const priorityOrder: Record<string, number> = { high: 1, medium: 2, low: 3 }
        const priorityA = priorityOrder[a.priority] || 4
        const priorityB = priorityOrder[b.priority] || 4
        return sortOrder === 'asc' ? priorityA - priorityB : priorityB - priorityA
      }
      return 0
    })

    setFilteredTasks(result)
  }, [tasks, searchTerm, filterCompleted, filterPriority, sortBy, sortOrder])

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    try {
      const response = await apiClient.post('/tasks', { title, description, priority })

      // Reset form
      setTitle('')
      setDescription('')
      setPriority('medium')

      // Show success message temporarily
      setError('Task added successfully!')

      // Refresh tasks
      fetchTasks()
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError('Authentication failed. Please log in again.')
        localStorage.removeItem('token')
        router.push('/auth/login')
      } else if (err.response?.status === 404) {
        setError('Tasks endpoint not found. Please check if the backend is running.')
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to the backend. Please make sure the server is running.')
      } else {
        setError(err.response?.data?.detail || 'Failed to add task')
      }
      console.error('Error adding task:', err)
    }
  }

  const handleDeleteTask = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return
    }

    try {
      await apiClient.delete(`/tasks/${id}`)

      // Show success message temporarily
      setError('Task deleted successfully!')

      // Refresh tasks
      fetchTasks()
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError('Authentication failed. Please log in again.')
        localStorage.removeItem('token')
        router.push('/auth/login')
      } else if (err.response?.status === 404) {
        setError('Task not found or already deleted.')
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to the backend. Please make sure the server is running.')
      } else {
        setError(err.response?.data?.detail || 'Failed to delete task')
      }
      console.error('Error deleting task:', err)
    }
  }

  const handleToggleComplete = async (id: number, completed: boolean) => {
    try {
      await apiClient.put(`/tasks/${id}/complete`, { completed: !completed })

      // Show success message temporarily
      setError('Task status updated successfully!')

      // Refresh tasks
      fetchTasks()
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError('Authentication failed. Please log in again.')
        localStorage.removeItem('token')
        router.push('/auth/login')
      } else if (err.response?.status === 404) {
        setError('Task not found.')
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to the backend. Please make sure the server is running.')
      } else {
        setError(err.response?.data?.detail || 'Failed to update task')
      }
      console.error('Error updating task:', err)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/auth/login')
  }

  // Chatbot functions
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // NOTE: No need to manually set Authorization header
      // The axios interceptor in api-client.ts automatically adds it
      const response = await aiAgentClient.post(
        "/chat",
        { message: inputMessage },
      );

      // Ensure we're getting the response in the expected format
      console.log("Received data from backend:", response.data);

      // Add AI response to chat - the backend returns data in {response: "..."} format
      const aiMessage: Message = {
        id: Date.now().toString(),
        content:
          typeof response.data === "string"
            ? response.data
            : response.data.response ||
              response.data.message ||
              JSON.stringify(response.data),
        role: "assistant",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error: any) {
      console.error("Error calling AI agent:", error);

      // Check if it's a network error or a 401/403 error
      if (
        error.code === "ECONNABORTED" ||
        error.message.includes("Network Error") ||
        error.request
      ) {
        // Network error - backend probably not running
        const fallbackResponse = generateFallbackResponse(inputMessage);

        const errorMessage: Message = {
          id: Date.now().toString(),
          content: fallbackResponse,
          role: "assistant",
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } else if (
        error.response?.status === 401 ||
        error.response?.status === 403
      ) {
        // Authentication error
        const errorMessage: Message = {
          id: Date.now().toString(),
          content: "Authentication failed. Please log in again.",
          role: "assistant",
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);

        // Remove token and redirect to login (this would need to be handled by the calling component)
        if (typeof window !== "undefined") {
          localStorage.removeItem("token");
        }
      } else {
        // Some other error - show the actual error message
        const errorMessage: Message = {
          id: Date.now().toString(),
          content: `Error communicating with AI agent: ${error.response?.data?.detail || error.message || "Unknown error"}`,
          role: "assistant",
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([
      {
        id: '1',
        content: 'Hello! I\'m your AI assistant for managing your todo list. How can I help you today?',
        role: 'assistant',
        timestamp: new Date().toISOString(),
      }
    ]);
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tasks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 w-8 h-8 rounded-lg flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h1 className="ml-3 text-xl font-bold text-gray-900">Todo Dashboard</h1>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-red-500 to-red-600 rounded-xl hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="rounded-lg bg-red-50 p-4 mb-6 border border-red-200 shadow-sm">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Add Task Form */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white shadow-lg rounded-2xl p-6 transition-all duration-300 hover:shadow-xl">
                <div className="flex items-center mb-4">
                  <div className="bg-indigo-100 p-2 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </div>
                  <h2 className="ml-3 text-lg font-semibold text-gray-900">Add New Task</h2>
                </div>
                
                <form onSubmit={handleAddTask}>
                  <div className="mb-4">
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                      Title *
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      className="block w-full border border-gray-300 rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-200"
                      placeholder="Enter task title"
                    />
                  </div>

                  <div className="mb-4">
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={3}
                      className="block w-full border border-gray-300 rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-200"
                      placeholder="Enter task description"
                    />
                  </div>

                  <div className="mb-6">
                    <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                      Priority
                    </label>
                    <select
                      id="priority"
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className="block w-full bg-white border border-gray-300 rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-200"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>

                  <button
                    type="submit"
                    className="w-full flex justify-center py-3 px-4 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 transform hover:-translate-y-0.5 shadow-md hover:shadow-lg"
                  >
                    Add Task
                  </button>
                </form>
              </div>

              {/* Filters Section */}
              <div className="bg-white shadow-lg rounded-2xl p-6 transition-all duration-300 hover:shadow-xl">
                <div className="flex items-center mb-4">
                  <div className="bg-indigo-100 p-2 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                  </div>
                  <h2 className="ml-3 text-lg font-semibold text-gray-900">Filters</h2>
                </div>

                <div className="mb-5">
                  <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                    Search
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <input
                      type="text"
                      id="search"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-200"
                      placeholder="Search tasks..."
                    />
                  </div>
                </div>

                <div className="mb-5">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <div className="space-y-2">
                    {[
                      { id: 'status-all', value: 'all', label: 'All' },
                      { id: 'status-completed', value: 'completed', label: 'Completed' },
                      { id: 'status-pending', value: 'pending', label: 'Pending' }
                    ].map((option) => (
                      <div key={option.id} className="flex items-center">
                        <input
                          id={option.id}
                          name="status"
                          type="radio"
                          checked={filterCompleted === option.value}
                          onChange={() => setFilterCompleted(option.value)}
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                        />
                        <label htmlFor={option.id} className="ml-2 block text-sm text-gray-700">
                          {option.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mb-5">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority
                  </label>
                  <div className="space-y-2">
                    {[
                      { id: 'priority-all', value: 'all', label: 'All' },
                      { id: 'priority-low', value: 'low', label: 'Low' },
                      { id: 'priority-medium', value: 'medium', label: 'Medium' },
                      { id: 'priority-high', value: 'high', label: 'High' }
                    ].map((option) => (
                      <div key={option.id} className="flex items-center">
                        <input
                          id={option.id}
                          name="priority"
                          type="radio"
                          checked={filterPriority === option.value}
                          onChange={() => setFilterPriority(option.value)}
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                        />
                        <label htmlFor={option.id} className="ml-2 block text-sm text-gray-700">
                          {option.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sort By
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as 'created_at' | 'priority')}
                        className="block w-full bg-white border border-gray-300 rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-200"
                      >
                        <option value="created_at">Created At</option>
                        <option value="priority">Priority</option>
                      </select>
                    </div>
                    <div>
                      <select
                        value={sortOrder}
                        onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                        className="block w-full bg-white border border-gray-300 rounded-xl py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition duration-200"
                      >
                        <option value="desc">Descending</option>
                        <option value="asc">Ascending</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tasks List */}
            <div className="lg:col-span-2">
              <div className="bg-white shadow-lg rounded-2xl overflow-hidden">
                <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg leading-6 font-semibold text-gray-900">Your Tasks ({filteredTasks.length})</h3>
                      <p className="mt-1 text-sm text-gray-500">Manage your tasks efficiently</p>
                    </div>
                    <div className="flex items-center">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                        {filteredTasks.filter(t => !t.completed).length} pending
                      </span>
                    </div>
                  </div>
                </div>

                <div className="divide-y divide-gray-200">
                  {filteredTasks.length === 0 ? (
                    <div className="px-6 py-12 text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
                      <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
                    </div>
                  ) : (
                    filteredTasks.map((task) => (
                      <div key={task.id} className="px-6 py-5 hover:bg-gray-50 transition-colors duration-150">
                        <div className="flex items-start">
                          <input
                            type="checkbox"
                            checked={task.completed}
                            onChange={() => handleToggleComplete(task.id, task.completed)}
                            className="h-5 w-5 mt-0.5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                          />
                          <div className="ml-4 flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className={`text-sm font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                {task.title}
                              </p>
                              <div className="flex items-center space-x-2">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  task.priority === 'high' ? 'bg-red-100 text-red-800' :
                                  task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-green-100 text-green-800'
                                }`}>
                                  {task.priority}
                                </span>
                                <span className="text-xs text-gray-500">
                                  {new Date(task.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                            <p className="mt-1 text-sm text-gray-500 truncate">{task.description}</p>
                          </div>
                          <div className="ml-4 flex-shrink-0">
                            <button
                              onClick={() => handleDeleteTask(task.id)}
                              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Chat Widget */}
      <div className="fixed bottom-6 right-6 z-50">
        {chatOpen ? (
          <div className="bg-white rounded-2xl shadow-xl w-80 h-[500px] flex flex-col border border-gray-200">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white p-4 rounded-t-2xl flex justify-between items-center">
              <div className="flex items-center">
                <div className="bg-white bg-opacity-20 w-8 h-8 rounded-full flex items-center justify-center mr-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="font-semibold">AI Assistant</h3>
              </div>
              <button 
                onClick={() => setChatOpen(false)}
                className="text-white hover:text-gray-200 focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className="flex max-w-[85%]">
                    {message.role === 'assistant' && (
                      <div className="mr-2 flex-shrink-0">
                        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 w-7 h-7 rounded-full flex items-center justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                      </div>
                    )}
                    <div
                      className={`px-3 py-2 rounded-2xl shadow-sm text-sm ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-tr-none'
                          : 'bg-white text-gray-800 rounded-tl-none border border-gray-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      <div
                        className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                    {message.role === 'user' && (
                      <div className="ml-2 flex-shrink-0">
                        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 w-7 h-7 rounded-full flex items-center justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex max-w-[85%]">
                    <div className="mr-2 flex-shrink-0">
                      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 w-7 h-7 rounded-full flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                    </div>
                    <div className="px-3 py-2 rounded-2xl bg-white text-gray-800 rounded-tl-none border border-gray-200 shadow-sm">
                      <div className="flex space-x-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce"></div>
                        <div className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-3 border-t border-gray-200 bg-white">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !inputMessage.trim()}
                  className={`px-3 py-2 rounded-lg text-white text-sm font-medium ${
                    isLoading || !inputMessage.trim()
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800'
                  }`}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                  </svg>
                </button>
              </form>
              <div className="mt-1 text-xs text-gray-500 text-center">
                AI Assistant
              </div>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setChatOpen(true)}
            className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white p-4 rounded-full shadow-lg hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 transform hover:scale-105"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}