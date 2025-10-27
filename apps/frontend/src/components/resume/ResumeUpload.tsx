/**
 * Resume upload component with drag-and-drop functionality
 */

import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, AlertCircle, CheckCircle } from 'lucide-react';
import { resumeService } from '../../services/resume';
import { DragDropFile, ResumeUploadRequest } from '../../types/resume';

interface ResumeUploadProps {
  onUploadSuccess?: (resumeId: string) => void;
  onUploadError?: (error: string) => void;
  className?: string;
}

export const ResumeUpload = ({
  onUploadSuccess,
  onUploadError,
  className = '',
}: ResumeUploadProps) => {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadData, setUploadData] = useState({});

  const onDrop = (acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(({ file, errors }) => 
        `${file.name}: ${errors.map((e: any) => e.message).join(', ')}`
      );
      onUploadError?.(errors.join('\n'));
      return;
    }

    // Validate and add accepted files
    const validFiles: DragDropFile[] = [];
    
    for (const file of acceptedFiles) {
      if (!resumeService.validateFileType(file)) {
        onUploadError?.(`${file.name}: Invalid file type. Please upload PDF, DOC, or DOCX files.`);
        continue;
      }
      
      if (!resumeService.validateFileSize(file)) {
        onUploadError?.(`${file.name}: File size exceeds 10MB limit.`);
        continue;
      }

      validFiles.push({
        file,
        preview: URL.createObjectURL(file),
        progress: 0,
      });
    }

    setFiles(prev => [...prev, ...validFiles]);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: 'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  } as any);

  const removeFile = (index: number) => {
    setFiles(prev => {
      const newFiles = [...prev];
      if (newFiles[index].preview) {
        URL.revokeObjectURL(newFiles[index].preview!);
      }
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setIsUploading(true);

    try {
      for (let i = 0; i < files.length; i++) {
        const fileData = files[i];
        
        // Update progress
        setFiles(prev => {
          const newFiles = [...prev];
          newFiles[i] = { ...newFiles[i], progress: 0 };
          return newFiles;
        });

        try {
          const result = await resumeService.uploadResume(fileData.file, uploadData);
          
          // Update progress to complete
          setFiles(prev => {
            const newFiles = [...prev];
            newFiles[i] = { ...newFiles[i], progress: 100 };
            return newFiles;
          });

          onUploadSuccess?.(result.id);
        } catch (error: any) {
          // Update with error
          setFiles(prev => {
            const newFiles = [...prev];
            newFiles[i] = { 
              ...newFiles[i], 
              error: error.response?.data?.detail || 'Upload failed' 
            };
            return newFiles;
          });
          
          onUploadError?.(error.response?.data?.detail || 'Upload failed');
        }
      }
    } finally {
      setIsUploading(false);
    }
  };

  const getFileIcon = (fileType: string) => {
    return <FileText className="w-8 h-8 text-blue-500" />;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Upload Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Role (Optional)
          </label>
          <input
            type="text"
            value={uploadData.target_role || ''}
            onChange={(e) => setUploadData(prev => ({ ...prev, target_role: e.target.value }))}
            placeholder="e.g., Software Engineer, Data Analyst"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Industry (Optional)
          </label>
          <select
            value={uploadData.target_industry || ''}
            onChange={(e) => setUploadData(prev => ({ ...prev, target_industry: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select Industry</option>
            <option value="technology">Technology</option>
            <option value="finance">Finance</option>
            <option value="healthcare">Healthcare</option>
            <option value="marketing">Marketing</option>
            <option value="consulting">Consulting</option>
            <option value="education">Education</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="retail">Retail</option>
          </select>
        </div>
      </div>

      {/* Drag and Drop Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input {...(getInputProps() as any)} />
        
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Drop your resume here...</p>
        ) : (
          <div>
            <p className="text-gray-600 font-medium mb-2">
              Drag and drop your resume here, or click to browse
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, DOC, and DOCX files up to 10MB
            </p>
          </div>
        )}
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900">Selected Files</h3>
          
          {files.map((fileData, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border"
            >
              <div className="flex items-center space-x-3">
                {getFileIcon(fileData.file.type)}
                
                <div>
                  <p className="font-medium text-gray-900">{fileData.file.name}</p>
                  <p className="text-sm text-gray-500">
                    {resumeService.formatFileSize(fileData.file.size)}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {/* Progress/Status */}
                {fileData.error ? (
                  <div className="flex items-center text-red-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    <span className="text-sm">Error</span>
                  </div>
                ) : fileData.progress === 100 ? (
                  <div className="flex items-center text-green-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span className="text-sm">Complete</span>
                  </div>
                ) : fileData.progress !== undefined && fileData.progress > 0 ? (
                  <div className="w-24">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${fileData.progress}%` }}
                      />
                    </div>
                  </div>
                ) : null}

                {/* Remove Button */}
                <button
                  onClick={() => removeFile(index)}
                  disabled={isUploading}
                  className="p-1 text-gray-400 hover:text-red-500 disabled:opacity-50"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}

          {/* Error Messages */}
          {files.some(f => f.error) && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="text-red-800 font-medium mb-2">Upload Errors:</h4>
              <ul className="text-sm text-red-700 space-y-1">
                {files
                  .filter(f => f.error)
                  .map((f, i) => (
                    <li key={i}>• {f.file.name}: {f.error}</li>
                  ))}
              </ul>
            </div>
          )}

          {/* Upload Button */}
          <div className="flex justify-end">
            <button
              onClick={uploadFiles}
              disabled={isUploading || files.length === 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isUploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload Resume{files.length > 1 ? 's' : ''}</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};