import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  ClockIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  UserGroupIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import { InterviewService } from '../../services/interview';
import {
  InterviewType,
  DifficultyLevel,
  QuestionCategory,
  InterviewSessionCreate
} from '../../types/interview';

export const InterviewCreator: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<InterviewSessionCreate>({
    interview_type: InterviewType.MIXED,
    title: '',
    description: '',
    company_name: '',
    position_title: '',
    total_duration: 30,
    question_count: 10,
    difficulty_level: DifficultyLevel.MEDIUM,
    adaptive_mode: true,
    performance_threshold: 0.7,
    question_categories: [QuestionCategory.BEHAVIORAL, QuestionCategory.HR_GENERAL],
    company_tags: [],
    topic_tags: [],
    enable_video_recording: true,
    enable_audio_recording: true
  });

  const handleInputChange = (field: keyof InterviewSessionCreate, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCategoryToggle = (category: QuestionCategory) => {
    setFormData(prev => ({
      ...prev,
      question_categories: prev.question_categories.includes(category)
        ? prev.question_categories.filter(c => c !== category)
        : [...prev.question_categories, category]
    }));
  };

  const handleTagsChange = (field: 'company_tags' | 'topic_tags', value: string) => {
    const tags = value.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
    setFormData(prev => ({
      ...prev,
      [field]: tags
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.question_categories.length === 0) {
      setError('Please select at least one question category');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const session = await InterviewService.createSession(formData);
      navigate(`/interview/session/${session.id}`);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create interview session');
      console.error('Interview creation error:', err);
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

  const interviewTypes = [
    {
      type: InterviewType.BEHAVIORAL,
      title: 'Behavioral Interview',
      description: 'Practice behavioral questions and soft skills',
      icon: <UserGroupIcon className="h-6 w-6" />
    },
    {
      type: InterviewType.TECHNICAL,
      title: 'Technical Interview',
      description: 'Focus on technical skills and problem-solving',
      icon: <AcademicCapIcon className="h-6 w-6" />
    },
    {
      type: InterviewType.HR,
      title: 'HR Interview',
      description: 'General HR questions and company fit',
      icon: <BriefcaseIcon className="h-6 w-6" />
    },
    {
      type: InterviewType.MIXED,
      title: 'Mixed Interview',
      description: 'Combination of behavioral, technical, and HR questions',
      icon: <DocumentTextIcon className="h-6 w-6" />
    }
  ];

  const questionCategories = [
    { category: QuestionCategory.BEHAVIORAL, label: 'Behavioral', description: 'STAR method questions' },
    { category: QuestionCategory.TECHNICAL_CODING, label: 'Technical Coding', description: 'Programming challenges' },
    { category: QuestionCategory.TECHNICAL_SYSTEM_DESIGN, label: 'System Design', description: 'Architecture questions' },
    { category: QuestionCategory.HR_GENERAL, label: 'HR General', description: 'General HR questions' },
    { category: QuestionCategory.COMPANY_SPECIFIC, label: 'Company Specific', description: 'Company culture fit' },
    { category: QuestionCategory.SITUATIONAL, label: 'Situational', description: 'Hypothetical scenarios' }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center mb-8">
        <button
          onClick={() => navigate('/interview')}
          className="mr-4 p-2 text-gray-400 hover:text-gray-600"
        >
          <ArrowLeftIcon className="h-6 w-6" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create Mock Interview</h1>
          <p className="text-gray-600 mt-2">
            Set up a personalized interview session with AI-powered questions
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interview Title *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Software Engineer Interview Practice"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={formData.company_name}
                onChange={(e) => handleInputChange('company_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Google, Microsoft"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Position Title
              </label>
              <input
                type="text"
                value={formData.position_title}
                onChange={(e) => handleInputChange('position_title', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Senior Software Engineer"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (minutes) *
              </label>
              <select
                value={formData.total_duration}
                onChange={(e) => handleInputChange('total_duration', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={45}>45 minutes</option>
                <option value={60}>1 hour</option>
                <option value={90}>1.5 hours</option>
                <option value={120}>2 hours</option>
              </select>
            </div>
          </div>
          
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe the focus and goals of this interview session..."
            />
          </div>
        </div>

        {/* Interview Type */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Interview Type</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {interviewTypes.map((type) => (
              <div
                key={type.type}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  formData.interview_type === type.type
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleInputChange('interview_type', type.type)}
              >
                <div className="flex items-center mb-2">
                  <div className={`p-2 rounded-lg mr-3 ${
                    formData.interview_type === type.type ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {type.icon}
                  </div>
                  <h3 className="font-medium text-gray-900">{type.title}</h3>
                </div>
                <p className="text-sm text-gray-600">{type.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Question Configuration */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Question Configuration</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Questions *
              </label>
              <select
                value={formData.question_count}
                onChange={(e) => handleInputChange('question_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {[5, 8, 10, 12, 15, 20].map(count => (
                  <option key={count} value={count}>{count} questions</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level *
              </label>
              <select
                value={formData.difficulty_level}
                onChange={(e) => handleInputChange('difficulty_level', e.target.value as DifficultyLevel)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value={DifficultyLevel.EASY}>Easy</option>
                <option value={DifficultyLevel.MEDIUM}>Medium</option>
                <option value={DifficultyLevel.HARD}>Hard</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Adaptive Mode
              </label>
              <div className="flex items-center mt-3">
                <input
                  type="checkbox"
                  checked={formData.adaptive_mode}
                  onChange={(e) => handleInputChange('adaptive_mode', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Adjust difficulty based on performance
                </span>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Question Categories *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {questionCategories.map((cat) => (
                <div
                  key={cat.category}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    formData.question_categories.includes(cat.category)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleCategoryToggle(cat.category)}
                >
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.question_categories.includes(cat.category)}
                      onChange={() => handleCategoryToggle(cat.category)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div className="ml-3">
                      <h4 className="font-medium text-gray-900">{cat.label}</h4>
                      <p className="text-sm text-gray-600">{cat.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Tags
              </label>
              <input
                type="text"
                value={formData.company_tags?.join(', ') || ''}
                onChange={(e) => handleTagsChange('company_tags', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., FAANG, startup, fintech (comma-separated)"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topic Tags
              </label>
              <input
                type="text"
                value={formData.topic_tags?.join(', ') || ''}
                onChange={(e) => handleTagsChange('topic_tags', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., algorithms, leadership, teamwork (comma-separated)"
              />
            </div>
          </div>
        </div>

        {/* Recording Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recording Settings</h2>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.enable_video_recording}
                onChange={(e) => handleInputChange('enable_video_recording', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div className="ml-3 flex items-center">
                <VideoCameraIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-700">Enable Video Recording</span>
              </div>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.enable_audio_recording}
                onChange={(e) => handleInputChange('enable_audio_recording', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div className="ml-3 flex items-center">
                <MicrophoneIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-700">Enable Audio Recording</span>
              </div>
            </div>
          </div>
          
          <p className="text-sm text-gray-600 mt-4">
            Recording helps provide better feedback on your communication skills and body language.
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => navigate('/interview')}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
          >
            Cancel
          </button>
          
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating...' : 'Create Interview'}
          </button>
        </div>
      </form>
    </div>
  );
};