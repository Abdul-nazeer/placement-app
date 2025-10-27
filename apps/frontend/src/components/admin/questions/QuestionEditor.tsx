import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { contentService } from '../../../services/content';
import { QuestionCreate, QuestionUpdate, QuestionType, DifficultyLevel, QuestionStatus } from '../../../types/content';

const QuestionEditor: React.FC = () => {
  const id = null; // TODO: Get from URL params
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    type: QuestionType.APTITUDE,
    category: '',
    subcategory: '',
    difficulty: DifficultyLevel.MEDIUM,
    title: '',
    content: '',
    options: ['', '', '', ''],
    correct_answer: '',
    explanation: '',
    hints: [],
    company_tags: [],
    topic_tags: [],
    skill_tags: [],
    extra_data: {},
    is_premium: false,
    status: QuestionStatus.DRAFT,
  });

  const [newTag, setNewTag] = useState('');
  const [tagType, setTagType] = useState('company');

  // Fetch existing question if editing
  const { data: existingQuestion, isLoading: isLoadingQuestion } = useQuery({
    queryKey: ['question', id],
    queryFn: () => contentService.getQuestion(id!),
    enabled: isEditing,
  });

  // Fetch categories and companies for dropdowns
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => contentService.getCategories(),
  });

  const { data: companies } = useQuery({
    queryKey: ['companies'],
    queryFn: () => contentService.getCompanies(),
  });

  // TODO: Add create/update mutations

  // Load existing question data
  useEffect(() => {
    if (existingQuestion) {
      setFormData({
        type: existingQuestion.type,
        category: existingQuestion.category,
        subcategory: existingQuestion.subcategory || '',
        difficulty: existingQuestion.difficulty,
        title: existingQuestion.title,
        content: existingQuestion.content,
        options: existingQuestion.options || ['', '', '', ''],
        correct_answer: existingQuestion.correct_answer,
        explanation: existingQuestion.explanation || '',
        hints: existingQuestion.hints || [],
        company_tags: existingQuestion.company_tags,
        topic_tags: existingQuestion.topic_tags,
        skill_tags: existingQuestion.skill_tags,
        extra_data: existingQuestion.extra_data,
        is_premium: existingQuestion.is_premium,
        status: existingQuestion.status,
      });
    }
  }, [existingQuestion]);

  const handleSubmit = (e: any) => {
    e.preventDefault();
    
    // Validation
    if (!formData.title.trim()) {
      toast.error('Title is required');
      return;
    }
    if (!formData.content.trim()) {
      toast.error('Content is required');
      return;
    }
    if (!formData.correct_answer.trim()) {
      toast.error('Correct answer is required');
      return;
    }
    if (formData.type === QuestionType.APTITUDE && (!formData.options || formData.options.every(opt => !opt.trim()))) {
      toast.error('Options are required for aptitude questions');
      return;
    }

    // Clean up options for non-aptitude questions
    const cleanedData = {
      ...formData,
      options: formData.type === QuestionType.APTITUDE ? formData.options?.filter(opt => opt.trim()) : undefined,
      subcategory: formData.subcategory || undefined,
      explanation: formData.explanation || undefined,
    };

    if (isEditing && id) {
      // TODO: Update question
      console.log('Update question:', id, cleanedData);
      toast.info('Update functionality coming soon');
    } else {
      // TODO: Create question
      console.log('Create question:', cleanedData);
      toast.info('Create functionality coming soon');
    }
  };

  const handleInputChange = (field: keyof QuestionCreate, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...(formData.options || [])];
    newOptions[index] = value;
    handleInputChange('options', newOptions);
  };

  const addOption = () => {
    const newOptions = [...(formData.options || []), ''];
    handleInputChange('options', newOptions);
  };

  const removeOption = (index: number) => {
    const newOptions = formData.options?.filter((_, i) => i !== index) || [];
    handleInputChange('options', newOptions);
  };

  const addTag = () => {
    if (!newTag.trim()) return;
    
    const tagField = `${tagType}_tags` as keyof QuestionCreate;
    const currentTags = formData[tagField] as string[] || [];
    
    if (!currentTags.includes(newTag.trim())) {
      handleInputChange(tagField, [...currentTags, newTag.trim()]);
    }
    
    setNewTag('');
  };

  const removeTag = (tagField: keyof QuestionCreate, tagToRemove: string) => {
    const currentTags = formData[tagField] as string[] || [];
    handleInputChange(tagField, currentTags.filter(tag => tag !== tagToRemove));
  };

  const addHint = () => {
    handleInputChange('hints', [...(formData.hints || []), '']);
  };

  const updateHint = (index: number, value: string) => {
    const newHints = [...(formData.hints || [])];
    newHints[index] = value;
    handleInputChange('hints', newHints);
  };

  const removeHint = (index: number) => {
    const newHints = formData.hints?.filter((_, i) => i !== index) || [];
    handleInputChange('hints', newHints);
  };

  if (isEditing && isLoadingQuestion) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-10 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit Question' : 'Create Question'}
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          {isEditing ? 'Update question details' : 'Add a new question to the bank'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type *
              </label>
              <select
                value={formData.type}
                onChange={(e) => handleInputChange('type', e.target.value as QuestionType)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              >
                <option value={QuestionType.APTITUDE}>Aptitude</option>
                <option value={QuestionType.CODING}>Coding</option>
                <option value={QuestionType.COMMUNICATION}>Communication</option>
              </select>
            </div>

            {/* Difficulty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Difficulty *
              </label>
              <select
                value={formData.difficulty}
                onChange={(e) => handleInputChange('difficulty', parseInt(e.target.value) as DifficultyLevel)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              >
                <option value={DifficultyLevel.BEGINNER}>Level 1 - Beginner</option>
                <option value={DifficultyLevel.EASY}>Level 2 - Easy</option>
                <option value={DifficultyLevel.MEDIUM}>Level 3 - Medium</option>
                <option value={DifficultyLevel.HARD}>Level 4 - Hard</option>
                <option value={DifficultyLevel.EXPERT}>Level 5 - Expert</option>
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category *
              </label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            {/* Subcategory */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subcategory
              </label>
              <input
                type="text"
                value={formData.subcategory}
                onChange={(e) => handleInputChange('subcategory', e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
          </div>

          {/* Title */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              required
            />
          </div>

          {/* Content */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content *
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => handleInputChange('content', e.target.value)}
              rows={6}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              required
            />
          </div>
        </div>

        {/* Options (for aptitude questions) */}
        {formData.type === QuestionType.APTITUDE && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Options</h2>
            
            <div className="space-y-3">
              {formData.options?.map((option, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-gray-700 w-8">
                    {String.fromCharCode(65 + index)}.
                  </span>
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => handleOptionChange(index, e.target.value)}
                    className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder={`Option ${String.fromCharCode(65 + index)}`}
                  />
                  {formData.options && formData.options.length > 2 && (
                    <button
                      type="button"
                      onClick={() => removeOption(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>
            
            <button
              type="button"
              onClick={addOption}
              className="mt-3 text-sm text-indigo-600 hover:text-indigo-800"
            >
              + Add Option
            </button>
          </div>
        )}

        {/* Answer and Explanation */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Answer & Explanation</h2>
          
          <div className="space-y-6">
            {/* Correct Answer */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Correct Answer *
              </label>
              {formData.type === QuestionType.APTITUDE ? (
                <select
                  value={formData.correct_answer}
                  onChange={(e) => handleInputChange('correct_answer', e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  required
                >
                  <option value="">Select correct option</option>
                  {formData.options?.map((option, index) => (
                    <option key={index} value={option}>
                      {String.fromCharCode(65 + index)}. {option}
                    </option>
                  ))}
                </select>
              ) : (
                <textarea
                  value={formData.correct_answer}
                  onChange={(e) => handleInputChange('correct_answer', e.target.value)}
                  rows={3}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  required
                />
              )}
            </div>

            {/* Explanation */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Explanation
              </label>
              <textarea
                value={formData.explanation}
                onChange={(e) => handleInputChange('explanation', e.target.value)}
                rows={4}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="Explain the correct answer..."
              />
            </div>
          </div>
        </div>

        {/* Hints */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Hints</h2>
          
          <div className="space-y-3">
            {formData.hints?.map((hint, index) => (
              <div key={index} className="flex items-center space-x-3">
                <span className="text-sm font-medium text-gray-700 w-8">
                  {index + 1}.
                </span>
                <input
                  type="text"
                  value={hint}
                  onChange={(e) => updateHint(index, e.target.value)}
                  className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder={`Hint ${index + 1}`}
                />
                <button
                  type="button"
                  onClick={() => removeHint(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          
          <button
            type="button"
            onClick={addHint}
            className="mt-3 text-sm text-indigo-600 hover:text-indigo-800"
          >
            + Add Hint
          </button>
        </div>

        {/* Tags */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Tags</h2>
          
          {/* Add Tag */}
          <div className="flex items-center space-x-3 mb-4">
            <select
              value={tagType}
              onChange={(e) => setTagType(e.target.value as 'company' | 'topic' | 'skill')}
              className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="company">Company</option>
              <option value="topic">Topic</option>
              <option value="skill">Skill</option>
            </select>
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter tag name"
            />
            <button
              type="button"
              onClick={addTag}
              className="px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </div>

          {/* Display Tags */}
          <div className="space-y-4">
            {/* Company Tags */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Company Tags</h4>
              <div className="flex flex-wrap gap-2">
                {formData.company_tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag('company_tags', tag)}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Topic Tags */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Topic Tags</h4>
              <div className="flex flex-wrap gap-2">
                {formData.topic_tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag('topic_tags', tag)}
                      className="ml-1 text-green-600 hover:text-green-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Skill Tags */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Skill Tags</h4>
              <div className="flex flex-wrap gap-2">
                {formData.skill_tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag('skill_tags', tag)}
                      className="ml-1 text-purple-600 hover:text-purple-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Settings</h2>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_premium}
                onChange={(e) => handleInputChange('is_premium', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Premium question
              </label>
            </div>

            {isEditing && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value as QuestionStatus)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value={QuestionStatus.DRAFT}>Draft</option>
                  <option value={QuestionStatus.PENDING_REVIEW}>Pending Review</option>
                  <option value={QuestionStatus.APPROVED}>Approved</option>
                  <option value={QuestionStatus.REJECTED}>Rejected</option>
                  <option value={QuestionStatus.ARCHIVED}>Archived</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/admin/questions')}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={false}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {isEditing ? 'Update Question' : 'Create Question'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default QuestionEditor;