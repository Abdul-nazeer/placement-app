import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      // Error is handled by the auth context
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">PlacementPrep</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.name}
              </span>
              <Link
                to="/profile"
                className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
              >
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to PlacementPrep Dashboard
              </h2>
              <p className="text-gray-600 mb-8">
                Your comprehensive platform for placement preparation
              </p>

              {/* User Info Card */}
              <div className="bg-white rounded-lg shadow p-6 max-w-md mx-auto mb-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Your Account</h3>
                <div className="space-y-2 text-left">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Name:</span>
                    <span className="text-sm font-medium">{user?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Email:</span>
                    <span className="text-sm font-medium">{user?.email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Role:</span>
                    <span className="text-sm font-medium capitalize">{user?.role}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Status:</span>
                    <span className={`text-sm font-medium ${
                      user?.is_active ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {user?.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Aptitude Tests</h3>
                  <p className="text-sm text-gray-500 mb-4">Practice aptitude questions organized by company and topic</p>
                  <Link
                    to="/aptitude"
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                  >
                    Start Practice
                  </Link>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Coding Challenges</h3>
                  <p className="text-sm text-gray-500 mb-4">Solve programming problems with automated testing</p>
                  <Link
                    to="/coding"
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200"
                  >
                    Start Coding
                  </Link>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Communication Training</h3>
                  <p className="text-sm text-gray-500 mb-4">Improve your interview communication skills with AI feedback</p>
                  <Link
                    to="/communication"
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-orange-700 bg-orange-100 hover:bg-orange-200"
                  >
                    Practice Speaking
                  </Link>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Mock Interviews</h3>
                  <p className="text-sm text-gray-500 mb-4">Practice with AI-powered interview simulations</p>
                  <Link
                    to="/interviews"
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-purple-700 bg-purple-100 hover:bg-purple-200"
                  >
                    Start Interview
                  </Link>
                </div>
              </div>

              <div className="mt-8">
                <p className="text-sm text-gray-500">
                  More features will be available as development progresses.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;