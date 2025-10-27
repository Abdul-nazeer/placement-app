/**
 * Main resume optimization dashboard
 */

import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  BarChart3, 
  Settings, 
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Eye,
  Download,
  Trash2,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Edit3,
  X
} from 'lucide-react';
import { resumeService } from '../../services/resume';
import { Resume, ResumeFilters, StructuredResumeData } from '../../types/resume';
import { ResumeUpload } from './ResumeUpload';
import { ResumeAnalysisDashboard } from './ResumeAnalysisDashboard';
import { ResumeEditor } from './ResumeEditor';
import { ResumeTemplateGallery } from './ResumeTemplateGallery';
import { ResumeVersionHistory } from './ResumeVersionHistory';

interface ResumeDashboardProps {
  className?: string;
}

export const ResumeDashboard = ({
  className = '',
}: ResumeDashboardProps) => {
  const [resumes, setResumes] = useState([]);
  const [filteredResumes, setFilteredResumes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('resumes');
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [viewMode, setViewMode] = useState('grid');
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    loadResumes();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [resumes, searchQuery, filters]);

  const loadResumes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await resumeService.getUserResumes();
      setResumes(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load resumes');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...resumes];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(resume =>
        resume.filename.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (filters.processing_status) {
      filtered = filtered.filter(resume => resume.processing_status === filters.processing_status);
    }

    // File type filter
    if (filters.file_type) {
      filtered = filtered.filter(resume => resume.file_type === filters.file_type);
    }

    // Sort by creation date (newest first)
    filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

    setFilteredResumes(filtered);
  };

  const handleUploadSuccess = (resumeId: string) => {
    setShowUploadModal(false);
    setSelectedResumeId(resumeId);
    setActiveTab('analysis');
    loadResumes(); // Refresh the list
  };

  const handleDeleteResume = async (resumeId: string) => {
    if (!confirm('Are you sure you want to delete this resume?')) return;

    try {
      await resumeService.deleteResume(resumeId);
      setResumes(prev => prev.filter(r => r.id !== resumeId));
      if (selectedResumeId === resumeId) {
        setSelectedResumeId(null);
        setActiveTab('resumes');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete resume');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const renderResumeGrid = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {filteredResumes.map((resume) => (
        <div
          key={resume.id}
          className="bg-white border rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
        >
          {/* Resume Preview */}
          <div className="aspect-[3/4] bg-gray-100 relative flex items-center justify-center">
            <FileText className="w-12 h-12 text-gray-400" />
            
            {/* Status Badge */}
            <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs flex items-center space-x-1 ${getStatusColor(resume.processing_status)}`}>
              {getStatusIcon(resume.processing_status)}
              <span className="capitalize">{resume.processing_status}</span>
            </div>

            {/* ATS Score Badge */}
            {resume.ats_score && (
              <div className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-medium ${resumeService.getScoreBadgeColor(resume.ats_score)}`}>
                {resume.ats_score.toFixed(0)}
              </div>
            )}

            {/* Overlay Actions */}
            <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center opacity-0 hover:opacity-100">
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setSelectedResumeId(resume.id);
                    setActiveTab('analysis');
                  }}
                  className="px-3 py-2 bg-white text-gray-900 rounded-lg hover:bg-gray-100 flex items-center space-x-1"
                >
                  <Eye className="w-4 h-4" />
                  <span>View</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedResumeId(resume.id);
                    setActiveTab('editor');
                  }}
                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Edit</span>
                </button>
              </div>
            </div>
          </div>

          {/* Resume Info */}
          <div className="p-4">
            <h3 className="font-semibold text-gray-900 mb-1 truncate">{resume.filename}</h3>
            <p className="text-sm text-gray-600 mb-2">
              {resumeService.formatFileSize(resume.file_size)} • {formatDate(resume.created_at)}
            </p>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 uppercase">{resume.file_type}</span>
              
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => resumeService.downloadResume(resume.id)}
                  className="p-1 text-gray-400 hover:text-gray-600"
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDeleteResume(resume.id)}
                  className="p-1 text-gray-400 hover:text-red-500"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderResumeList = () => (
    <div className="space-y-4">
      {filteredResumes.map((resume) => (
        <div
          key={resume.id}
          className="bg-white border rounded-lg p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-1">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">{resume.filename}</h3>
                  
                  <span className={`px-2 py-1 rounded-full text-xs flex items-center space-x-1 ${getStatusColor(resume.processing_status)}`}>
                    {getStatusIcon(resume.processing_status)}
                    <span className="capitalize">{resume.processing_status}</span>
                  </span>
                  
                  {resume.ats_score && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${resumeService.getScoreBadgeColor(resume.ats_score)}`}>
                      ATS: {resume.ats_score.toFixed(0)}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>{resumeService.formatFileSize(resume.file_size)}</span>
                  <span>{resume.file_type.toUpperCase()}</span>
                  <span>{formatDate(resume.created_at)}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => {
                  setSelectedResumeId(resume.id);
                  setActiveTab('analysis');
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
              >
                <Eye className="w-4 h-4" />
                <span>Analyze</span>
              </button>
              
              <button
                onClick={() => {
                  setSelectedResumeId(resume.id);
                  setActiveTab('editor');
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <Edit3 className="w-4 h-4" />
                <span>Edit</span>
              </button>
              
              <button
                onClick={() => resumeService.downloadResume(resume.id)}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Download"
              >
                <Download className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleDeleteResume(resume.id)}
                className="p-2 text-gray-400 hover:text-red-500"
                title="Delete"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading resumes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Resume Optimization</h1>
          <p className="text-gray-600">Upload, analyze, and optimize your resumes for better ATS compatibility</p>
        </div>
        
        <button
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Resume</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'resumes', label: 'My Resumes', icon: FileText },
            { id: 'templates', label: 'Templates', icon: Grid },
            { id: 'analysis', label: 'Analysis', icon: BarChart3, disabled: !selectedResumeId },
            { id: 'editor', label: 'Editor', icon: Edit3, disabled: !selectedResumeId },
            { id: 'history', label: 'History', icon: Clock, disabled: !selectedResumeId },
          ].map(({ id, label, icon: Icon, disabled }) => (
            <button
              key={id}
              onClick={() => !disabled && setActiveTab(id as any)}
              disabled={disabled}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : disabled
                  ? 'border-transparent text-gray-400 cursor-not-allowed'
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
        {activeTab === 'resumes' && (
          <div className="space-y-6">
            {/* Search and Filters */}
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search resumes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Filters */}
              <div className="flex flex-wrap gap-3">
                <select
                  value={filters.processing_status || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, processing_status: e.target.value as any || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>

                <select
                  value={filters.file_type || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, file_type: e.target.value as any || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  <option value="pdf">PDF</option>
                  <option value="doc">DOC</option>
                  <option value="docx">DOCX</option>
                </select>

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

                <button
                  onClick={loadResumes}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  title="Refresh"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Results Count */}
            <div className="flex items-center justify-between">
              <p className="text-gray-600">
                {filteredResumes.length} resume{filteredResumes.length !== 1 ? 's' : ''} found
              </p>
            </div>

            {/* Resume Grid/List */}
            {filteredResumes.length > 0 ? (
              viewMode === 'grid' ? renderResumeGrid() : renderResumeList()
            ) : (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No resumes found</h3>
                <p className="text-gray-600 mb-4">
                  {searchQuery || Object.keys(filters).length > 0
                    ? 'Try adjusting your search criteria or filters'
                    : 'Upload your first resume to get started with optimization'
                  }
                </p>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Upload Resume
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'templates' && (
          <ResumeTemplateGallery
            onSelectTemplate={(template) => {
              console.log('Selected template:', template);
              // Handle template selection
            }}
            onPreviewTemplate={(template) => {
              console.log('Preview template:', template);
              // Handle template preview
            }}
          />
        )}

        {activeTab === 'analysis' && selectedResumeId && (
          <ResumeAnalysisDashboard
            resumeId={selectedResumeId}
            onOptimize={() => setActiveTab('editor')}
          />
        )}

        {activeTab === 'editor' && selectedResumeId && (
          <ResumeEditor
            resumeId={selectedResumeId}
            onSave={(data: StructuredResumeData) => {
              console.log('Resume saved:', data);
              // Handle save
            }}
          />
        )}

        {activeTab === 'history' && selectedResumeId && (
          <ResumeVersionHistory
            resumeId={selectedResumeId}
            onRestoreVersion={(version) => {
              console.log('Restore version:', version);
              // Handle version restore
            }}
            onPreviewVersion={(version) => {
              console.log('Preview version:', version);
              // Handle version preview
            }}
          />
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Upload Resume</h2>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <ResumeUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={(error) => setError(error)}
            />
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 max-w-md">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-red-800 font-medium">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}; 