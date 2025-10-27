/**
 * Resume editor with real-time optimization suggestions
 */

import React, { useState, useEffect } from 'react';
import { 
  Save, 
  Undo, 
  Redo, 
  Eye, 
  Download,
  Lightbulb,
  Plus,
  Trash2,
  Edit3,
  AlertCircle
} from 'lucide-react';
import { resumeService } from '../../services/resume';
import { 
  StructuredResumeData, 
  ResumeEditorState, 
  OptimizationSuggestion,
  WorkExperience,
  Education,
  Skill
} from '../../types/resume';

interface ResumeEditorProps {
  resumeId: string;
  initialData?: StructuredResumeData;
  onSave?: (data: StructuredResumeData) => void;
  className?: string;
}

export const ResumeEditor = ({
  resumeId,
  initialData,
  onSave,
  className = '',
}: ResumeEditorProps) => {
  const [editorState, setEditorState] = useState({
    content: initialData || {
      contact_info: {},
      work_experience: [],
      education: [],
      skills: [],
      certifications: [],
      projects: [],
      sections: [],
    },
    isDirty: false,
    isLoading: false,
    suggestions: [],
  });

  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [previewMode, setPreviewMode] = useState(false);

  useEffect(() => {
    if (initialData) {
      setEditorState(prev => ({ ...prev, content: initialData }));
      setHistory([initialData]);
      setHistoryIndex(0);
    }
  }, [initialData]);

  const updateContent = (updater: any) => {
    setEditorState(prev => {
      const newContent = updater(prev.content);
      
      // Add to history if content changed
      if (JSON.stringify(newContent) !== JSON.stringify(prev.content)) {
        const newHistory = history.slice(0, historyIndex + 1);
        newHistory.push(newContent);
        setHistory(newHistory);
        setHistoryIndex(newHistory.length - 1);
      }

      return {
        ...prev,
        content: newContent,
        isDirty: true,
      };
    });
  };

  const undo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setEditorState(prev => ({
        ...prev,
        content: history[newIndex],
        isDirty: true,
      }));
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setEditorState(prev => ({
        ...prev,
        content: history[newIndex],
        isDirty: true,
      }));
    }
  };

  const handleSave = async () => {
    try {
      setEditorState(prev => ({ ...prev, isLoading: true }));
      
      // Here you would typically save to backend
      // For now, just call the onSave callback
      onSave?.(editorState.content);
      
      setEditorState(prev => ({ ...prev, isDirty: false }));
    } catch (error) {
      console.error('Failed to save resume:', error);
    } finally {
      setEditorState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const addWorkExperience = () => {
    updateContent(prev => ({
      ...prev,
      work_experience: [
        ...prev.work_experience,
        {
          company: '',
          position: '',
          start_date: '',
          end_date: '',
          location: '',
          description: [''],
          skills_used: [],
        },
      ],
    }));
  };

  const updateWorkExperience = (index: number, field: keyof WorkExperience, value: any) => {
    updateContent(prev => ({
      ...prev,
      work_experience: prev.work_experience.map((exp, i) =>
        i === index ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  const removeWorkExperience = (index: number) => {
    updateContent(prev => ({
      ...prev,
      work_experience: prev.work_experience.filter((_, i) => i !== index),
    }));
  };

  const addEducation = () => {
    updateContent(prev => ({
      ...prev,
      education: [
        ...prev.education,
        {
          institution: '',
          degree: '',
          field_of_study: '',
          start_date: '',
          end_date: '',
          gpa: '',
          achievements: [],
        },
      ],
    }));
  };

  const updateEducation = (index: number, field: keyof Education, value: any) => {
    updateContent(prev => ({
      ...prev,
      education: prev.education.map((edu, i) =>
        i === index ? { ...edu, [field]: value } : edu
      ),
    }));
  };

  const removeEducation = (index: number) => {
    updateContent(prev => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== index),
    }));
  };

  const addSkill = () => {
    updateContent(prev => ({
      ...prev,
      skills: [
        ...prev.skills,
        {
          name: '',
          category: 'technical',
          proficiency: '',
          years_experience: 0,
        },
      ],
    }));
  };

  const updateSkill = (index: number, field: keyof Skill, value: any) => {
    updateContent(prev => ({
      ...prev,
      skills: prev.skills.map((skill, i) =>
        i === index ? { ...skill, [field]: value } : skill
      ),
    }));
  };

  const removeSkill = (index: number) => {
    updateContent(prev => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index),
    }));
  };

  if (previewMode) {
    return (
      <div className={`bg-white ${className}`}>
        {/* Preview Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold">Resume Preview</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPreviewMode(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Edit3 className="w-4 h-4 mr-2 inline" />
              Edit
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <Download className="w-4 h-4 mr-2 inline" />
              Download
            </button>
          </div>
        </div>

        {/* Resume Preview Content */}
        <div className="p-8 max-w-4xl mx-auto">
          <div className="bg-white shadow-lg rounded-lg p-8 space-y-6">
            {/* Contact Info */}
            <div className="text-center border-b pb-6">
              <h1 className="text-3xl font-bold text-gray-900">
                {editorState.content.contact_info.name || 'Your Name'}
              </h1>
              <div className="flex justify-center space-x-4 mt-2 text-gray-600">
                {editorState.content.contact_info.email && (
                  <span>{editorState.content.contact_info.email}</span>
                )}
                {editorState.content.contact_info.phone && (
                  <span>{editorState.content.contact_info.phone}</span>
                )}
                {editorState.content.contact_info.linkedin && (
                  <span>{editorState.content.contact_info.linkedin}</span>
                )}
              </div>
            </div>

            {/* Summary */}
            {editorState.content.summary && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-3">Professional Summary</h2>
                <p className="text-gray-700">{editorState.content.summary}</p>
              </div>
            )}

            {/* Work Experience */}
            {editorState.content.work_experience.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Work Experience</h2>
                <div className="space-y-4">
                  {editorState.content.work_experience.map((exp, index) => (
                    <div key={index} className="border-l-2 border-blue-200 pl-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-semibold text-gray-900">{exp.position}</h3>
                          <p className="text-blue-600">{exp.company}</p>
                        </div>
                        <div className="text-right text-sm text-gray-600">
                          <p>{exp.start_date} - {exp.end_date || 'Present'}</p>
                          {exp.location && <p>{exp.location}</p>}
                        </div>
                      </div>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {exp.description.map((desc, i) => (
                          <li key={i}>{desc}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {editorState.content.education.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Education</h2>
                <div className="space-y-3">
                  {editorState.content.education.map((edu, index) => (
                    <div key={index}>
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-gray-900">{edu.degree}</h3>
                          <p className="text-blue-600">{edu.institution}</p>
                          {edu.field_of_study && (
                            <p className="text-gray-600">{edu.field_of_study}</p>
                          )}
                        </div>
                        <div className="text-right text-sm text-gray-600">
                          <p>{edu.start_date} - {edu.end_date}</p>
                          {edu.gpa && <p>GPA: {edu.gpa}</p>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Skills */}
            {editorState.content.skills.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {editorState.content.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {skill.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white ${className}`}>
      {/* Editor Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold">Resume Editor</h2>
          {editorState.isDirty && (
            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
              Unsaved changes
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={undo}
            disabled={historyIndex <= 0}
            className="p-2 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            <Undo className="w-4 h-4" />
          </button>
          
          <button
            onClick={redo}
            disabled={historyIndex >= history.length - 1}
            className="p-2 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            <Redo className="w-4 h-4" />
          </button>

          <button
            onClick={() => setPreviewMode(true)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Eye className="w-4 h-4 mr-2 inline" />
            Preview
          </button>

          <button
            onClick={handleSave}
            disabled={!editorState.isDirty || editorState.isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {editorState.isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2 inline-block" />
            ) : (
              <Save className="w-4 h-4 mr-2 inline" />
            )}
            Save
          </button>
        </div>
      </div>

      <div className="flex">
        {/* Editor Content */}
        <div className="flex-1 p-6 space-y-8 overflow-y-auto max-h-screen">
          {/* Contact Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Full Name"
                value={editorState.content.contact_info.name || ''}
                onChange={(e) => updateContent(prev => ({
                  ...prev,
                  contact_info: { ...prev.contact_info, name: e.target.value }
                }))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              <input
                type="email"
                placeholder="Email Address"
                value={editorState.content.contact_info.email || ''}
                onChange={(e) => updateContent(prev => ({
                  ...prev,
                  contact_info: { ...prev.contact_info, email: e.target.value }
                }))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              <input
                type="tel"
                placeholder="Phone Number"
                value={editorState.content.contact_info.phone || ''}
                onChange={(e) => updateContent(prev => ({
                  ...prev,
                  contact_info: { ...prev.contact_info, phone: e.target.value }
                }))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              <input
                type="url"
                placeholder="LinkedIn Profile"
                value={editorState.content.contact_info.linkedin || ''}
                onChange={(e) => updateContent(prev => ({
                  ...prev,
                  contact_info: { ...prev.contact_info, linkedin: e.target.value }
                }))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Professional Summary */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Professional Summary</h3>
            <textarea
              placeholder="Write a compelling professional summary..."
              value={editorState.content.summary || ''}
              onChange={(e) => updateContent(prev => ({
                ...prev,
                summary: e.target.value
              }))}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Work Experience */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Work Experience</h3>
              <button
                onClick={addWorkExperience}
                className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>

            {editorState.content.work_experience.map((exp, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <h4 className="font-medium text-gray-900">Experience #{index + 1}</h4>
                  <button
                    onClick={() => removeWorkExperience(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    placeholder="Job Title"
                    value={exp.position}
                    onChange={(e) => updateWorkExperience(index, 'position', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="text"
                    placeholder="Company Name"
                    value={exp.company}
                    onChange={(e) => updateWorkExperience(index, 'company', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="text"
                    placeholder="Start Date"
                    value={exp.start_date || ''}
                    onChange={(e) => updateWorkExperience(index, 'start_date', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="text"
                    placeholder="End Date (or Present)"
                    value={exp.end_date || ''}
                    onChange={(e) => updateWorkExperience(index, 'end_date', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <textarea
                  placeholder="Job description and achievements..."
                  value={exp.description.join('\n')}
                  onChange={(e) => updateWorkExperience(index, 'description', e.target.value.split('\n'))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>

          {/* Education */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Education</h3>
              <button
                onClick={addEducation}
                className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>

            {editorState.content.education.map((edu, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <h4 className="font-medium text-gray-900">Education #{index + 1}</h4>
                  <button
                    onClick={() => removeEducation(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    placeholder="Degree"
                    value={edu.degree}
                    onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="text"
                    placeholder="Institution"
                    value={edu.institution}
                    onChange={(e) => updateEducation(index, 'institution', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="text"
                    placeholder="Field of Study"
                    value={edu.field_of_study || ''}
                    onChange={(e) => updateEducation(index, 'field_of_study', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  
                  <input
                    type="text"
                    placeholder="GPA (Optional)"
                    value={edu.gpa || ''}
                    onChange={(e) => updateEducation(index, 'gpa', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Skills */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Skills</h3>
              <button
                onClick={addSkill}
                className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {editorState.content.skills.map((skill, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-3 space-y-2">
                  <div className="flex justify-between items-start">
                    <input
                      type="text"
                      placeholder="Skill name"
                      value={skill.name}
                      onChange={(e) => updateSkill(index, 'name', e.target.value)}
                      className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => removeSkill(index)}
                      className="ml-2 text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                  
                  <select
                    value={skill.category}
                    onChange={(e) => updateSkill(index, 'category', e.target.value)}
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="technical">Technical</option>
                    <option value="soft">Soft Skills</option>
                    <option value="language">Language</option>
                    <option value="certification">Certification</option>
                  </select>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Suggestions Sidebar */}
        <div className="w-80 border-l bg-gray-50 p-4 space-y-4 overflow-y-auto max-h-screen">
          <div className="flex items-center space-x-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <h3 className="font-semibold text-gray-900">Optimization Tips</h3>
          </div>

          {editorState.suggestions.length > 0 ? (
            <div className="space-y-3">
              {editorState.suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="bg-white border rounded-lg p-3 space-y-2"
                >
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {suggestion.type.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        {suggestion.suggestion}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Lightbulb className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">
                Start editing to see optimization suggestions
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};