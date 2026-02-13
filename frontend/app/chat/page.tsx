'use client';

import { useState, useRef, useEffect } from 'react';
import { aiAgentClient } from '../api-client';

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
    return "I understand you want to delete a task, but I'm unable to connect to the backend to remove tasks. Please check that the backend services are running.";
  } else {
    return "I'm currently unable to connect to my backend services. Please make sure the AI agent server is running on http://localhost:8001 and the main backend is running on http://localhost:8000. I can still chat with you, but I can't manage your tasks until the services are available.";
  }
};

export default function ChatPage() {
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

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // const handleSubmit = async (e: React.FormEvent) => {
  //   e.preventDefault();

  //   if (!inputMessage.trim()) return;

  //   // Add user message to chat
  //   const userMessage: Message = {
  //     id: Date.now().toString(),
  //     content: inputMessage,
  //     role: 'user',
  //     timestamp: new Date().toISOString(),
  //   };

  //   setMessages(prev => [...prev, userMessage]);
  //   setInputMessage('');
  //   setIsLoading(true);

  //   try {
  //     // Call the AI agent API using the centralized client
  //     const response = await aiAgentClient.post('/chat', { message: inputMessage });

  //     // Ensure we're getting the response in the expected format
  //     console.log('Received data from backend:', response.data);

  //     // Add AI response to chat - the backend returns data in {response: "..."} format
  //     const aiMessage: Message = {
  //       id: Date.now().toString(),
  //       content: typeof response.data === 'string' 
  //         ? response.data 
  //         : (response.data.response || response.data.message || JSON.stringify(response.data)),
  //       role: 'assistant',
  //       timestamp: new Date().toISOString(),
  //     };

  //     setMessages(prev => [...prev, aiMessage]);
  //   } catch (error: any) {
  //     console.error('Error calling AI agent:', error);

  //     // Check if it's a network error or a 401/403 error
  //     if (error.code === 'ECONNABORTED' || error.message.includes('Network Error') || error.request) {
  //       // Network error - backend probably not running
  //       const fallbackResponse = generateFallbackResponse(inputMessage);

  //       const errorMessage: Message = {
  //         id: Date.now().toString(),
  //         content: fallbackResponse,
  //         role: 'assistant',
  //         timestamp: new Date().toISOString(),
  //       };

  //       setMessages(prev => [...prev, errorMessage]);
  //     } else if (error.response?.status === 401 || error.response?.status === 403) {
  //       // Authentication error
  //       const errorMessage: Message = {
  //         id: Date.now().toString(),
  //         content: 'Authentication failed. Please log in again.',
  //         role: 'assistant',
  //         timestamp: new Date().toISOString(),
  //       };

  //       setMessages(prev => [...prev, errorMessage]);
        
  //       // Remove token and redirect to login (this would need to be handled by the calling component)
  //       if (typeof window !== 'undefined') {
  //         localStorage.removeItem('token');
  //       }
  //     } else {
  //       // Some other error - show the actual error message
  //       const errorMessage: Message = {
  //         id: Date.now().toString(),
  //         content: `Error communicating with AI agent: ${error.response?.data?.detail || error.message || 'Unknown error'}`,
  //         role: 'assistant',
  //         timestamp: new Date().toISOString(),
  //       };

  //       setMessages(prev => [...prev, errorMessage]);
  //     }
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

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
      // Get the stored token after login
      const token = localStorage.getItem("token");

      // Call the AI agent API with Authorization header
      const response = await aiAgentClient.post(
        "/chat",
        { message: inputMessage },
        {
          headers: {
            Authorization: `Bearer ${token}`, // Send token to backend
          },
        },
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 w-10 h-10 rounded-full flex items-center justify-center mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-gray-900">AI Todo Assistant</h1>
          </div>
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-red-500 to-red-600 rounded-xl hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 shadow-md hover:shadow-lg"
          >
            Reset Chat
          </button>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 overflow-hidden max-w-4xl mx-auto w-full flex flex-col px-4 py-6">
        <div className="flex-1 overflow-y-auto space-y-6 pb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className="flex max-w-[85%] md:max-w-[75%]">
                {message.role === 'assistant' && (
                  <div className="mr-3 flex-shrink-0">
                    <div className="bg-gradient-to-r from-indigo-500 to-purple-600 w-8 h-8 rounded-full flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                )}
                <div
                  className={`px-5 py-3 rounded-2xl shadow-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-tr-none'
                      : 'bg-white text-gray-800 rounded-tl-none border border-gray-200'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div
                    className={`text-xs mt-2 ${
                      message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                    }`}
                  >
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {message.role === 'user' && (
                  <div className="ml-3 flex-shrink-0">
                    <div className="bg-gradient-to-r from-blue-500 to-indigo-600 w-8 h-8 rounded-full flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
              <div className="flex max-w-[75%]">
                <div className="mr-3 flex-shrink-0">
                  <div className="bg-gradient-to-r from-indigo-500 to-purple-600 w-8 h-8 rounded-full flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
                <div className="px-5 py-3 rounded-2xl bg-white text-gray-800 rounded-tl-none border border-gray-200 shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl shadow-lg p-4 border border-gray-200">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message here..."
              className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-200"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className={`px-5 py-3 rounded-xl text-white font-medium ${
                isLoading || !inputMessage.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 shadow-md hover:shadow-lg'
              } transition-all duration-200 transform hover:-translate-y-0.5`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </form>
          <div className="mt-3 text-xs text-gray-500 text-center">
            Example: "Add a task to buy groceries tomorrow" or "Show my tasks"
          </div>
        </div>
      </div>
    </div>
  );
}