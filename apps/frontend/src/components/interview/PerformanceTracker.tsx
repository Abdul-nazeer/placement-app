import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CalendarIcon,
  ClockIcon,
  AcademicCapIcon,
  UserGroupIcon,
  BriefcaseIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { InterviewService } from '../../services/interview';
import {
  InterviewAnalytics,
  InterviewSessionSummary,
  InterviewType,
  QuestionCategory
} from '../../types/interview';

export const PerformanceTracker: React.FC = () => {
  const [analytics, setAnalytics] = useState<InterviewAnalytics | null>(null);
  const [recentSessions, setRecentSessions] = useState<InterviewSessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'quarter' | 'year'>('month');

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      const [analyticsData, sessionsData] = await Promise.all([
        InterviewService.getUserAnalytics(),
        InterviewService.getUserSessions(10, 0, 'completed')
      ]);
      
      setAnalytics(analyticsData);
      setRecentSessions(sessionsData.sessions);
      
    } catch (err) {
      setError('Failed to load performance analytics');
      console.error('Analytics load error:', err);
    } finally {
      setLoading(false);
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

  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <TrendingUpIcon className="h-4 w-4 text-green-600" />;
    } else if (trend 