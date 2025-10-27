/**
 * Resume analysis dashboard with detailed insights and actionable recommendations
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Target,
  FileText,
  Lightbulb,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { resumeService } from '../../services/resume';
import { ResumeAnalysisResponse, OptimizationSuggestion } from '../../types/resume';

interface ResumeAnalysisDashboardProps {
  resumeId: string;
  onOptimize?: () => void;
  className?: string;
}

export const ResumeAnalysisDashboard = ({
  resumeId,
  onOptimize,
  className = '',
}: ResumeAnalysisDashboardProps) => {
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalysis();
  }, [resumeId]);

  const loadAnalysis = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await resumeService.getResumeAnalysis(resumeId);
      setAnalysis(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReanalyze = async () => {
    try {
      setIsReanalyzing(true);
      await resumeService.reanalyzeResume(resumeId);
      // Poll for updated results
      setTimeout(loadAnalysis, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reanalyze resume');
    } finally {
      setIsReanalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'medium':
        return <Target className="w-4 h-4 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <Lightbulb className="w-4 h-4 text-blue-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center mb-4">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Analysis Error</h3>
        </div>
        <p className="text-red-700 mb-4">{error}</p>
        <button
          onClick={loadAnalysis}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className={`text-center p-8 ${className}`}>
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No analysis available</p>
      </div>
    );
  }

  const { analysis_results } = analysis;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Resume Analysis</h2>
          <p className="text-gray-600">{analysis.filename}</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleReanalyze}
            disabled={isReanalyzing}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isReanalyzing ? 'animate-spin' : ''}`} />
            <span>Reanalyze</span>
          </button>
          
          {onOptimize && (
            <button
              onClick={onOptimize}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <TrendingUp className="w-4 h-4" />
              <span>Optimize</span>
            </button>
          )}
        </div>
      </div>

      {/* Overall Score */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Overall Score</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBackground(analysis_results.overall_score)} ${getScoreColor(analysis_results.overall_score)}`}>
            {analysis_results.overall_score.toFixed(1)}/100
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              analysis_results.overall_score >= 80 ? 'bg-green-500' :
              analysis_results.overall_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${analysis_results.overall_score}%` }}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold ${getScoreColor(analysis_results.ats_analysis.overall_score)}`}>
              {analysis_results.ats_analysis.overall_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">ATS Score</div>
          </div>
          
          <div className="text-center">
            <div className={`text-2xl font-bold ${getScoreColor(analysis_results.content_analysis.readability_score)}`}>
              {analysis_results.content_analysis.readability_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Content Quality</div>
          </div>
          
          <div className="text-center">
            <div className={`text-2xl font-bold ${getScoreColor(analysis_results.industry_match_score || 0)}`}>
              {(analysis_results.industry_match_score || 0).toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Industry Match</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'ats', label: 'ATS Analysis', icon: Target },
            { id: 'content', label: 'Content Quality', icon: FileText },
            { id: 'suggestions', label: 'Suggestions', icon: Lightbulb },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {analysis_results.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                    <span className="text-green-700">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Areas for Improvement */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Areas for Improvement
              </h3>
              <ul className="space-y-2">
                {analysis_results.weaknesses.map((weakness, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                    <span className="text-yellow-700">{weakness}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'ats' && (
          <div className="space-y-6">
            {/* ATS Scores Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Keyword Score</h4>
                <div className={`text-2xl font-bold ${getScoreColor(analysis_results.ats_analysis.keyword_score)}`}>
                  {analysis_results.ats_analysis.keyword_score.toFixed(1)}
                </div>
              </div>
              
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Format Score</h4>
                <div className={`text-2xl font-bold ${getScoreColor(analysis_results.ats_analysis.format_score)}`}>
                  {analysis_results.ats_analysis.format_score.toFixed(1)}
                </div>
              </div>
              
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Structure Score</h4>
                <div className={`text-2xl font-bold ${getScoreColor(analysis_results.ats_analysis.structure_score)}`}>
                  {analysis_results.ats_analysis.structure_score.toFixed(1)}
                </div>
              </div>
            </div>

            {/* Missing Keywords */}
            {analysis_results.ats_analysis.missing_keywords.length > 0 && (
              <div className="bg-white border rounded-lg p-6">
                <h4 className="font-medium text-gray-900 mb-4">Missing Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {analysis_results.ats_analysis.missing_keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Format Issues */}
            {analysis_results.ats_analysis.format_issues.length > 0 && (
              <div className="bg-white border rounded-lg p-6">
                <h4 className="font-medium text-gray-900 mb-4">Format Issues</h4>
                <ul className="space-y-2">
                  {analysis_results.ats_analysis.format_issues.map((issue, index) => (
                    <li key={index} className="flex items-start">
                      <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span className="text-gray-700">{issue}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'content' && (
          <div className="space-y-6">
            {/* Content Scores */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Readability</h4>
                <div className={`text-2xl font-bold ${getScoreColor(analysis_results.content_analysis.readability_score)}`}>
                  {analysis_results.content_analysis.readability_score.toFixed(1)}
                </div>
              </div>
              
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Grammar</h4>
                <div className={`text-2xl font-bold ${getScoreColor(analysis_results.content_analysis.grammar_score)}`}>
                  {analysis_results.content_analysis.grammar_score.toFixed(1)}
                </div>
              </div>
              
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Impact</h4>
                <div className={`text-2xl font-bold ${getScoreColor(analysis_results.content_analysis.impact_score)}`}>
                  {analysis_results.content_analysis.impact_score.toFixed(1)}
                </div>
              </div>
            </div>

            {/* Grammar Issues */}
            {analysis_results.content_analysis.grammar_issues.length > 0 && (
              <div className="bg-white border rounded-lg p-6">
                <h4 className="font-medium text-gray-900 mb-4">Grammar Issues</h4>
                <div className="space-y-3">
                  {analysis_results.content_analysis.grammar_issues.map((issue, index) => (
                    <div key={index} className="flex items-start p-3 bg-red-50 rounded-lg">
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                      <div>
                        <div className="font-medium text-red-800">{issue.type}</div>
                        <div className="text-red-700 text-sm">{issue.message}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Weak Phrases */}
            {analysis_results.content_analysis.weak_phrases.length > 0 && (
              <div className="bg-white border rounded-lg p-6">
                <h4 className="font-medium text-gray-900 mb-4">Weak Phrases to Improve</h4>
                <div className="flex flex-wrap gap-2">
                  {analysis_results.content_analysis.weak_phrases.map((phrase, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm"
                    >
                      {phrase}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'suggestions' && (
          <div className="space-y-4">
            {analysis.suggestions.map((suggestion, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${resumeService.getPriorityColor(suggestion.priority)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {getPriorityIcon(suggestion.priority)}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-medium capitalize">{suggestion.type.replace('_', ' ')}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          suggestion.priority === 'high' ? 'bg-red-100 text-red-800' :
                          suggestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {suggestion.priority} priority
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{suggestion.suggestion}</p>
                      <p className="text-sm text-gray-600">{suggestion.impact}</p>
                    </div>
                  </div>
                  
                  <ArrowRight className="w-4 h-4 text-gray-400 mt-1" />
                </div>
              </div>
            ))}
            
            {analysis.suggestions.length === 0 && (
              <div className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Great Job!</h3>
                <p className="text-gray-600">Your resume looks excellent. No major improvements needed.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};