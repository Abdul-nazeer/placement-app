/**
 * Resume version control and history management
 */

import React, { useState, useEffect } from 'react';
import { 
  History, 
  Download, 
  Eye, 
  GitBranch, 
  Clock, 
  TrendingUp, 
  TrendingDown,
  Minus,
  Plus,
  RotateCcw,
  FileText
} from 'lucide-react';
import { resumeService } from '../../services/resume';
import { ResumeVersion } from '../../types/resume';

interface ResumeVersionHistoryProps {
  resumeId: string;
  onRestoreVersion?: (version: ResumeVersion) => void;
  onPreviewVersion?: (version: ResumeVersion) => void;
  className?: string;
}

export const ResumeVersionHistory = ({
  resumeId,
  onRestoreVersion,
  onPreviewVersion,
  className = '',
}: ResumeVersionHistoryProps) => {
  const [versions, setVersions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [compareMode, setCompareMode] = useState(false);

  useEffect(() => {
    loadVersions();
  }, [resumeId]);

  const loadVersions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await resumeService.getResumeVersions(resumeId);
      setVersions(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load version history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVersionSelect = (versionId: string) => {
    if (compareMode) {
      setSelectedVersions(prev => {
        if (prev.includes(versionId)) {
          return prev.filter(id => id !== versionId);
        } else if (prev.length < 2) {
          return [...prev, versionId];
        } else {
          return [prev[1], versionId]; // Replace oldest selection
        }
      });
    }
  };

  const getScoreChange = (currentScore: number, previousScore?: number) => {
    if (!previousScore) return null;
    
    const change = currentScore - previousScore;
    return {
      value: change,
      percentage: ((change / previousScore) * 100).toFixed(1),
      isPositive: change > 0,
      isNeutral: Math.abs(change) < 0.1,
    };
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else if (diffInHours < 168) { // 7 days
      return `${Math.floor(diffInHours / 24)} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const renderScoreChange = (change: ReturnType<typeof getScoreChange>) => {
    if (!change || change.isNeutral) {
      return (
        <div className="flex items-center text-gray-500">
          <Minus className="w-3 h-3 mr-1" />
          <span className="text-xs">No change</span>
        </div>
      );
    }

    return (
      <div className={`flex items-center ${change.isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {change.isPositive ? (
          <TrendingUp className="w-3 h-3 mr-1" />
        ) : (
          <TrendingDown className="w-3 h-3 mr-1" />
        )}
        <span className="text-xs">
          {change.isPositive ? '+' : ''}{change.value.toFixed(1)} ({change.percentage}%)
        </span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading version history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center mb-4">
          <History className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Error Loading History</h3>
        </div>
        <p className="text-red-700 mb-4">{error}</p>
        <button
          onClick={loadVersions}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <History className="w-6 h-6 text-gray-700" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Version History</h2>
            <p className="text-gray-600">{versions.length} version{versions.length !== 1 ? 's' : ''}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setCompareMode(!compareMode);
              setSelectedVersions([]);
            }}
            className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${
              compareMode 
                ? 'bg-blue-100 border-blue-300 text-blue-700' 
                : 'border-gray-300 hover:bg-gray-50'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            <span>Compare</span>
          </button>

          {compareMode && selectedVersions.length === 2 && (
            <button
              onClick={() => {
                // Handle comparison logic here
                console.log('Compare versions:', selectedVersions);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Compare Selected
            </button>
          )}
        </div>
      </div>

      {/* Compare Mode Instructions */}
      {compareMode && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <GitBranch className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900">Compare Mode Active</h3>
              <p className="text-blue-700 text-sm mt-1">
                Select up to 2 versions to compare changes. 
                {selectedVersions.length > 0 && (
                  <span className="font-medium"> {selectedVersions.length}/2 selected</span>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Version Timeline */}
      <div className="space-y-4">
        {versions.map((version, index) => {
          const previousVersion = versions[index + 1];
          const scoreChange = version.ats_score && previousVersion?.ats_score 
            ? getScoreChange(version.ats_score, previousVersion.ats_score)
            : null;
          const isSelected = selectedVersions.includes(version.id);
          const isLatest = index === 0;

          return (
            <div
              key={version.id}
              className={`relative bg-white border rounded-lg p-6 transition-all ${
                compareMode 
                  ? `cursor-pointer hover:border-blue-300 ${isSelected ? 'border-blue-500 bg-blue-50' : ''}` 
                  : 'hover:shadow-md'
              }`}
              onClick={() => compareMode && handleVersionSelect(version.id)}
            >
              {/* Timeline Line */}
              {index < versions.length - 1 && (
                <div className="absolute left-8 top-16 w-0.5 h-8 bg-gray-200" />
              )}

              <div className="flex items-start space-x-4">
                {/* Version Icon */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  isLatest ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'
                }`}>
                  {isLatest ? (
                    <FileText className="w-4 h-4" />
                  ) : (
                    <Clock className="w-4 h-4" />
                  )}
                </div>

                {/* Version Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-medium text-gray-900">
                        Version {version.version_number}
                        {isLatest && (
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                            Current
                          </span>
                        )}
                      </h3>
                      
                      {compareMode && isSelected && (
                        <div className="w-4 h-4 bg-blue-600 rounded-full flex items-center justify-center">
                          <Plus className="w-2 h-2 text-white" />
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>{formatDate(version.created_at)}</span>
                    </div>
                  </div>

                  <p className="text-gray-600 mb-3">{version.filename}</p>

                  {/* Score and Changes */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      {version.ats_score && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">ATS Score:</span>
                          <span className={`font-medium ${resumeService.getScoreColor(version.ats_score)}`}>
                            {version.ats_score.toFixed(1)}
                          </span>
                          {scoreChange && renderScoreChange(scoreChange)}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Changes Made */}
                  {version.changes_made && Object.keys(version.changes_made).length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Changes Made:</h4>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(version.changes_made).map(([key, value]) => (
                          <span
                            key={key}
                            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                          >
                            {key}: {String(value)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  {!compareMode && (
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => onPreviewVersion?.(version)}
                        className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-sm"
                      >
                        <Eye className="w-4 h-4" />
                        <span>Preview</span>
                      </button>

                      <button
                        onClick={() => {
                          // Handle download
                          console.log('Download version:', version.id);
                        }}
                        className="flex items-center space-x-1 text-gray-600 hover:text-gray-700 text-sm"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>

                      {!isLatest && (
                        <button
                          onClick={() => onRestoreVersion?.(version)}
                          className="flex items-center space-x-1 text-green-600 hover:text-green-700 text-sm"
                        >
                          <RotateCcw className="w-4 h-4" />
                          <span>Restore</span>
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {versions.length === 0 && (
        <div className="text-center py-12">
          <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Version History</h3>
          <p className="text-gray-600">
            Version history will appear here as you make changes to your resume
          </p>
        </div>
      )}
    </div>
  );
};