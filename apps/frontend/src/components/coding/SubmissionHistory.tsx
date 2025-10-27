import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  ClockIcon,
  CpuChipIcon,
  CodeBracketIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ShareIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { CodingService } from '../../services/coding';
import { CodeSubmission, LanguageType } from '../../types/coding';
import CodeEditor from './CodeEditor';
import CodeSharing from './CodeSharing';
import SubmissionAnalytics from './SubmissionAnalytics';

interface SubmissionHistoryProps {
  challengeId?: string;
  userId?: string;
}

const SubmissionHistory = ({ challengeId, userId }: SubmissionHistoryProps) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedSubmission, setSelectedSubmission] = useState<CodeSubmission | null>(null);
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const itemsPerPage = 10;

  // Fetch submissions
  const { data: submissions, isLoading, error } = useQuery({
    queryKey: ['submissions', challengeId, currentPage],
    queryFn: () => CodingService.getUserSubmissions(
      challengeId,
      itemsPerPage,
      (currentPage - 1) * itemsPerPage
    )
  });

  const totalPages = submissions ? Math.ceil(submissions.length / itemsPerPage) : 0;

  const handleViewCode = (submission: CodeSubmission) => {
    setSelectedSubmission(submission);
    setShowCodeModal(true);
  };

  const handleShareCode = (submission: CodeSubmission) => {
    setSelectedSubmission(submission);
    setShowShareModal(true);
  };

  const handleViewAnalytics = (submission: CodeSubmission) => {
    setSelectedSubmission(submission);
    setShowAnalytics(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
      case 'timeout':
      case 'memory_exceeded':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="flex space-x-2">
                <div className="h-6 bg-gray-200 rounded w-16"></div>
                <div className="h-6 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">Failed to load submissions</div>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Submission History</h2>
          <p className="mt-1 text-sm text-gray-500">
            {challengeId ? 'Your submissions for this challenge' : 'All your coding submissions'}
          </p>
        </div>
        {submissions && submissions.length > 0 && (
          <div className="text-sm text-gray-500">
            {submissions.length} submission{submissions.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Submissions List */}
      {submissions && submissions.length > 0 ? (
        <div className="space-y-4">
          {submissions.map((submission) => (
            <div
              key={submission.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    {getStatusIcon(submission.status)}
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${CodingService.getStatusColor(submission.status)}`}>
                          {submission.status.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {CodingService.getLanguageDisplayName(submission.language)}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(submission.submitted_at).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500">Score:</span>
                      <span className={`text-sm font-semibold ${getScoreColor(submission.score)}`}>
                        {submission.score.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500">Tests:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {submission.passed_test_cases}/{submission.total_test_cases}
                      </span>
                    </div>
                    {submission.execution_time && (
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {CodingService.formatExecutionTime(submission.execution_time)}
                        </span>
                      </div>
                    )}
                    {submission.memory_usage && (
                      <div className="flex items-center space-x-2">
                        <CpuChipIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {CodingService.formatMemoryUsage(submission.memory_usage)}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Error Messages */}
                  {submission.compilation_error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                      <h4 className="text-sm font-medium text-red-800 mb-1">Compilation Error:</h4>
                      <pre className="text-xs text-red-700 whitespace-pre-wrap font-mono">
                        {submission.compilation_error}
                      </pre>
                    </div>
                  )}

                  {submission.runtime_error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                      <h4 className="text-sm font-medium text-red-800 mb-1">Runtime Error:</h4>
                      <pre className="text-xs text-red-700 whitespace-pre-wrap font-mono">
                        {submission.runtime_error}
                      </pre>
                    </div>
                  )}

                  {/* Test Results Summary */}
                  {submission.test_results && submission.test_results.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Test Results:</h4>
                      <div className="flex flex-wrap gap-2">
                        {submission.test_results.map((result, index) => (
                          <div
                            key={index}
                            className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
                              result.passed
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {result.passed ? (
                              <CheckCircleIcon className="h-3 w-3" />
                            ) : (
                              <XCircleIcon className="h-3 w-3" />
                            )}
                            <span>Test {index + 1}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="ml-4 flex flex-col space-y-2">
                  <button
                    onClick={() => handleViewCode(submission)}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <EyeIcon className="h-4 w-4 mr-1" />
                    View Code
                  </button>
                  
                  {submission.status === 'completed' && (
                    <button
                      onClick={() => handleShareCode(submission)}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <ShareIcon className="h-4 w-4 mr-1" />
                      Share
                    </button>
                  )}

                  <button
                    onClick={() => handleViewAnalytics(submission)}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <ChartBarIcon className="h-4 w-4 mr-1" />
                    Analytics
                  </button>
                  
                  {!challengeId && (
                    <Link
                      to={`/coding/challenges/${submission.challenge_id}`}
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <CodeBracketIcon className="h-4 w-4 mr-1" />
                      Challenge
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CodeBracketIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No submissions yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            {challengeId 
              ? 'Submit your first solution to see it here.'
              : 'Start solving coding challenges to see your submissions here.'
            }
          </p>
          {!challengeId && (
            <div className="mt-6">
              <Link
                to="/coding"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Browse Challenges
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-5 w-5 mr-1" />
            Previous
          </button>

          <div className="flex space-x-2">
            {[...Array(Math.min(5, totalPages))].map((_, i) => {
              const pageNum = Math.max(1, currentPage - 2) + i;
              if (pageNum > totalPages) return null;
              
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    pageNum === currentPage
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRightIcon className="h-5 w-5 ml-1" />
          </button>
        </div>
      )}

      {/* Code View Modal */}
      {showCodeModal && selectedSubmission && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Submission Code - {CodingService.getLanguageDisplayName(selectedSubmission.language)}
                </h3>
                <p className="text-sm text-gray-500">
                  Submitted on {new Date(selectedSubmission.submitted_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => setShowCodeModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-4">
              <CodeEditor
                language={selectedSubmission.language}
                value={selectedSubmission.code}
                onChange={() => {}} // Read-only
                readOnly={true}
                height="400px"
                showToolbar={true}
              />
            </div>

            <div className="flex justify-end space-x-3">
              {selectedSubmission.status === 'completed' && (
                <button
                  onClick={() => {
                    setShowCodeModal(false);
                    handleShareCode(selectedSubmission);
                  }}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  Share Code
                </button>
              )}
              <button
                onClick={() => setShowCodeModal(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Code Sharing Modal */}
      {showShareModal && selectedSubmission && (
        <CodeSharing
          submission={selectedSubmission}
          onClose={() => setShowShareModal(false)}
        />
      )}

      {/* Analytics Modal */}
      {showAnalytics && selectedSubmission && (
        <SubmissionAnalytics
          submission={selectedSubmission}
          onClose={() => setShowAnalytics(false)}
        />
      )}
    </div>
  );
};

export default SubmissionHistory;