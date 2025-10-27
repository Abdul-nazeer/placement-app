/**
 * Resume template gallery with filtering and preview
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Star, 
  Crown, 
  Eye, 
  Download,
  CheckCircle,
  Grid,
  List
} from 'lucide-react';
import { resumeService } from '../../services/resume';
import { ResumeTemplate, ResumeTemplateFilters } from '../../types/resume';

interface ResumeTemplateGalleryProps {
  onSelectTemplate?: (template: ResumeTemplate) => void;
  onPreviewTemplate?: (template: ResumeTemplate) => void;
  className?: string;
}

export const ResumeTemplateGallery = ({
  onSelectTemplate,
  onPreviewTemplate,
  className = '',
}: ResumeTemplateGalleryProps) => {
  const [templates, setTemplates] = useState([]);
  const [filteredTemplates, setFilteredTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [viewMode, setViewMode] = useState('grid');
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [templates, searchQuery, filters]);

  const loadTemplates = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await resumeService.getResumeTemplates();
      setTemplates(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load templates');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...templates];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(template =>
        template.name.toLowerCase().includes(query) ||
        template.description?.toLowerCase().includes(query) ||
        template.category?.toLowerCase().includes(query) ||
        template.industry?.toLowerCase().includes(query)
      );
    }

    // Category filter
    if (filters.category) {
      filtered = filtered.filter(template => template.category === filters.category);
    }

    // Industry filter
    if (filters.industry) {
      filtered = filtered.filter(template => template.industry === filters.industry);
    }

    // ATS friendly filter
    if (filters.ats_friendly !== undefined) {
      const threshold = filters.ats_friendly ? 80 : 0;
      filtered = filtered.filter(template => template.ats_friendly_score >= threshold);
    }

    // Sort by popularity
    filtered.sort((a, b) => b.popularity_score - a.popularity_score);

    setFilteredTemplates(filtered);
  };

  const handleSelectTemplate = (template: ResumeTemplate) => {
    setSelectedTemplate(template.id);
    onSelectTemplate?.(template);
  };

  const getUniqueValues = (key: keyof ResumeTemplate) => {
    const values = templates
      .map(template => template[key])
      .filter((value, index, array) => value && array.indexOf(value) === index);
    return values as string[];
  };

  const renderStars = (score: number) => {
    const stars = Math.round(score / 20); // Convert 0-100 to 0-5 stars
    return (
      <div className="flex items-center">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-3 h-3 ${
              i < stars ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-xs text-gray-600">({score.toFixed(0)})</span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading templates...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center mb-4">
          <CheckCircle className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Error Loading Templates</h3>
        </div>
        <p className="text-red-700 mb-4">{error}</p>
        <button
          onClick={loadTemplates}
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
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Resume Templates</h2>
          <p className="text-gray-600">Choose from professional, ATS-friendly templates</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg ${
              viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg ${
              viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          <select
            value={filters.category || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value || undefined }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {getUniqueValues('category').map(category => (
              <option key={category} value={category}>
                {category?.charAt(0).toUpperCase() + category?.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={filters.industry || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, industry: e.target.value || undefined }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Industries</option>
            {getUniqueValues('industry').map(industry => (
              <option key={industry} value={industry}>
                {industry?.charAt(0).toUpperCase() + industry?.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={filters.ats_friendly === undefined ? '' : filters.ats_friendly.toString()}
            onChange={(e) => setFilters(prev => ({ 
              ...prev, 
              ats_friendly: e.target.value === '' ? undefined : e.target.value === 'true'
            }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Templates</option>
            <option value="true">ATS Friendly</option>
            <option value="false">Creative</option>
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-gray-600">
          {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} found
        </p>
        
        {filters.ats_friendly && (
          <div className="flex items-center text-green-600 text-sm">
            <CheckCircle className="w-4 h-4 mr-1" />
            ATS Friendly
          </div>
        )}
      </div>

      {/* Templates Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTemplates.map((template) => (
            <div
              key={template.id}
              className={`bg-white border rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer ${
                selectedTemplate === template.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => handleSelectTemplate(template)}
            >
              {/* Template Preview */}
              <div className="aspect-[3/4] bg-gray-100 relative">
                {template.preview_image ? (
                  <img
                    src={template.preview_image}
                    alt={template.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <Eye className="w-8 h-8" />
                  </div>
                )}
                
                {/* Premium Badge */}
                {template.is_premium && (
                  <div className="absolute top-2 right-2 bg-yellow-500 text-white px-2 py-1 rounded-full text-xs flex items-center">
                    <Crown className="w-3 h-3 mr-1" />
                    Pro
                  </div>
                )}

                {/* ATS Badge */}
                {template.ats_friendly_score >= 80 && (
                  <div className="absolute top-2 left-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    ATS
                  </div>
                )}

                {/* Overlay Actions */}
                <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center opacity-0 hover:opacity-100">
                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onPreviewTemplate?.(template);
                      }}
                      className="px-3 py-2 bg-white text-gray-900 rounded-lg hover:bg-gray-100 flex items-center space-x-1"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Preview</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectTemplate(template);
                      }}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                    >
                      <Download className="w-4 h-4" />
                      <span>Use</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Template Info */}
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1">{template.name}</h3>
                {template.description && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">{template.description}</p>
                )}
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {template.category && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                        {template.category}
                      </span>
                    )}
                    {template.industry && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                        {template.industry}
                      </span>
                    )}
                  </div>
                  
                  {renderStars(template.popularity_score)}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTemplates.map((template) => (
            <div
              key={template.id}
              className={`bg-white border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer ${
                selectedTemplate === template.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => handleSelectTemplate(template)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                    
                    {template.is_premium && (
                      <span className="bg-yellow-500 text-white px-2 py-1 rounded-full text-xs flex items-center">
                        <Crown className="w-3 h-3 mr-1" />
                        Pro
                      </span>
                    )}
                    
                    {template.ats_friendly_score >= 80 && (
                      <span className="bg-green-500 text-white px-2 py-1 rounded-full text-xs flex items-center">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        ATS Friendly
                      </span>
                    )}
                  </div>
                  
                  {template.description && (
                    <p className="text-gray-600 mb-3">{template.description}</p>
                  )}
                  
                  <div className="flex items-center space-x-4">
                    {template.category && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                        {template.category}
                      </span>
                    )}
                    {template.industry && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                        {template.industry}
                      </span>
                    )}
                    {renderStars(template.popularity_score)}
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-6">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onPreviewTemplate?.(template);
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
                  >
                    <Eye className="w-4 h-4" />
                    <span>Preview</span>
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectTemplate(template);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Use Template</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search criteria or filters
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setFilters({});
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
};