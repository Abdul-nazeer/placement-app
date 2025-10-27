import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import {
  PlayIcon,
  PaperAirplaneIcon,
  ClockIcon,
  CpuChipIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  LightBulbIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import CodeEditor from './CodeEditor';
import { CodingService } from '../../services/coding';
import { LanguageType, CodeSubmission, TestCase } from '../../types/coding';

const ChallengeInterface: React.FC = () => {
  const { challengeId } = useParams<{ challengeId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedLanguage, setSelectedLanguage] = useState<LanguageType>('python');
  const [code, setCode] = useState('');
  const [activeTab, setActiveTab] = useState<'description' | 'submissions' | 'hints'>('description');
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [showHints, setShowHints] = useState(false);

  // Fetch challenge details
  const { data: challenge, isLoading, error } = useQuery({
    queryKey: ['challenge', challengeId],
    queryFn: () => challengeId ? CodingService.getChallenge(challengeId) : null,
    enabled: !!challengeId
  });

  // Fetch user submissions for this challenge
  const { data: submissions } = useQuery({
    queryKey: ['submissions', challengeId],
    queryFn: () => challengeId ? CodingService.getUserSubmissions(challengeId) : [],
    enabled: !!challengeId
  });

  // Fetch supported languages
  const { data: supportedLanguages } = useQuery({
    queryKey: ['supported-languages'],
    queryFn: CodingService.getSupportedLanguages
  });

  // Submit code mutation
  const submitCodeMutation = useMutation({
    mutationFn: CodingService.submitCode,
    onSuccess: (submission) => {
      toast.success('Code submitted successfully!');
      queryClient.invalidateQueries(['submissions', challengeId]);
      // Poll for results
      pollSubmissionResult(submission.id);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to submit code');
      setIsRunning(false);
    }
  });

  // Initialize code with template when challenge loads
  useEffect(() => {
    if (challenge && challenge.template_code[selectedLanguage]) {
      setCode(challenge.template_code[selectedLanguage]);
    }
  }, [challenge, selectedLanguage]);

  const pollSubmissionResult = async (submissionId: string) => {
    const maxAttempts = 30; // 30 seconds max
    let attempts = 0;

    const poll = async () => {
      try {
        const submission = await CodingService.getSubmission(submissionId);
        
        if (submission.status === 'completed' || submission.status === 'failed' || 
            submission.status === 'timeout' || submission.status === 'memory_exceeded') {
          setIsRunning(false);
          setTestResults(submission.test_results);
          
          if (submission.status === 'completed') {
            const passedTests = submission.passed_test_cases;
            const totalTests = submission.total_test_cases;
            
            if (passedTests === totalTests) {
              toast.success(`All tests passed! Score: ${submission.score.toFixed(1)}%`);
            } else {
              toast.error(`${passedTests}/${totalTests} tests passed. Score: ${submission.score.toFixed(1)}%`);
            }
          } else {
            toast.error(`Execution failed: ${submission.status}`);
          }
          
          return;
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 1000);
        } else {
          setIsRunning(false);
          toast.error('Execution timeout - please try again');
        }
      } catch (error) {
        setIsRunning(false);
        toast.error('Failed to get execution results');
      }
    };

    poll();
  };

  const handleLanguageChange = (language: LanguageType) => {
    setSelectedLanguage(language);
    if (challenge?.template_code[language]) {
      setCode(challenge.template_code[language]);
    } else {
      setCode('');
    }
  };

  const handleRunCode = () => {
    if (!challengeId || !code.trim()) {
      toast.error('Please write some code first');
      return;
    }

    setIsRunning(true);
    setTestResults([]);
    
    submitCodeMutation.mutate({
      challenge_id: challengeId,
      language: selectedLanguage,
      code: code.trim()
    });
  };

  const getSampleTestCases = (): TestCase[] => {
    return challenge?.test_cases.filter(tc => tc.is_sample) || [];
  };

  const getDifficultyColor = (difficulty: string) => {
    return CodingService.getDifficultyColor(difficulty as any);
  };

  const getStatusIcon = (passed: boolean) => {
    return passed ? (
      <CheckCircleIcon className="h-5 w-5 text-green-500" />
    ) : (
      <XCircleIcon className="h-5 w-5 text-red-500" />
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Challenge not found</h1>
          <button
            onClick={() => navigate('/coding')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Back to Challenges
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/coding')}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{challenge.title}</h1>
                <div className="flex items-center space-x-4 mt-1">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(challenge.difficulty)}`}>
                    {challenge.difficulty.charAt(0).toUpperCase() + challenge.difficulty.slice(1)}
                  </span>
                  <span className="text-sm text-gray-500">{challenge.category}</span>
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {challenge.time_limit}ms
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <CpuChipIcon className="h-4 w-4 mr-1" />
                    {challenge.memory_limit}MB
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Problem Description */}
          <div className="bg-white rounded-lg shadow">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                <button
                  onClick={() => setActiveTab('description')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'description'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Description
                </button>
                <button
                  onClick={() => setActiveTab('submissions')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'submissions'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Submissions ({submissions?.length || 0})
                </button>
                {challenge.hints.length > 0 && (
                  <button
                    onClick={() => setActiveTab('hints')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'hints'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Hints
                  </button>
                )}
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'description' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Problem Statement</h3>
                    <div className="prose prose-sm max-w-none text-gray-700">
                      {challenge.description.split('\n').map((paragraph, index) => (
                        <p key={index} className="mb-3">{paragraph}</p>
                      ))}
                    </div>
                  </div>

                  {/* Sample Test Cases */}
                  {getSampleTestCases().length > 0 && (
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-3">Sample Test Cases</h3>
                      <div className="space-y-4">
                        {getSampleTestCases().map((testCase, index) => (
                          <div key={testCase.id} className="bg-gray-50 p-4 rounded-lg">
                            <h4 className="font-medium text-gray-900 mb-2">Example {index + 1}</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium text-gray-700 mb-1">Input:</p>
                                <pre className="text-sm bg-white p-2 rounded border font-mono">
                                  {testCase.input_data}
                                </pre>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-700 mb-1">Output:</p>
                                <pre className="text-sm bg-white p-2 rounded border font-mono">
                                  {testCase.expected_output}
                                </pre>
                              </div>
                            </div>
                            {testCase.explanation && (
                              <div className="mt-3">
                                <p className="text-sm font-medium text-gray-700 mb-1">Explanation:</p>
                                <p className="text-sm text-gray-600">{testCase.explanation}</p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Tags */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Tags</h3>
                    <div className="flex flex-wrap gap-2">
                      {challenge.topic_tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {tag}
                        </span>
                      ))}
                      {challenge.company_tags.map((company) => (
                        <span
                          key={company}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                        >
                          {company}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'submissions' && (
                <div className="space-y-4">
                  {submissions && submissions.length > 0 ? (
                    submissions.map((submission) => (
                      <div key={submission.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${CodingService.getStatusColor(submission.status)}`}>
                              {submission.status}
                            </span>
                            <span className="text-sm text-gray-500">
                              {CodingService.getLanguageDisplayName(submission.language)}
                            </span>
                          </div>
                          <span className="text-sm text-gray-500">
                            {new Date(submission.submitted_at).toLocaleString()}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span>Score: {submission.score.toFixed(1)}%</span>
                          <span>Tests: {submission.passed_test_cases}/{submission.total_test_cases}</span>
                          {submission.execution_time && (
                            <span>Time: {CodingService.formatExecutionTime(submission.execution_time)}</span>
                          )}
                          {submission.memory_usage && (
                            <span>Memory: {CodingService.formatMemoryUsage(submission.memory_usage)}</span>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No submissions yet</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Submit your first solution to see it here.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'hints' && (
                <div className="space-y-4">
                  {challenge.hints.map((hint, index) => (
                    <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex items-start">
                        <LightBulbIcon className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                        <div>
                          <h4 className="text-sm font-medium text-yellow-800 mb-1">
                            Hint {index + 1}
                          </h4>
                          <p className="text-sm text-yellow-700">{hint}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Code Editor */}
          <div className="bg-white rounded-lg shadow">
            <div className="border-b border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <label className="text-sm font-medium text-gray-700">Language:</label>
                  <select
                    value={selectedLanguage}
                    onChange={(e) => handleLanguageChange(e.target.value as LanguageType)}
                    className="block w-32 px-3 py-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  >
                    {supportedLanguages?.map((lang) => (
                      <option key={lang} value={lang}>
                        {CodingService.getLanguageDisplayName(lang as LanguageType)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleRunCode}
                    disabled={isRunning || !code.trim()}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isRunning ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Running...
                      </>
                    ) : (
                      <>
                        <PaperAirplaneIcon className="h-4 w-4 mr-2" />
                        Submit
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div className="p-6">
              <CodeEditor
                language={selectedLanguage}
                value={code}
                onChange={setCode}
                height="500px"
                onRun={handleRunCode}
                isRunning={isRunning}
                showToolbar={true}
              />
            </div>

            {/* Test Results */}
            {testResults.length > 0 && (
              <div className="border-t border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Test Results</h3>
                <div className="space-y-3">
                  {testResults.map((result, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      {getStatusIcon(result.passed)}
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-900">
                            Test Case {index + 1}
                          </span>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Time: {CodingService.formatExecutionTime(result.execution_time)}</span>
                            <span>Memory: {CodingService.formatMemoryUsage(result.memory_usage)}</span>
                          </div>
                        </div>
                        {!result.passed && result.error_message && (
                          <p className="text-sm text-red-600 mt-1">{result.error_message}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChallengeInterface;