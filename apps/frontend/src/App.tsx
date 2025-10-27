import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import Dashboard from './components/Dashboard';
import ProfileForm from './components/profile/ProfileForm';
import AdminLayout from './components/admin/AdminLayout';
import AdminDashboard from './components/admin/AdminDashboard';
import QuestionList from './components/admin/questions/QuestionList';
import QuestionEditor from './components/admin/questions/QuestionEditor';
import ImportExport from './components/admin/ImportExport';
import Analytics from './components/admin/Analytics';

// Communication components
import { CommunicationDashboard } from './components/communication/CommunicationDashboard';
import { PracticeSession } from './components/communication/PracticeSession';
import { PromptBrowser } from './components/communication/PromptBrowser';
import { ProgressTracker } from './components/communication/ProgressTracker';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <div className="App">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              
              {/* Protected routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfileForm />
                  </ProtectedRoute>
                }
              />
              
              {/* Communication routes */}
              <Route
                path="/communication"
                element={
                  <ProtectedRoute>
                    <CommunicationDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/communication/practice/:sessionId"
                element={
                  <ProtectedRoute>
                    <PracticeSession />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/communication/prompts"
                element={
                  <ProtectedRoute>
                    <PromptBrowser />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/communication/progress"
                element={
                  <ProtectedRoute>
                    <ProgressTracker />
                  </ProtectedRoute>
                }
              />
              
              {/* Admin only routes */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <AdminLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<AdminDashboard />} />
                <Route path="questions" element={<QuestionList />} />
                <Route path="questions/new" element={<QuestionEditor />} />
                <Route path="questions/:id" element={<QuestionEditor />} />
                <Route path="questions/:id/edit" element={<QuestionEditor />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="import-export" element={<ImportExport />} />
              </Route>
              
              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* 404 page */}
              <Route
                path="*"
                element={
                  <div className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="text-center">
                      <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                      <p className="text-gray-600 mb-8">Page not found</p>
                      <a
                        href="/dashboard"
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                      >
                        Go to Dashboard
                      </a>
                    </div>
                  </div>
                }
              />
            </Routes>
            
            {/* Toast notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#10B981',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#EF4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;