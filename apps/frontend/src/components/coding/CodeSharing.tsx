import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
  ShareIcon,
  LinkIcon,
  EyeIcon,
  ChatBubbleOvalLeftIcon,
  UserGroupIcon,
  ClockIcon,
  CodeBracketIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';
import { CodingService } from '../../services/coding';
import { CodeSubmission, LanguageType } from '../../types/coding';
import CodeEditor from './CodeEditor';

interface CodeSharingProps {
  submission: CodeSubmission;
  onClose: () => void;
}

interface SharedCode {
  id: string;
  submission_id: string;
  title: string;
  description?: string;
  is_public: boolean;
  share_url: string;
  created_at: string;
  views: number;
  comments: CodeComment[];
}

interface CodeComment {
  id: string;
  user_id: string;
  user_name: string;
  content: string;
  line_number?: number;
  created_at: string;
}

interface ShareCodeRequest {
  submission_id: string;
  title: string;
  description?: string;
  is_public: boolean;
}

const CodeSharing = ({ submission, onClose }: CodeSharingProps) => {
  const [shareTitle, setShareTitle] = useState(`Solution for Challenge`);
  const [shareDescription, setShareDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [showShareForm, setShowShareForm] = useState(false);
  const [sharedCode, setSharedCode] = useState<SharedCode | null>(null);
  const [newComment, setNewComment] = useState('');

  // Share code mutation
  const shareCodeMutation = useMutation({
    mutationFn: async (shareData: ShareCodeRequest) => {
      // This would call your backend API
      const response = await fetch('/api/v1/coding/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(shareData)
      });
      return response.json();
    },
    onSuccess: (data) => {
      setSharedCode(data);
      setShowShareForm(false);
      toast.success('Code shared successfully!');
    },
    onError: () => {
      toast.error('Failed to share code');
    }
  });

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: async (comment: { shared_code_id: string; content: string; line_number?: number }) => {
      const response = await fetch('/api/v1/coding/share/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(comment)
      });
      return response.json();
    },
    onSuccess: () => {
      setNewComment('');
      toast.success('Comment added!');
      // Refresh comments
    },
    onError: () => {
      toast.error('Failed to add comment');
    }
  });

  const handleShare = () => {
    shareCodeMutation.mutate({
      submission_id: submission.id,
      title: shareTitle,
      description: shareDescription,
      is_public: isPublic
    });
  };

  const handleCopyShareUrl = async () => {
    if (sharedCode?.share_url) {
      try {
        await navigator.clipboard.writeText(sharedCode.share_url);
        toast.success('Share URL copied to clipboard!');
      } catch (err) {
        toast.error('Failed to copy URL');
      }
    }
  };

  const handleAddComment = () => {
    if (newComment.trim() && sharedCode) {
      addCommentMutation.mutate({
        shared_code_id: sharedCode.id,
        content: newComment.trim()
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <ShareIcon className="h-6 w-6 text-indigo-600" />
            <h3 className="text-lg font-medium text-gray-900">Share Code Solution</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <span className="sr-only">Close</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Code Preview */}
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-2">Code Preview</h4>
              <div className="bg-gray-50 p-3 rounded-lg text-sm">
                <div className="flex items-center space-x-4 mb-2">
                  <span className="font-medium">{CodingService.getLanguageDisplayName(submission.language)}</span>
                  <span className={`px-2 py-1 rounded text-xs ${CodingService.getStatusColor(submission.status)}`}>
                    {submission.status}
                  </span>
                  <span className="text-gray-500">Score: {submission.score.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <CodeEditor
              language={submission.language}
              value={submission.code}
              onChange={() => {}} // Read-only
              readOnly={true}
              height="400px"
              showToolbar={false}
            />

            {/* Submission Stats */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-2">Performance</h5>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Tests Passed:</span>
                  <span className="ml-2 font-medium">{submission.passed_test_cases}/{submission.total_test_cases}</span>
                </div>
                <div>
                  <span className="text-gray-500">Score:</span>
                  <span className="ml-2 font-medium">{submission.score.toFixed(1)}%</span>
                </div>
                {submission.execution_time && (
                  <div>
                    <span className="text-gray-500">Time:</span>
                    <span className="ml-2 font-medium">{CodingService.formatExecutionTime(submission.execution_time)}</span>
                  </div>
                )}
                {submission.memory_usage && (
                  <div>
                    <span className="text-gray-500">Memory:</span>
                    <span className="ml-2 font-medium">{CodingService.formatMemoryUsage(submission.memory_usage)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Share Options */}
          <div className="space-y-6">
            {!sharedCode && !showShareForm && (
              <div className="text-center py-8">
                <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Share Your Solution</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Share your code with the community to get feedback and help others learn.
                </p>
                <div className="mt-6">
                  <button
                    onClick={() => setShowShareForm(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                  >
                    <ShareIcon className="h-4 w-4 mr-2" />
                    Share Code
                  </button>
                </div>
              </div>
            )}

            {showShareForm && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={shareTitle}
                    onChange={(e) => setShareTitle(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Give your solution a title..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description (Optional)
                  </label>
                  <textarea
                    value={shareDescription}
                    onChange={(e) => setShareDescription(e.target.value)}
                    rows={3}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Explain your approach, complexity analysis, or any insights..."
                  />
                </div>

                <div className="flex items-center">
                  <input
                    id="is-public"
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is-public" className="ml-2 block text-sm text-gray-900">
                    Make this solution public
                  </label>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={handleShare}
                    disabled={shareCodeMutation.isLoading || !shareTitle.trim()}
                    className="flex-1 inline-flex justify-center items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {shareCodeMutation.isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Sharing...
                      </>
                    ) : (
                      <>
                        <ShareIcon className="h-4 w-4 mr-2" />
                        Share
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setShowShareForm(false)}
                    className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {sharedCode && (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ShareIcon className="h-5 w-5 text-green-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-green-800">
                        Code Shared Successfully!
                      </h3>
                      <div className="mt-2 text-sm text-green-700">
                        <p>Your solution is now available for others to view and learn from.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{sharedCode.title}</h4>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <EyeIcon className="h-4 w-4" />
                      <span>{sharedCode.views} views</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 mb-3">
                    <span className={`px-2 py-1 rounded text-xs ${isPublic ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {isPublic ? 'Public' : 'Private'}
                    </span>
                    <div className="flex items-center text-sm text-gray-500">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {new Date(sharedCode.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={sharedCode.share_url}
                      readOnly
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm"
                    />
                    <button
                      onClick={handleCopyShareUrl}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <DocumentDuplicateIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Comments Section */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 flex items-center">
                    <ChatBubbleOvalLeftIcon className="h-5 w-5 mr-2" />
                    Comments ({sharedCode.comments.length})
                  </h4>

                  {/* Add Comment */}
                  <div className="flex space-x-3">
                    <div className="flex-1">
                      <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        rows={2}
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                        placeholder="Add a comment..."
                      />
                    </div>
                    <button
                      onClick={handleAddComment}
                      disabled={!newComment.trim() || addCommentMutation.isLoading}
                      className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Comment
                    </button>
                  </div>

                  {/* Comments List */}
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {sharedCode.comments.map((comment) => (
                      <div key={comment.id} className="bg-white p-3 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-gray-900">{comment.user_name}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(comment.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{comment.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default CodeSharing;