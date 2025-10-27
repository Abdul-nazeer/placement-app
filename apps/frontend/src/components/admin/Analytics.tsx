import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { contentService } from '../../services/content';
import { ContentAnalytics } from '../../types/content';

const Analytics: React.FC = () => {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['content-analytics'],
    queryFn: contentService.getContentAnalytics,
  });

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white shadow rounded-lg p-6">
                <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="space-y-3">
                  {[...Array(5)].map((_, j) => (
                    <div key={j} className="h-4 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-sm text-red-700">
            Failed to load analytics data. Please try again.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-1 text-sm text-gray-600">
          Detailed insights into your content performance
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-indigo-500 rounded-md p-3 text-white text-xl">
                  📚
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Questions
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics?.total_questions || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-green-500 rounded-md p-3 text-white text-xl">
                  📝
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Submissions
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics?.total_submissions || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-yellow-500 rounded-md p-3 text-white text-xl">
                  📊
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Avg Success Rate
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics?.average_success_rate ? `${analytics.average_success_rate.toFixed(1)}%` : 'N/A'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-purple-500 rounded-md p-3 text-white text-xl">
                  🏷️
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Question Types
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {Object.keys(analytics?.questions_by_type || {}).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-8">
        {/* Questions by Type */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Questions by Type
            </h3>
            <div className="space-y-4">
              {Object.entries(analytics?.questions_by_type || {}).map(([type, count]) => {
                const total = analytics?.total_questions || 1;
                const percentage = (((count as number) / total) * 100).toFixed(1);
                return (
                  <div key={type}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {type.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-500">
                        {count as number} ({percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Questions by Difficulty */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Questions by Difficulty
            </h3>
            <div className="space-y-4">
              {Object.entries(analytics?.questions_by_difficulty || {}).map(([difficulty, count]) => {
                const total = analytics?.total_questions || 1;
                const percentage = (((count as number) / total) * 100).toFixed(1);
                const colors = {
                  '1': 'bg-green-500',
                  '2': 'bg-blue-500',
                  '3': 'bg-yellow-500',
                  '4': 'bg-orange-500',
                  '5': 'bg-red-500',
                };
                return (
                  <div key={difficulty}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        Level {difficulty}
                      </span>
                      <span className="text-sm text-gray-500">
                        {count as number} ({percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`${colors[difficulty as keyof typeof colors] || 'bg-gray-500'} h-2 rounded-full`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Questions by Status */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Questions by Status
            </h3>
            <div className="space-y-4">
              {Object.entries(analytics?.questions_by_status || {}).map(([status, count]) => {
                const total = analytics?.total_questions || 1;
                const percentage = (((count as number) / total) * 100).toFixed(1);
                const colors = {
                  'draft': 'bg-gray-500',
                  'pending_review': 'bg-yellow-500',
                  'approved': 'bg-green-500',
                  'rejected': 'bg-red-500',
                  'archived': 'bg-purple-500',
                };
                return (
                  <div key={status}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {status.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-500">
                        {count as number} ({percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`${colors[status as keyof typeof colors] || 'bg-gray-500'} h-2 rounded-full`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Top Companies */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Top Companies
            </h3>
            <div className="space-y-3">
              {analytics?.top_companies?.slice(0, 10).map((company, index) => (
                <div key={company.name} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-500 mr-3 w-6">
                      #{index + 1}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {company.name}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">{company.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top Topics */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Top Topics
          </h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {analytics?.top_topics?.slice(0, 15).map((topic, index) => (
              <div key={topic.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center">
                  <span className="text-xs font-medium text-gray-500 mr-2">
                    #{index + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {topic.name}
                  </span>
                </div>
                <span className="text-sm text-gray-500 ml-2">{topic.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;