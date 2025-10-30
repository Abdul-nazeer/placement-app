import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PlusIcon,
  PlayIcon,
  ClockIcon,
  ChartBarIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { InterviewService } from '../../services/interview';
import {
  InterviewSessionSummary,
  InterviewType,
  InterviewStatus,
  DifficultyLevel,
  QuestionCategory
} from '../../types/interview';

export const MockInterviewDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<InterviewSessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | InterviewStatus>('all');

  useEffect(() => {
    loadSessions();
  }, [filter]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const statusFilter = filter === 'all' ? undefined : filter;
      const data = await InterviewService.getUserSessions(20, 0, statusFilter);
      setSessions(data.sessions);
    } catch (err) {
      setError('Failed to load interview sessions');
      console.error('Sessions load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInterview = () => {
    navigate('/interview/create');
  };

  const handleStartInterview = (sessionId: string) => {
    navigate(`/interview/session/${sessionId}`);
  };

  const handleViewResults = (sessionId: string) => {
    navigate(`/interview/results/${sessionId}`);
  };

  const getStatusColor = (status: InterviewStatus) => {
    switch (status) {
      case InterviewStatus.SCHEDULED:
        return 'bg-blue-100 text-blue-800';
      case InterviewStatus.IN_PROGRESS:
        return 'bg-yellow-100 text-yellow-800';
      case InterviewStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case InterviewStatus.PAUSED:
        return 'bg-orange-100 text-orange-800';
      case InterviewStatus.CANCELLED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getInterviewTypeIcon = (type: InterviewType) => {
    switch (type) {
      case InterviewType.TECHNICAL:
        return <AcademicCapIcon className="h-5 w-5" />;
      case InterviewType.BEHAVIORAL:
        return <UserGroupIcon className="h-5 w-5" />;
      case InterviewType.HR:
        return <BriefcaseIcon className="h-5 w-5" />;
      default:
        return <DocumentTextIcon className="h-5 w-5" />;
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mock Interviews</h1>
          <p className="text-gray-600 mt-2">
            Practice with AI-powered interviews to improve your performance
          </p>
        </div>
        
        <button
          onClick={handleCreateInterview}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Interview
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <DocumentTextIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Interviews</p>
              <p className="text-2xl font-bold text-gray-900">{sessions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">
                {sessions.filter(s => s.status === InterviewStatus.COMPLETED).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg. Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {sessions.filter(s => s.overall_score).length > 0
                  ? Math.round(
                      sessions
                        .filter(s => s.overall_score)
                        .reduce((sum, s) => sum + (s.overall_score || 0), 0) /
                      sessions.filter(s => s.overall_score).length
                    )
                  : '--'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <VideoCameraIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Practice Hours</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(
                  sessions
                    .filter(s => s.actual_duration)
                    .reduce((sum, s) => sum + (s.actual_duration || 0), 0) / 60
                )}h
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'all', label: 'All Interviews' },
              { key: InterviewStatus.SCHEDULED, label: 'Scheduled' },
              { key: InterviewStatus.IN_PROGRESS, label: 'In Progress' },
              { key: InterviewStatus.COMPLETED, label: 'Completed' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  filter === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Interview Sessions List */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="text-center py-12">
          <VideoCameraIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No interviews yet</h3>
          <p className="text-gray-600 mb-6">
            Create your first mock interview to start practicing
          </p>
          <button
            onClick={handleCreateInterview}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Interview
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {sessions.map((session) => (
            <div key={session.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className="p-2 bg-gray-100 rounded-lg mr-3">
                      {getInterviewTypeIcon(session.interview_type)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{session.title}</h3>
                      <p className="text-sm text-gray-600">
                        {session.company_name && `${session.company_name} • `}
                        {session.position_title}
                      </p>
                    </div>
                  </div>
                  
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(session.status)}`}>
                    {session.status.replace('_', ' ')}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {formatDuration(session.total_duration)}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <DocumentTextIcon className="h-4 w-4 mr-1" />
                    {session.questions_answered}/{session.question_count} questions
                  </div>
                </div>

                {/* Scores */}
                {session.overall_score && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-600">Overall Score</span>
                      <span className="font-medium">{Math.round(session.overall_score)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${session.overall_score}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-3">
                  {session.status === InterviewStatus.SCHEDULED || session.status === InterviewStatus.IN_PROGRESS ? (
                    <button
                      onClick={() => handleStartInterview(session.id)}
                      className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                      <PlayIcon className="h-4 w-4 mr-2" />
                      {session.status === InterviewStatus.IN_PROGRESS ? 'Continue' : 'Start'}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleViewResults(session.id)}
                      className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                    >
                      <ChartBarIcon className="h-4 w-4 mr-2" />
                      View Results
                    </button>
                  )}
                  
                  <button
                    onClick={() => navigate(`/interview/session/${session.id}`)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                  >
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};