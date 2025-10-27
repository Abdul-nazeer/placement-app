import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { contentService } from '../../services/content';
import { ContentAnalytics } from '../../types/content';

const AdminDashboard: React.FC = () => {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['content-analytics'],
    queryFn: contentService.getContentAnalytics,
  });

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
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
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error loading analytics
              </h3>
              <div className="mt-2 text-sm text-red-700">
                Failed to load dashboard data. Please try again.
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Questions',
      value: analytics?.total_questions || 0,
      icon: '❓',
      color: 'bg-blue-500',
    },
    {
      name: 'Total Submissions',
      value: analytics?.total_submissions || 0,
      icon: '📝',
      color: 'bg-green-500',
    },
    {
      name: 'Average Success Rate',
      value: analytics?.average_success_rate ? `${analytics.average_success_rate.toFixed(1)}%` : 'N/A',
      icon: '📊',
      color: 'bg-yellow-500',
    },
    {
      name: 'Active Categories',
      value: Object.keys(analytics?.questions_by_type || {}).length,
      icon: '📁',
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Overview of your content management system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`${stat.color} rounded-md p-3 text-white text-xl`}>
                    {stat.icon}
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Questions by Type */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Questions by Type
            </h3>
            <div className="space-y-3">
              {Object.entries(analytics?.questions_by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">{count as number}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Questions by Difficulty */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Questions by Difficulty
            </h3>
            <div className="space-y-3">
              {Object.entries(analytics?.questions_by_difficulty || {}).map(([difficulty, count]) => (
                <div key={difficulty} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      difficulty === '1' ? 'bg-green-500' :
                      difficulty === '2' ? 'bg-yellow-500' :
                      difficulty === '3' ? 'bg-orange-500' :
                      difficulty === '4' ? 'bg-red-500' : 'bg-purple-500'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-900">
                      Level {difficulty}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">{count as number}</span>
                </div>
              ))}
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
              {analytics?.top_companies?.slice(0, 5).map((company, index) => (
                <div key={company.name} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-500 mr-3">
                      #{index + 1}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {company.name}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">{company.count} questions</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Topics */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Top Topics
            </h3>
            <div className="space-y-3">
              {analytics?.top_topics?.slice(0, 5).map((topic, index) => (
                <div key={topic.name} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-500 mr-3">
                      #{index + 1}
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {topic.name}
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">{topic.count} questions</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;