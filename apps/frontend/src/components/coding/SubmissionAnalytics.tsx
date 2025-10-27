import React from 'react';
import { useQuery } from '@tanstack/react-query';
// Using inline SVG icons since some heroicons are not available
import { CodingService } from '../../services/coding';
import { CodeSubmission, CodeQualityMetrics } from '../../types/coding';

interface SubmissionAnalyticsProps {
  submission: CodeSubmission;
  onClose: () => void;
}

interface PerformanceComparison {
  percentile: number;
  average_execution_time: number;
  average_memory_usage: number;
  success_rate: number;
  language_distribution: Record<string, number>;
}

const SubmissionAnalytics = ({ submission, onClose }: SubmissionAnalyticsProps) => {
  // Fetch code quality metrics
  const { data: qualityMetrics, isLoading: qualityLoading } = useQuery({
    queryKey: ['code-quality', submission.id],
    queryFn: () => CodingService.getCodeQuality(submission.id),
    enabled: submission.status === 'completed'
  });

  // Fetch performance comparison
  const { data: performanceComparison, isLoading: performanceLoading } = useQuery({
    queryKey: ['performance-comparison', submission.challenge_id, submission.language],
    queryFn: async () => {
      // This would be implemented in your backend
      const response = await fetch(`/api/v1/coding/challenges/${submission.challenge_id}/performance?language=${submission.language}`);
      return response.json();
    }
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPercentileColor = (percentile: number) => {
    if (percentile >= 90) return 'bg-green-100 text-green-800';
    if (percentile >= 70) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900">Submission Analytics</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <span className="sr-only">Close</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Performance Metrics */}
          <div className="space-y-6">
            {/* Basic Stats */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                Performance Summary
              </h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className={`text-2xl font-bold ${getScoreColor(submission.score)}`}>
                    {submission.score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-500">Score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {submission.passed_test_cases}/{submission.total_test_cases}
                  </div>
                  <div className="text-sm text-gray-500">Tests Passed</div>
                </div>
                {submission.execution_time && (
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {CodingService.formatExecutionTime(submission.execution_time)}
                    </div>
                    <div className="text-sm text-gray-500">Execution Time</div>
                  </div>
                )}
                {submission.memory_usage && (
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {CodingService.formatMemoryUsage(submission.memory_usage)}
                    </div>
                    <div className="text-sm text-gray-500">Memory Usage</div>
                  </div>
                )}
              </div>
            </div>

            {/* Performance Comparison */}
            {performanceComparison && !performanceLoading && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Performance Comparison</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Your Percentile:</span>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${getPercentileColor(performanceComparison.percentile)}`}>
                      {performanceComparison.percentile}th percentile
                    </span>
                  </div>
                  
                  {submission.execution_time && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Avg. Time:</span>
                      <span className="text-sm font-medium">
                        {CodingService.formatExecutionTime(performanceComparison.average_execution_time)}
                      </span>
                    </div>
                  )}
                  
                  {submission.memory_usage && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Avg. Memory:</span>
                      <span className="text-sm font-medium">
                        {CodingService.formatMemoryUsage(performanceComparison.average_memory_usage)}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Success Rate:</span>
                    <span className="text-sm font-medium">
                      {(performanceComparison.success_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Test Results Breakdown */}
            {submission.test_results && submission.test_results.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Test Results Breakdown</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {submission.test_results.map((result, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                      <div className="flex items-center space-x-2">
                        {result.passed ? (
                          <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : (
                          <svg className="h-4 w-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        <span className="text-sm font-medium">Test {index + 1}</span>
                      </div>
                      <div className="flex items-center space-x-3 text-xs text-gray-500">
                        <span>{CodingService.formatExecutionTime(result.execution_time)}</span>
                        <span>{CodingService.formatMemoryUsage(result.memory_usage)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Code Quality */}
          <div className="space-y-6">
            {qualityMetrics && !qualityLoading ? (
              <>
                {/* Code Quality Scores */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                    <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                    Code Quality Analysis
                  </h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Complexity:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getScoreColor(qualityMetrics.complexity_score) === 'text-green-600' ? 'bg-green-500' : getScoreColor(qualityMetrics.complexity_score) === 'text-yellow-600' ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${qualityMetrics.complexity_score}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-medium ${getScoreColor(qualityMetrics.complexity_score)}`}>
                          {qualityMetrics.complexity_score}/100
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Readability:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getScoreColor(qualityMetrics.readability_score) === 'text-green-600' ? 'bg-green-500' : getScoreColor(qualityMetrics.readability_score) === 'text-yellow-600' ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${qualityMetrics.readability_score}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-medium ${getScoreColor(qualityMetrics.readability_score)}`}>
                          {qualityMetrics.readability_score}/100
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Efficiency:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getScoreColor(qualityMetrics.efficiency_score) === 'text-green-600' ? 'bg-green-500' : getScoreColor(qualityMetrics.efficiency_score) === 'text-yellow-600' ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${qualityMetrics.efficiency_score}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-medium ${getScoreColor(qualityMetrics.efficiency_score)}`}>
                          {qualityMetrics.efficiency_score}/100
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Best Practices:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getScoreColor(qualityMetrics.best_practices_score) === 'text-green-600' ? 'bg-green-500' : getScoreColor(qualityMetrics.best_practices_score) === 'text-yellow-600' ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${qualityMetrics.best_practices_score}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-medium ${getScoreColor(qualityMetrics.best_practices_score)}`}>
                          {qualityMetrics.best_practices_score}/100
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Suggestions */}
                {qualityMetrics.suggestions.length > 0 && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-medium text-green-800 mb-3 flex items-center">
                      <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Improvement Suggestions
                    </h4>
                    <ul className="space-y-2">
                      {qualityMetrics.suggestions.map((suggestion, index) => (
                        <li key={index} className="text-sm text-green-700 flex items-start">
                          <span className="mr-2">•</span>
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Code Smells */}
                {qualityMetrics.code_smells.length > 0 && (
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-medium text-yellow-800 mb-3 flex items-center">
                      <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      Code Issues
                    </h4>
                    <ul className="space-y-2">
                      {qualityMetrics.code_smells.map((smell, index) => (
                        <li key={index} className="text-sm text-yellow-700 flex items-start">
                          <span className="mr-2">⚠</span>
                          <span>{smell}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : qualityLoading ? (
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="animate-pulse space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
                <p className="text-sm text-gray-500">
                  Code quality analysis not available for this submission
                </p>
              </div>
            )}

            {/* Language Statistics */}
            {performanceComparison?.language_distribution && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Language Distribution</h4>
                <div className="space-y-2">
                  {Object.entries(performanceComparison.language_distribution)
                    .sort(([,a], [,b]) => (b as number) - (a as number))
                    .map(([language, percentage]) => (
                      <div key={language} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">
                          {CodingService.getLanguageDisplayName(language as any)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="h-2 bg-indigo-500 rounded-full"
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium w-8 text-right">
                            {(percentage as number).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default SubmissionAnalytics;