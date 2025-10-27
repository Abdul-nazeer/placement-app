/**
 * Communication prompt browser component
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  PlayIcon,
  ClockIcon,
  TagIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { communicationService } from '../../services/communication';
import { CommunicationPrompt, CommunicationFilters } from '../../types/communication';

export const PromptBrowser: React.FC = () => {
  const navigate = useNavigate();
  const [prompts, setPrompts] = useState<CommunicationPrompt[]>([]);
  const [filteredPrompts, setFilteredPrompts] = useState<CommunicationPrompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<CommunicationFilters>({});
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadPrompts();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [prompts, searchTerm, filters]);

  const loadPrompts = async () => {
    try {
      setLoading(true);
      const promptsData = await communicationService.getPrompts();
      setPrompts(promptsData);
    } catch (err) {
      setError('Failed to load practice scenarios');
      console.error('Prompts load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...prompts];

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(prompt =>
        prompt.title.toLowerCase().includes(term) ||
        prompt.description.toLowerCase().includes(term) ||
        prompt.prompt_text.toLowerCase().includes(term)
      );
    }

    // Apply category filter
    if (filters.category) {
      filtered = filtered.filter(prompt => prompt.category === filters.category);
    }

    // Apply difficulty filter
    if (filters.difficulty_level) {
      filtered = filtered.filter(prompt => prompt.difficulty_level === filters.difficulty_level);
    }

    setFilteredPrompts(filtered);
  };

  const startPracticeSession = async (promptId: string) => {
    try {
      const sessionData = {
        session_type: 'hr_interview' as const,
        prompt_id: promptId
      };
      
      const session = await communicationService.createSession(sessionData);
      navigate(`/communication/practice/${session.id}`);
    } catch (err) {
      setError('Failed to start practice session');
      console.error('Session creation error:', err);
    }
  };

  const getCategoryLabel = (category: string): string => {
    switch (category) {
      case 'hr_interview':
        return 'HR Interview';
      case 'behavioral':
        return 'Behavioral';
      case 'presentation':
        return 'Presentation';
      default:
        return category;
    }
  };

  const getDifficultyColor = (level: number): string => {
    switch (level) {
      case 1:
        return 'bg-green-100 text-green-800';
      case 2:
        return 'bg-blue-100 text-blue-800';
      case 3:
        return 'bg-yellow-100 text-yellow-800';
      case 4:
        return 'bg-orange-100 text-orange-800';
      case 5:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (level: number): string => {
    const labels = ['', 'Beginner', 'Easy', 'Medium', 'Hard', 'Expert'];
    return labels[level] || 'Unknown';
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
            <h1 className="text-3xl font-bold text-gray-900">Practice Scenarios</h1>
            <p className="mt-2 text-gray-600">
              Choose from {filteredPrompts.length} structured communication exercises
            </p>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search scenarios..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filters
            </button>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Category Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={filters.category || ''}
                    onChange={(e) => setFilters({ ...filters, category: e.target.value as any || undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Categories</option>
                    <option value="hr_interview">HR Interview</option>
                    <option value="behavioral">Behavioral</option>
                    <option value="presentation">Presentation</option>
                  </select>
                </div>

                {/* Difficulty Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Difficulty
                  </label>
                  <select
                    value={filters.difficulty_level || ''}
                    onChange={(e) => setFilters({ ...filters, difficulty_level: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Levels</option>
                    <option value="1">Beginner</option>
                    <option value="2">Easy</option>
                    <option value="3">Medium</option>
                    <option value="4">Hard</option>
                    <option value="5">Expert</option>
                  </select>
                </div>

                {/* Clear Filters */}
                <div className="flex items-end">
                  <button
                    onClick={() => {
                      setFilters({});
                      setSearchTerm('');
                    }}
                    className="w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Prompts Grid */}
      {filteredPrompts.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No scenarios found matching your criteria</p>
          <button
            onClick={() => {
              setFilters({});
              setSearchTerm('');
            }}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPrompts.map((prompt) => (
            <div key={prompt.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                    {prompt.title}
                  </h3>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDifficultyColor(prompt.difficulty_level)}`}>
                    {getDifficultyLabel(prompt.difficulty_level)}
                  </span>
                </div>

                {/* Description */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {prompt.description}
                </p>

                {/* Metadata */}
                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span className="flex items-center">
                    <TagIcon className="h-4 w-4 mr-1" />
                    {getCategoryLabel(prompt.category)}
                  </span>
                  
                  {prompt.time_limit && (
                    <span className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {Math.floor(prompt.time_limit / 60)}m
                    </span>
                  )}
                </div>

                {/* Tags */}
                {prompt.tags && prompt.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {prompt.tags.slice(0, 3).map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                    {prompt.tags.length > 3 && (
                      <span className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                        +{prompt.tags.length - 3} more
                      </span>
                    )}
                  </div>
                )}

                {/* Action Button */}
                <button
                  onClick={() => startPracticeSession(prompt.id)}
                  className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Start Practice
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};