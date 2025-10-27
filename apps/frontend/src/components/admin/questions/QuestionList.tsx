import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { contentService } from '../../../services/content';
import { Question, QuestionFilters, QuestionType, DifficultyLevel, QuestionStatus } from '../../../types/content';
import QuestionFiltersComponent from './QuestionFilters';

const QuestionList: React.FC = () => {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const queryClient = useQueryClient();

  const { data: searchResult, isLoading, error } = useQuery({
    queryKey: ['questions', filters, page],
    queryFn: () => contentService.searchQuestions(filters, page, 20),
  });

  // TODO: Add mutations for delete, approve, reject

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      // TODO: Implement delete
      console.log('Delete question:', id);
    }
  };

  const handleApprove = (id: string) => {
    // TODO: Implement approve
    console.log('Approve question:', id);
  };

  const handleReject = (id: string) => {
    const reason = window.prompt('Enter rejection reason (optional):');
    // TODO: Implement reject
    console.log('Reject question:', id, reason);
  };

  const handleSelectAll = () => {
    if (selectedQuestions.length === searchResult?.questions.length) {
      setSelectedQuestions([]);
    } else {
      setSelectedQuestions(searchResult?.questions.map(q => q.id) || []);
    }
  };

  const handleSelectQuestion = (id: string) => {
    setSelectedQuestions(prev => 
      prev.includes(id) 
        ? prev.filter(qId => qId !== id)
        : [...prev, id]
    );
  };

  const getDifficultyColor = (difficulty: DifficultyLevel) => {
    switch (difficulty) {
      case DifficultyLevel.BEGINNER: return 'bg-green-100 text-green-800';
      case DifficultyLevel.EASY: return 'bg-blue-100 text-blue-800';
      case DifficultyLevel.MEDIUM: return 'bg-yellow-100 text-yellow-800';
      case DifficultyLevel.HARD: return 'bg-orange-100 text-orange-800';
      case DifficultyLevel.EXPERT: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: QuestionStatus) => {
    switch (status) {
      case QuestionStatus.DRAFT: return 'bg-gray-100 text-gray-800';
      case QuestionStatus.PENDING_REVIEW: return 'bg-yellow-100 text-yellow-800';
      case QuestionStatus.APPROVED: return 'bg-green-100 text-green-800';
      case QuestionStatus.REJECTED: return 'bg-red-100 text-red-800';
      case QuestionStatus.ARCHIVED: return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-sm text-red-700">
            Failed to load questions. Please try again.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Questions</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your question bank
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link
            to="/admin/questions/new"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
          >
            Add Question
          </Link>
        </div>
      </div>

      {/* Filters */}
      <QuestionFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        onReset={() => setFilters({})}
      />

      {/* Bulk Actions */}
      {selectedQuestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-700">
              {selectedQuestions.length} question(s) selected
            </span>
            <div className="space-x-2">
              <button
                className="text-sm text-blue-600 hover:text-blue-800"
                onClick={() => {
                  // TODO: Implement bulk approve
                  toast.info('Bulk approve coming soon');
                }}
              >
                Approve All
              </button>
              <button
                className="text-sm text-red-600 hover:text-red-800"
                onClick={() => {
                  // TODO: Implement bulk delete
                  toast.info('Bulk delete coming soon');
                }}
              >
                Delete All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Questions Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {isLoading ? (
          <div className="p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {searchResult?.questions.map((question) => (
              <li key={question.id}>
                <div className="px-4 py-4 flex items-center justify-between">
                  <div className="flex items-center min-w-0 flex-1">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mr-4"
                      checked={selectedQuestions.includes(question.id)}
                      onChange={() => handleSelectQuestion(question.id)}
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-sm font-medium text-gray-900 truncate">
                          {question.title}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
                          Level {question.difficulty}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(question.status)}`}>
                          {question.status.replace('_', ' ')}
                        </span>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {question.type}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                        <span>{question.category}</span>
                        {question.subcategory && <span>• {question.subcategory}</span>}
                        <span>• {question.usage_count} uses</span>
                        {question.success_rate && (
                          <span>• {question.success_rate.toFixed(1)}% success</span>
                        )}
                      </div>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {question.company_tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {tag}
                          </span>
                        ))}
                        {question.company_tags.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{question.company_tags.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/admin/questions/${question.id}`}
                      className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                    >
                      View
                    </Link>
                    <Link
                      to={`/admin/questions/${question.id}/edit`}
                      className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                    >
                      Edit
                    </Link>
                    {question.status === QuestionStatus.PENDING_REVIEW && (
                      <>
                        <button
                          onClick={() => handleApprove(question.id)}
                          className="text-green-600 hover:text-green-900 text-sm font-medium"
                          disabled={false}
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(question.id)}
                          className="text-red-600 hover:text-red-900 text-sm font-medium"
                          disabled={false}
                        >
                          Reject
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => handleDelete(question.id)}
                      className="text-red-600 hover:text-red-900 text-sm font-medium"
                      disabled={false}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Pagination */}
      {searchResult && searchResult.pages > 1 && (
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(Math.min(searchResult.pages, page + 1))}
              disabled={page === searchResult.pages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing{' '}
                <span className="font-medium">{(page - 1) * 20 + 1}</span>
                {' '}to{' '}
                <span className="font-medium">
                  {Math.min(page * 20, searchResult.total)}
                </span>
                {' '}of{' '}
                <span className="font-medium">{searchResult.total}</span>
                {' '}results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(searchResult.pages, page + 1))}
                  disabled={page === searchResult.pages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionList;