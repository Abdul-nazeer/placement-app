import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  ChevronLeftIcon, 
  ChevronRightIcon,
  CodeBracketIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { CodingService } from '../../services/coding';
import { CodingChallengeFilters, DifficultyLevel } from '../../types/coding';

interface ChallengeBrowserProps {
  onChallengeSelect?: (challengeId: string) => void;
}

const ChallengeBrowser = ({ onChallengeSelect }: ChallengeBrowserProps) => {
  const [filters, setFilters] = useState<CodingChallengeFilters>({
    difficulty: [],
    category: [],
    topic_tags: [],
    company_tags: [],
    search: '',
    limit: 20,
    offset: 0
  });
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'created_at' | 'difficulty' | 'title'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);

  // Fetch challenges
  const { data: challengesData, isLoading, error, refetch } = useQuery({
    queryKey: ['challenges', filters],
    queryFn: () => CodingService.getChallenges(filters),
    keepPreviousData: true
  });

  // Fetch filter options
  const { data: categories } = useQuery({
    queryKey: ['challenge-categories'],
    queryFn: CodingService.getCategories
  });

  const { data: difficulties } = useQuery({
    queryKey: ['difficulty-levels'],
    queryFn: CodingService.getDifficultyLevels
  });

  const { data: allTags } = useQuery({
    queryKey: ['all-topic-tags'],
    queryFn: async () => {
      // This would fetch all available topic tags
      const response = await fetch('/api/v1/coding/tags');
      return response.json();
    }
  });

  const { data: allCompanies } = useQuery({
    queryKey: ['all-companies'],
    queryFn: async () => {
      // This would fetch all available company tags
      const response = await fetch('/api/v1/coding/companies');
      return response.json();
    }
  });

  const totalPages = challengesData ? Math.ceil(challengesData.total / (filters.limit || 20)) : 0;

  const handleSearch = (searchTerm: string) => {
    setFilters(prev => ({ ...prev, search: searchTerm, offset: 0 }));
    setCurrentPage(1);
  };

  const handleFilterChange = (key: keyof CodingChallengeFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, offset: 0 }));
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    const offset = (page - 1) * (filters.limit || 20);
    setFilters(prev => ({ ...prev, offset }));
    setCurrentPage(page);
  };

  const clearFilters = () => {
    setFilters({
      difficulty: [],
      category: [],
      topic_tags: [],
      company_tags: [],
      search: '',
      limit: 20,
      offset: 0
    });
    setCurrentPage(1);
  };

  const getDifficultyBadge = (difficulty: DifficultyLevel) => {
    const colorClass = CodingService.getDifficultyColor(difficulty);
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
      </span>
    );
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">Failed to load challenges</div>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Coding Challenges</h1>
          <p className="mt-1 text-sm text-gray-500">
            Practice coding problems to improve your programming skills
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            Filters
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Search challenges..."
          value={filters.search || ''}
          onChange={(e) => handleSearch(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-gray-50 p-6 rounded-lg space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Difficulty Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Difficulty Level
              </label>
              <div className="space-y-2">
                {difficulties?.map((diff) => (
                  <label key={diff} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.difficulty?.includes(diff as DifficultyLevel) || false}
                      onChange={(e) => {
                        const currentDifficulties = filters.difficulty || [];
                        const newDifficulties = e.target.checked
                          ? [...currentDifficulties, diff as DifficultyLevel]
                          : currentDifficulties.filter(d => d !== diff);
                        handleFilterChange('difficulty', newDifficulties);
                      }}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700 capitalize">{diff}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Category
              </label>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {categories?.map((category) => (
                  <label key={category} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.category?.includes(category) || false}
                      onChange={(e) => {
                        const currentCategories = filters.category || [];
                        const newCategories = e.target.checked
                          ? [...currentCategories, category]
                          : currentCategories.filter(c => c !== category);
                        handleFilterChange('category', newCategories);
                      }}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Topic Tags Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Topic Tags
              </label>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {allTags?.slice(0, 10).map((tag: string) => (
                  <label key={tag} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedTags.includes(tag)}
                      onChange={(e) => {
                        const newTags = e.target.checked
                          ? [...selectedTags, tag]
                          : selectedTags.filter(t => t !== tag);
                        setSelectedTags(newTags);
                        handleFilterChange('topic_tags', newTags);
                      }}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{tag}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Company Tags Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Companies
              </label>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {allCompanies?.slice(0, 10).map((company: string) => (
                  <label key={company} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedCompanies.includes(company)}
                      onChange={(e) => {
                        const newCompanies = e.target.checked
                          ? [...selectedCompanies, company]
                          : selectedCompanies.filter(c => c !== company);
                        setSelectedCompanies(newCompanies);
                        handleFilterChange('company_tags', newCompanies);
                      }}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{company}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Sort Options */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center space-x-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                >
                  <option value="created_at">Date</option>
                  <option value="difficulty">Difficulty</option>
                  <option value="title">Title</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order
                </label>
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as any)}
                  className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                >
                  <option value="desc">Descending</option>
                  <option value="asc">Ascending</option>
                </select>
              </div>

              <div className="flex-1 flex justify-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results Summary */}
      {challengesData && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-700">
            Showing {challengesData.challenges.length} of {challengesData.total} challenges
          </p>
          <div className="text-sm text-gray-500">
            Page {currentPage} of {totalPages}
          </div>
        </div>
      )}

      {/* Challenge List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="flex space-x-2">
                  <div className="h-6 bg-gray-200 rounded w-16"></div>
                  <div className="h-6 bg-gray-200 rounded w-20"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {challengesData?.challenges.map((challenge) => (
            <div
              key={challenge.id}
              className="bg-white p-6 rounded-lg shadow border hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {onChallengeSelect ? (
                        <button
                          onClick={() => onChallengeSelect(challenge.id)}
                          className="hover:text-indigo-600 text-left"
                        >
                          {challenge.title}
                        </button>
                      ) : (
                        <Link
                          to={`/coding/challenges/${challenge.id}`}
                          className="hover:text-indigo-600"
                        >
                          {challenge.title}
                        </Link>
                      )}
                    </h3>
                    {getDifficultyBadge(challenge.difficulty)}
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center">
                      <CodeBracketIcon className="h-4 w-4 mr-1" />
                      {challenge.category}
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {new Date(challenge.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2">
                    {challenge.topic_tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        <span className="text-xs mr-1">#</span>
                        {tag}
                      </span>
                    ))}
                    {challenge.topic_tags.length > 3 && (
                      <span className="text-xs text-gray-500">
                        +{challenge.topic_tags.length - 3} more
                      </span>
                    )}
                  </div>

                  {/* Company Tags */}
                  {challenge.company_tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {challenge.company_tags.slice(0, 2).map((company) => (
                        <span
                          key={company}
                          className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800"
                        >
                          {company}
                        </span>
                      ))}
                      {challenge.company_tags.length > 2 && (
                        <span className="text-xs text-gray-500">
                          +{challenge.company_tags.length - 2} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="ml-4">
                  {onChallengeSelect ? (
                    <button
                      onClick={() => onChallengeSelect(challenge.id)}
                      className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700"
                    >
                      Solve
                    </button>
                  ) : (
                    <Link
                      to={`/coding/challenges/${challenge.id}`}
                      className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 inline-block"
                    >
                      Solve
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-5 w-5 mr-1" />
            Previous
          </button>

          <div className="flex space-x-2">
            {[...Array(Math.min(5, totalPages))].map((_, i) => {
              const pageNum = Math.max(1, currentPage - 2) + i;
              if (pageNum > totalPages) return null;
              
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    pageNum === currentPage
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRightIcon className="h-5 w-5 ml-1" />
          </button>
        </div>
      )}

      {/* Empty State */}
      {challengesData && challengesData.challenges.length === 0 && (
        <div className="text-center py-12">
          <CodeBracketIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No challenges found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search criteria or filters.
          </p>
          <div className="mt-6">
            <button
              onClick={clearFilters}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Clear Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChallengeBrowser;