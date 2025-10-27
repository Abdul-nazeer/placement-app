import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { contentService } from '../../services/content';
import { QuestionFilters, QuestionType, QuestionStatus } from '../../types/content';

const ImportExport: React.FC = () => {
  const [exportFilters, setExportFilters] = useState({});
  const [importFile, setImportFile] = useState(null);
  const [importResult, setImportResult] = useState(null);

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => contentService.getCategories(),
  });

  // TODO: Add export and import mutations

  const handleExport = () => {
    // TODO: Implement export
    console.log('Export with filters:', exportFilters);
    toast.info('Export functionality coming soon');
  };

  const handleImport = () => {
    if (!importFile) {
      toast.error('Please select a file to import');
      return;
    }
    // TODO: Implement import
    console.log('Import file:', importFile);
    toast.info('Import functionality coming soon');
  };

  const handleFileChange = (e: any) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        toast.error('Please select a CSV file');
        return;
      }
      setImportFile(file);
      setImportResult(null);
    }
  };

  const handleFilterChange = (key: keyof QuestionFilters, value: any) => {
    setExportFilters(prev => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Import & Export</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage bulk question operations
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Export Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Export Questions</h2>
          <p className="text-sm text-gray-600 mb-6">
            Export questions to CSV format with optional filtering
          </p>

          <div className="space-y-4">
            {/* Export Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Question Type
              </label>
              <select
                value={exportFilters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value as QuestionType)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="">All types</option>
                <option value={QuestionType.APTITUDE}>Aptitude</option>
                <option value={QuestionType.CODING}>Coding</option>
                <option value={QuestionType.COMMUNICATION}>Communication</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={exportFilters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value)}
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={exportFilters.status?.[0] || ''}
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

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={exportFilters.is_active !== false}
                onChange={(e) => handleFilterChange('is_active', e.target.checked ? undefined : false)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Include active questions only
              </label>
            </div>

            <button
              onClick={handleExport}
              disabled={false}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              Export to CSV
            </button>
          </div>
        </div>

        {/* Import Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Import Questions</h2>
          <p className="text-sm text-gray-600 mb-6">
            Import questions from CSV file. Make sure your CSV follows the required format.
          </p>

          <div className="space-y-4">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CSV File
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <label className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                      <span>Upload a file</span>
                      <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        className="sr-only"
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">CSV files only</p>
                </div>
              </div>
              {importFile && (
                <div className="mt-2 text-sm text-gray-600">
                  Selected: {importFile.name} ({(importFile.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>

            <button
              onClick={handleImport}
              disabled={!importFile}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              Import Questions
            </button>

            {/* Import Result */}
            {importResult && (
              <div className="mt-4 p-4 bg-gray-50 rounded-md">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Import Results</h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <div className="flex justify-between">
                    <span>Successful:</span>
                    <span className="font-medium text-green-600">{importResult.success_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Errors:</span>
                    <span className="font-medium text-red-600">{importResult.error_count}</span>
                  </div>
                </div>
                
                {importResult.errors && importResult.errors.length > 0 && (
                  <div className="mt-3">
                    <h4 className="text-sm font-medium text-red-800 mb-1">Errors:</h4>
                    <div className="max-h-32 overflow-y-auto">
                      {importResult.errors.slice(0, 5).map((error: any, index: number) => (
                        <div key={index} className="text-xs text-red-700 mb-1">
                          Row {error.row}: {error.message}
                        </div>
                      ))}
                      {importResult.errors.length > 5 && (
                        <div className="text-xs text-red-700">
                          ... and {importResult.errors.length - 5} more errors
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* CSV Format Guide */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">CSV Format Guide</h2>
        <p className="text-sm text-gray-600 mb-4">
          Your CSV file should include the following columns:
        </p>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Column
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Required
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Example
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">type</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Yes</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Question type</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">aptitude</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">category</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Yes</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Question category</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">logical_reasoning</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">difficulty</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Yes</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Difficulty level (1-5)</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">3</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">title</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Yes</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Question title</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Find the next number</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">content</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Yes</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Question content</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">What is 2 + 2?</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">options</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-600">Conditional</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Options (pipe-separated)</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">3|4|5|6</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">correct_answer</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">Yes</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Correct answer</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">4</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">company_tags</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">No</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Company tags (pipe-separated)</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Google|Microsoft</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ImportExport;