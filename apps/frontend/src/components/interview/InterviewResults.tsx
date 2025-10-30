import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  ChartBarIcon,
  DocumentArrowDownIcon,
  PlayIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  ClockIcon,
  MicrophoneIcon,
  VideoCameraIcon
} from '@heroicons/react/24/outline';
import { InterviewService } from '../../services/interview';
import {
  InterviewSessionWithDetails,
  InterviewResponse,
  InterviewAnalytics,
  InterviewFeedback
} from '../../types/interview';

export const InterviewResults: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  
  const [session, setSession] = useState<InterviewSessionWithDetails | null>(null);
  const [analytics, setAnalytics] = useState<InterviewAnalytics | null>(null);
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'detailed' | 'feedback'>('overview');
  const [selectedResponse, setSelectedResponse] = useState<InterviewResponse | null>(null);

  useEffect(() => {
    if (sessionId) {
      loadResults();
    }
  }, [sessionId]);

  const loadResults = async () => {
    try {
      setLoading(true);
      
      const [sessionData, analyticsData, feedbackData] = await Promise.all([
        InterviewService.getSession(sessionId!),
        InterviewService.getSessionAnalytics(sessionId!),
        InterviewService.getSessionFeedback(sessionId!)
      ]);
      
      setSession(sessionData);
      setAnalytics(analyticsData);
      setFeedback(feedbackData);
      
    } catch (err) {
      setError('Failed to load interview results');
      console.error('Results load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportResults = async () => {
    try {
      const blob = await InterviewService.exportSession(sessionId!, 'pdf');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `interview-results-${sessionId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error || 'Session not found'}</p>
          <button
            onClick={() => navigate('/interview')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/interview')}
            className="mr-4 p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeftIcon className="h-6 w-6" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Interview Results</h1>
            <p className="text-gray-600 mt-2">
              {session.title} • {session.company_name && `${session.company_name} • `}
              {new Date(session.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        <button
          onClick={handleExportResults}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
          Export Report
        </button>
      </div>

      {/* Overall Score Card */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBgColor(session.overall_score || 0)} mb-4`}>
              <span className={`text-2xl font-bold ${getScoreColor(session.overall_score || 0)}`}>
                {Math.round(session.overall_score || 0)}
              </span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Overall Score</h3>
            <p className="text-sm text-gray-600">Out of 100</p>
          </div>
          
          <div className="text-center">
            <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBgColor(session.communication_score || 0)} mb-4`}>
              <MicrophoneIcon className={`h-8 w-8 ${getScoreColor(session.communication_score || 0)}`} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Communication</h3>
            <p className="text-sm text-gray-600">{Math.round(session.communication_score || 0)}%</p>
          </div>
          
          <div className="text-center">
            <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBgColor(session.technical_score || 0)} mb-4`}>
              <ChartBarIcon className={`h-8 w-8 ${getScoreColor(session.technical_score || 0)}`} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Technical</h3>
            <p className="text-sm text-gray-600">{Math.round(session.technical_score || 0)}%</p>
          </div>
          
          <div className="text-center">
            <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${getScoreBgColor(session.behavioral_score || 0)} mb-4`}>
              <TrophyIcon className={`h-8 w-8 ${getScoreColor(session.behavioral_score || 0)}`} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Behavioral</h3>
            <p className="text-sm text-gray-600">{Math.round(session.behavioral_score || 0)}%</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'overview', label: 'Overview' },
              { key: 'detailed', label: 'Detailed Analysis' },
              { key: 'feedback', label: 'AI Feedback' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
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

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Session Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Summary</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Duration:</span>
                <span className="font-medium">
                  {session.end_time && session.start_time
                    ? formatDuration(
                        (new Date(session.end_time).getTime() - new Date(session.start_time).getTime()) / 1000
                      )
                    : 'N/A'}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Questions Answered:</span>
                <span className="font-medium">
                  {session.responses.length} / {session.question_count}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Interview Type:</span>
                <span className="font-medium capitalize">
                  {session.interview_type.replace('_', ' ')}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Difficulty Level:</span>
                <span className="font-medium capitalize">{session.difficulty_level}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Recording:</span>
                <div className="flex items-center space-x-2">
                  {session.enable_video_recording && (
                    <VideoCameraIcon className="h-4 w-4 text-green-600" />
                  )}
                  {session.enable_audio_recording && (
                    <MicrophoneIcon className="h-4 w-4 text-green-600" />
                  )}
                  <span className="text-sm text-gray-600">
                    {session.enable_video_recording ? 'Video' : 'Audio'} recorded
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Breakdown */}
          {analytics && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Breakdown</h3>
              
              <div className="space-y-4">
                {Object.entries(analytics.category_performance).map(([category, score]) => (
                  <div key={category}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600 capitalize">
                        {category.replace('_', ' ')}
                      </span>
                      <span className="font-medium">{Math.round(score)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'detailed' && (
        <div className="space-y-6">
          {/* Question-by-Question Analysis */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Question-by-Question Analysis</h3>
            </div>
            
            <div className="divide-y divide-gray-200">
              {session.responses.map((response, index) => {
                const question = session.questions.find(q => q.id === response.question_id);
                if (!question) return null;
                
                return (
                  <div key={response.id} className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-2">
                          Question {index + 1}: {question.category.replace('_', ' ')}
                        </h4>
                        <p className="text-gray-700 mb-3">{question.question_text}</p>
                      </div>
                      
                      <div className="ml-4 text-right">
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${
                          (response.overall_score || 0) >= 80
                            ? 'bg-green-100 text-green-800'
                            : (response.overall_score || 0) >= 60
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {Math.round(response.overall_score || 0)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="text-sm">
                        <span className="text-gray-600">Duration:</span>
                        <span className="ml-2 font-medium">
                          {formatDuration(response.response_duration)}
                        </span>
                      </div>
                      
                      <div className="text-sm">
                        <span className="text-gray-600">Thinking Time:</span>
                        <span className="ml-2 font-medium">
                          {formatDuration(response.thinking_time)}
                        </span>
                      </div>
                      
                      {response.speech_pace && (
                        <div className="text-sm">
                          <span className="text-gray-600">Speech Pace:</span>
                          <span className="ml-2 font-medium">
                            {Math.round(response.speech_pace)} WPM
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {/* Detailed Scores */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      {response.communication_score && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">Communication</span>
                            <span className="font-medium">{Math.round(response.communication_score)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-blue-600 h-1.5 rounded-full"
                              style={{ width: `${response.communication_score}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                      
                      {response.content_score && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">Content</span>
                            <span className="font-medium">{Math.round(response.content_score)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-green-600 h-1.5 rounded-full"
                              style={{ width: `${response.content_score}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                      
                      {response.technical_accuracy && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">Technical</span>
                            <span className="font-medium">{Math.round(response.technical_accuracy * 100)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-purple-600 h-1.5 rounded-full"
                              style={{ width: `${response.technical_accuracy * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* AI Feedback */}
                    {response.ai_feedback && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h5 className="font-medium text-gray-900 mb-2">AI Feedback:</h5>
                        <p className="text-gray-700 text-sm">{response.ai_feedback}</p>
                      </div>
                    )}
                    
                    {/* Strengths and Weaknesses */}
                    {(response.strengths.length > 0 || response.weaknesses.length > 0) && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        {response.strengths.length > 0 && (
                          <div>
                            <h5 className="font-medium text-green-800 mb-2 flex items-center">
                              <CheckCircleIcon className="h-4 w-4 mr-1" />
                              Strengths
                            </h5>
                            <ul className="text-sm text-gray-700 space-y-1">
                              {response.strengths.map((strength, idx) => (
                                <li key={idx} className="flex items-start">
                                  <span className="text-green-600 mr-2">•</span>
                                  {strength}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {response.weaknesses.length > 0 && (
                          <div>
                            <h5 className="font-medium text-red-800 mb-2 flex items-center">
                              <XCircleIcon className="h-4 w-4 mr-1" />
                              Areas for Improvement
                            </h5>
                            <ul className="text-sm text-gray-700 space-y-1">
                              {response.weaknesses.map((weakness, idx) => (
                                <li key={idx} className="flex items-start">
                                  <span className="text-red-600 mr-2">•</span>
                                  {weakness}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'feedback' && feedback && (
        <div className="space-y-6">
          {/* Overall Feedback */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Performance Feedback</h3>
            <p className="text-gray-700 leading-relaxed">{feedback.overall_feedback}</p>
          </div>

          {/* Category-specific Feedback */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <MicrophoneIcon className="h-5 w-5 mr-2 text-blue-600" />
                Communication Feedback
              </h4>
              <p className="text-gray-700">{feedback.communication_feedback}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <ChartBarIcon className="h-5 w-5 mr-2 text-green-600" />
                Technical Feedback
              </h4>
              <p className="text-gray-700">{feedback.technical_feedback}</p>
            </div>
          </div>

          {/* Improvement Suggestions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
              <LightBulbIcon className="h-5 w-5 mr-2 text-yellow-600" />
              Improvement Suggestions
            </h4>
            <ul className="space-y-3">
              {feedback.improvement_suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-yellow-600 mr-3 mt-1">•</span>
                  <span className="text-gray-700">{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Next Steps */}
          <div className="bg-blue-50 rounded-lg p-6">
            <h4 className="font-semibold text-blue-900 mb-4">Recommended Next Steps</h4>
            <ul className="space-y-2">
              {feedback.next_steps.map((step, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-600 mr-3 mt-1">→</span>
                  <span className="text-blue-800">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4 mt-8">
        <button
          onClick={() => navigate('/interview/create')}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          Practice Again
        </button>
        
        <button
          onClick={() => navigate('/interview')}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};