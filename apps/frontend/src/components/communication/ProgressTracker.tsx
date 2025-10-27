/**
 * Communication progress tracking component
 */

import React, { useEffect, useState } from 'react';
import {
  ChartBarIcon,
  TrendingUpIcon,
  CalendarIcon,
  ClockIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { communicationService } from '../../services/communication';
import { CommunicationProgress } from '../../types/communication';

export const ProgressTracker: React.FC = () => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState<CommunicationProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const progressData = await communicationService.getProgress();
      setProgress(progressData);
    } catch (err) {
      setError('Failed to load progress data');
      console.error('Progress load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatSkillCategory = (category: string): string => {
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getProgressColor = (level: number): string => {
    if (level >= 0.8) return 'bg-green-500';
    if (level >= 0.6) return 'bg-blue-500';
    if (level >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getProgressTextColor = (level: number): string => {
    if (level >= 0.8) return 'text-green-600';
    if (level >= 0.6) return 'text-blue-600';
    if (level >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/communication')}
            className="mr-4 p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeftIcon className="h-6 w-6" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Progress Tracking</h1>
            <p className="mt-2 text-gray-600">
              Monitor your communication skill development over time
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Progress Overview */}
      {progress.length === 0 ? (
        <div className="text-center py-12">
          <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Progress Data Yet</h3>
          <p className="text-gray-500 mb-6">
            Complete some practice sessions to start tracking your progress
          </p>
          <button
            onClick={() => navigate('/communication')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Start Practicing
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Skills Tracked</p>
                  <p className="text-2xl font-bold text-gray-900">{progress.length}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <TrendingUpIcon className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Sessions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {progress.reduce((sum, p) => sum + p.sessions_completed, 0)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <ClockIcon className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Practice Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatTime(progress.reduce((sum, p) => sum + p.total_practice_time, 0))}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <CalendarIcon className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Last Session</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatDate(
                      progress
                        .filter(p => p.last_session_date)
                        .sort((a, b) => new Date(b.last_session_date!).getTime() - new Date(a.last_session_date!).getTime())[0]?.last_session_date
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Skill Progress Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {progress.map((skillProgress) => (
              <div key={skillProgress.id} className="bg-white rounded-lg shadow">
                <div className="p-6">
                  {/* Skill Header */}
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {formatSkillCategory(skillProgress.skill_category)}
                    </h3>
                    <span className={`text-2xl font-bold ${getProgressTextColor(skillProgress.current_level)}`}>
                      {Math.round(skillProgress.current_level * 100)}%
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all duration-300 ${getProgressColor(skillProgress.current_level)}`}
                        style={{ width: `${skillProgress.current_level * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Skill Stats */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Sessions Completed</p>
                      <p className="font-semibold text-gray-900">{skillProgress.sessions_completed}</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-500">Practice Time</p>
                      <p className="font-semibold text-gray-900">
                        {formatTime(skillProgress.total_practice_time)}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-gray-500">Last Session</p>
                      <p className="font-semibold text-gray-900">
                        {formatDate(skillProgress.last_session_date)}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-gray-500">Improvement Rate</p>
                      <p className={`font-semibold ${
                        skillProgress.improvement_rate && skillProgress.improvement_rate > 0 
                          ? 'text-green-600' 
                          : skillProgress.improvement_rate && skillProgress.improvement_rate < 0
                          ? 'text-red-600'
                          : 'text-gray-900'
                      }`}>
                        {skillProgress.improvement_rate 
                          ? `${skillProgress.improvement_rate > 0 ? '+' : ''}${Math.round(skillProgress.improvement_rate * 100)}%`
                          : 'N/A'
                        }
                      </p>
                    </div>
                  </div>

                  {/* Progress Level Description */}
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">
                      {skillProgress.current_level >= 0.8 
                        ? 'Excellent! You have mastered this skill.'
                        : skillProgress.current_level >= 0.6
                        ? 'Good progress! Keep practicing to reach mastery.'
                        : skillProgress.current_level >= 0.4
                        ? 'Making progress. Focus on consistent practice.'
                        : 'Getting started. Regular practice will help you improve quickly.'
                      }
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/communication')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Continue Practice
            </button>
            
            <button
              onClick={() => navigate('/communication/prompts')}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Browse Scenarios
            </button>
          </div>
        </div>
      )}
    </div>
  );
};