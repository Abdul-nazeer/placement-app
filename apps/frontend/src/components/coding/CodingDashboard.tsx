import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
// Using inline SVG icons since some heroicons are not available
import { CodingService } from '../../services/coding';
import { UserCodingStats } from '../../types/coding';
import ChallengeBrowser from './ChallengeBrowser';
import SubmissionHistory from './SubmissionHistory';

interface CodingDashboardProps {
  activeTab?: 'challenges' | 'submissions' | 'stats';
}

const CodingDashboard = ({ activeTab = 'challenges' }: CodingDashboardProps) => {
  const [currentTab, setCurrentTab] = useState(activeTab);

  // Fetch user coding statistics
  const { data: userStats, isLoading: statsLoading } = useQuery({
    queryKey: ['user-coding-stats'],
    queryFn: CodingService.getUserStats
  });

  // Fetch recent challenges for quick access
  const { data: recentChallenges } = useQuery({
    queryKey: ['recent-challenges'],
    queryFn: () => CodingService.getChallenges({ limit: 5, offset: 0 })
  });

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSuccessRate = () => {
    if (!userStats || userStats.total_submissions === 0) return 0;
    return (userStats.successful_submissions / userStats.total_submissions) * 100;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Coding Challenges</h1>
              <p className="mt-1 text-sm text-gray-500">
                Practice coding problems and improve your programming skills
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/coding/leaderboard"
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
                Leaderboard
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Overview */}
        {userStats && !statsLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Problems Solved
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {userStats.challenges_solved}
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
                    <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Success Rate
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {getSuccessRate().toFixed(1)}%
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
                    <svg className="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Average Score
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {userStats.average_score.toFixed(1)}%
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
                    <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 1-4 4-4 5 0 5 4 5 4s1.657 1.657 0 8.657z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Favorite Language
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {userStats.favorite_language ? 
                          CodingService.getLanguageDisplayName(userStats.favorite_language as any) : 
                          'None'
                        }
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Quick Start</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Random Challenge */}
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white mb-4">
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">Random Challenge</h4>
                <p className="text-sm text-gray-500 mb-4">
                  Get a random coding problem to solve
                </p>
                <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                  Start Random
                </button>
              </div>

              {/* Daily Challenge */}
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white mb-4">
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">Daily Challenge</h4>
                <p className="text-sm text-gray-500 mb-4">
                  Solve today's featured problem
                </p>
                <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
                  Daily Problem
                </button>
              </div>

              {/* Study Plan */}
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-md bg-yellow-500 text-white mb-4">
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">Study Plan</h4>
                <p className="text-sm text-gray-500 mb-4">
                  Follow a structured learning path
                </p>
                <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700">
                  View Plans
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Tabs */}
        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setCurrentTab('challenges')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  currentTab === 'challenges'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Browse Challenges
              </button>
              <button
                onClick={() => setCurrentTab('submissions')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  currentTab === 'submissions'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                My Submissions
              </button>
              <button
                onClick={() => setCurrentTab('stats')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  currentTab === 'stats'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Statistics
              </button>
            </nav>
          </div>

          <div className="p-6">
            {currentTab === 'challenges' && (
              <ChallengeBrowser />
            )}

            {currentTab === 'submissions' && (
              <SubmissionHistory />
            )}

            {currentTab === 'stats' && userStats && (
              <div className="space-y-6">
                {/* Difficulty Breakdown */}
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Problems by Difficulty</h4>
                  <div className="grid grid-cols-3 gap-4">
                    {Object.entries(userStats.difficulty_breakdown).map(([difficulty, count]) => (
                      <div key={difficulty} className="text-center">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(difficulty)}`}>
                          {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                        </div>
                        <div className="mt-2 text-2xl font-bold text-gray-900">{count as number}</div>
                        <div className="text-sm text-gray-500">solved</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Submissions */}
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h4>
                  <div className="space-y-3">
                    {userStats.recent_submissions.slice(0, 5).map((submission) => (
                      <div key={submission.id} className="flex items-center justify-between p-3 bg-white rounded border">
                        <div className="flex items-center space-x-3">
                          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${CodingService.getStatusColor(submission.status)}`}>
                            {submission.status}
                          </span>
                          <span className="text-sm font-medium text-gray-900">
                            {CodingService.getLanguageDisplayName(submission.language)}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>Score: {submission.score.toFixed(1)}%</span>
                          <span>{new Date(submission.submitted_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Challenges Sidebar */}
        {recentChallenges && currentTab === 'challenges' && (
          <div className="mt-8 bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recently Added</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentChallenges.challenges.slice(0, 3).map((challenge) => (
                  <div key={challenge.id} className="flex items-center justify-between">
                    <div>
                      <Link
                        to={`/coding/challenges/${challenge.id}`}
                        className="text-sm font-medium text-gray-900 hover:text-indigo-600"
                      >
                        {challenge.title}
                      </Link>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getDifficultyColor(challenge.difficulty)}`}>
                          {challenge.difficulty}
                        </span>
                        <span className="text-xs text-gray-500">{challenge.category}</span>
                      </div>
                    </div>
                    <Link
                      to={`/coding/challenges/${challenge.id}`}
                      className="text-xs text-indigo-600 hover:text-indigo-800"
                    >
                      Solve →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodingDashboard;