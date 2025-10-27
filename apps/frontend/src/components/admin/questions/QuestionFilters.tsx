import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { QuestionFilters, QuestionType, DifficultyLevel, QuestionStatus } from '../../../types/content';
import { contentService } from '../../../services/content';

interface QuestionFiltersProps {
  filters: QuestionFilters;
  onFiltersChange: (filters: QuestionFilters) => void;
  onReset: () => void;
}

const QuestionFiltersComponent = ({
  filters,
  onFiltersChange,
  onReset,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => contentService.getCategories(),
  });

  const { data: companies } = useQuery({
    queryKey: ['companies'],
    queryFn: () => contentService.getCompanies(),
  });

  const { data: tags } = useQuery({
    queryKey: ['tags'],
    queryFn: () => contentService.getTags(),
  });

  const handleFilterChange = (key: keyof QuestionFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  const handleArrayFilterChange = (key: keyof QuestionFilters, value: string, checked: boolean) => {
    const currentArray = (filters[key] as string[]) || [];
    const newArray = checked
      ? [...currentArray, value]
      : currentArray.filter(item => item !== value);
    
    onFiltersChange({
      ...filters,
      [key]: newArray.length > 0 ? newArray : undefined,
    });
  };

  const hasActiveFilters = Object.values(filters).some(value => 
    value !== undefined && value !== null && 
    (Array.isArray(value) ? value.length > 0 : true)
  );

  return (
    <div className="bg-white shadow rounded-lg mb-6">
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">Filters</h3>
          <div className="flex items-center space-x-2">
            {hasActiveFilters && (
              <button
                onClick={onReset}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Clear all
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-sm text-indigo-600 hover:text-indigo-800"
            >
              {isExpanded ? 'Hide' : 'Show'} filters
            </button>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-4 py-4 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value || undefined)}
                placeholder="Search questions..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            {/* Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <select
                value={filters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="">All types</option>
                <option value={QuestionType.APTITUDE}>Aptitude</option>
                <option value={QuestionType.CODING}>Coding</option>
                <option value={QuestionType.COMMUNICATION}>Communication</option>
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="">All categories</option>
                {categories?.map((category) => (
                  <option key={category.id} value={category.name}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.status?.[0] || ''}
                onChange={(e) => handleFilterChange('status', e.target.value ? [e.target.value as QuestionStatus] : undefined)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="">All statuses</option>
                <option value={QuestionStatus.DRAFT}>Draft</option>
                <option value={QuestionStatus.PENDING_REVIEW}>Pending Review</option>
                <option value={QuestionStatus.APPROVED}>Approved</option>
                <option value={QuestionStatus.REJECTED}>Rejected</option>
                <option value={QuestionStatus.ARCHIVED}>Archived</option>
              </select>
            </div>
          </div>

          {/* Difficulty Levels */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Levels
            </label>
            <div className="flex flex-wrap gap-2">
              {[1, 2, 3, 4, 5].map((level) => (
                <label key={level} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.difficulty?.includes(level as DifficultyLevel) || false}
                    onChange={(e) => handleArrayFilterChange('difficulty', level.toString(), e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Level {level}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Company Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Companies
            </label>
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
              {companies?.slice(0, 10).map((company) => (
                <label key={company.id} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.company_tags?.includes(company.name) || false}
                    onChange={(e) => handleArrayFilterChange('company_tags', company.name, e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{company.name}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Success Rate Range */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Success Rate (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={filters.min_success_rate || ''}
                onChange={(e) => handleFilterChange('min_success_rate', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Success Rate (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={filters.max_success_rate || ''}
                onChange={(e) => handleFilterChange('max_success_rate', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
          </div>

          {/* Additional Filters */}
          <div className="flex flex-wrap gap-4">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={filters.is_premium === true}
                onChange={(e) => handleFilterChange('is_premium', e.target.checked ? true : undefined)}
                className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700">Premium only</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={filters.is_active === false}
                onChange={(e) => handleFilterChange('is_active', e.target.checked ? false : undefined)}
                className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700">Include inactive</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionFiltersComponent;