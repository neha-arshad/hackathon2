'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '../api-client'
import { API_BASE_URL } from '../api.config'

interface Task {
  id: number
  title: string
  description: string
  completed: boolean
  priority: string
  created_at: string
}

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tasks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Todo Dashboard</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
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
            <div className="rounded-md bg-red-50 p-4 mb-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Add Task Form */}
            <div className="lg:col-span-1">
              <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Add New Task</h2>
                <form onSubmit={handleAddTask}>
                  <div className="mb-4">
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                      Title *
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Task title"
                    />
                  </div>

                  <div className="mb-4">
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <textarea
                      id="description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={3}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Task description"
                    />
                  </div>

                  <div className="mb-4">
                    <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                      Priority
                    </label>
                    <select
                      id="priority"
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className="mt-1 block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>

                  <button
                    type="submit"
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Add Task
                  </button>
                </form>
              </div>

              {/* Filters Section */}
              <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Filters</h2>

                <div className="mb-4">
                  <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                    Search
                  </label>
                  <input
                    type="text"
                    id="search"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Search tasks..."
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <input
                        id="status-all"
                        name="status"
                        type="radio"
                        checked={filterCompleted === 'all'}
                        onChange={() => setFilterCompleted('all')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="status-all" className="ml-2 block text-sm text-gray-900">
                        All
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="status-completed"
                        name="status"
                        type="radio"
                        checked={filterCompleted === 'completed'}
                        onChange={() => setFilterCompleted('completed')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="status-completed" className="ml-2 block text-sm text-gray-900">
                        Completed
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="status-pending"
                        name="status"
                        type="radio"
                        checked={filterCompleted === 'pending'}
                        onChange={() => setFilterCompleted('pending')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="status-pending" className="ml-2 block text-sm text-gray-900">
                        Pending
                      </label>
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <input
                        id="priority-all"
                        name="priority"
                        type="radio"
                        checked={filterPriority === 'all'}
                        onChange={() => setFilterPriority('all')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="priority-all" className="ml-2 block text-sm text-gray-900">
                        All
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="priority-low"
                        name="priority"
                        type="radio"
                        checked={filterPriority === 'low'}
                        onChange={() => setFilterPriority('low')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="priority-low" className="ml-2 block text-sm text-gray-900">
                        Low
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="priority-medium"
                        name="priority"
                        type="radio"
                        checked={filterPriority === 'medium'}
                        onChange={() => setFilterPriority('medium')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="priority-medium" className="ml-2 block text-sm text-gray-900">
                        Medium
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="priority-high"
                        name="priority"
                        type="radio"
                        checked={filterPriority === 'high'}
                        onChange={() => setFilterPriority('high')}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <label htmlFor="priority-high" className="ml-2 block text-sm text-gray-900">
                        High
                      </label>
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sort By
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as 'created_at' | 'priority')}
                        className="block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      >
                        <option value="created_at">Created At</option>
                        <option value="priority">Priority</option>
                      </select>
                    </div>
                    <div>
                      <select
                        value={sortOrder}
                        onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                        className="block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
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
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Your Tasks ({filteredTasks.length})</h3>
                  <p className="mt-1 text-sm text-gray-500">Manage your tasks efficiently</p>
                </div>

                <ul className="divide-y divide-gray-200">
                  {filteredTasks.length === 0 ? (
                    <li className="px-4 py-5 sm:px-6">
                      <p className="text-gray-500 text-center">No tasks match your filters. Try changing your search or filter criteria.</p>
                    </li>
                  ) : (
                    filteredTasks.map((task) => (
                      <li key={task.id} className="px-4 py-5 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={task.completed}
                              onChange={() => handleToggleComplete(task.id, task.completed)}
                              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                            />
                            <div className="ml-3">
                              <p className={`text-sm font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                {task.title}
                              </p>
                              <p className="text-sm text-gray-500 truncate max-w-xs">{task.description}</p>
                              <div className="mt-1 flex items-center">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  task.priority === 'high' ? 'bg-red-100 text-red-800' :
                                  task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-green-100 text-green-800'
                                }`}>
                                  {task.priority}
                                </span>
                                <span className="ml-2 text-xs text-gray-500">
                                  {new Date(task.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <button
                              onClick={() => handleDeleteTask(task.id)}
                              className="ml-2 inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </li>
                    ))
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}