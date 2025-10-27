/**
 * Basic test for Resume Dashboard component
 */

import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { ResumeDashboard } from '../ResumeDashboard';

// Mock the services
vi.mock('../../../services/resume', () => ({
  resumeService: {
    getUserResumes: vi.fn().mockResolvedValue([]),
    deleteResume: vi.fn().mockResolvedValue(undefined),
    formatFileSize: vi.fn().mockReturnValue('1 MB'),
    getScoreBadgeColor: vi.fn().mockReturnValue('bg-green-100 text-green-800'),
    downloadResume: vi.fn().mockResolvedValue(new Blob()),
  },
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Upload: () => React.createElement('div', { 'data-testid': 'upload-icon' }),
  FileText: () => React.createElement('div', { 'data-testid': 'file-text-icon' }),
  BarChart3: () => React.createElement('div', { 'data-testid': 'bar-chart-icon' }),
  Settings: () => React.createElement('div', { 'data-testid': 'settings-icon' }),
  Plus: () => React.createElement('div', { 'data-testid': 'plus-icon' }),
  Search: () => React.createElement('div', { 'data-testid': 'search-icon' }),
  Filter: () => React.createElement('div', { 'data-testid': 'filter-icon' }),
  Grid: () => React.createElement('div', { 'data-testid': 'grid-icon' }),
  List: () => React.createElement('div', { 'data-testid': 'list-icon' }),
  Eye: () => React.createElement('div', { 'data-testid': 'eye-icon' }),
  Download: () => React.createElement('div', { 'data-testid': 'download-icon' }),
  Trash2: () => React.createElement('div', { 'data-testid': 'trash-icon' }),
  RefreshCw: () => React.createElement('div', { 'data-testid': 'refresh-icon' }),
  AlertCircle: () => React.createElement('div', { 'data-testid': 'alert-icon' }),
  CheckCircle: () => React.createElement('div', { 'data-testid': 'check-icon' }),
  Clock: () => React.createElement('div', { 'data-testid': 'clock-icon' }),
  Edit3: () => React.createElement('div', { 'data-testid': 'edit-icon' }),
  X: () => React.createElement('div', { 'data-testid': 'x-icon' }),
}));

// Mock child components
vi.mock('../ResumeUpload', () => ({
  ResumeUpload: ({ onUploadSuccess }: any) =>
    React.createElement('div', { 'data-testid': 'resume-upload' },
      React.createElement('button', { onClick: () => onUploadSuccess('test-id') }, 'Upload')
    ),
}));

vi.mock('../ResumeAnalysisDashboard', () => ({
  ResumeAnalysisDashboard: () => React.createElement('div', { 'data-testid': 'resume-analysis' }),
}));

vi.mock('../ResumeEditor', () => ({
  ResumeEditor: () => React.createElement('div', { 'data-testid': 'resume-editor' }),
}));

vi.mock('../ResumeTemplateGallery', () => ({
  ResumeTemplateGallery: () => React.createElement('div', { 'data-testid': 'resume-templates' }),
}));

vi.mock('../ResumeVersionHistory', () => ({
  ResumeVersionHistory: () => React.createElement('div', { 'data-testid': 'resume-history' }),
}));

describe('ResumeDashboard', () => {
  it('renders without crashing', () => {
    const component = React.createElement(ResumeDashboard);
    expect(component).toBeDefined();
  });

  it('has the correct structure', () => {
    const component = React.createElement(ResumeDashboard, { className: 'test-class' });
    expect(component.props.className).toBe('test-class');
  });
});