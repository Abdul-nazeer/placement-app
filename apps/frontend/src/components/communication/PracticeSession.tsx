/**
 * Communication practice session component
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeftIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { AudioRecorder } from './AudioRecorder';
import { SpeechAnalysisDashboard } from './SpeechAnalysisDashboard';
import { communicationService } from '../../services/communication';
import { 
  CommunicationSessionWithPrompt, 
  CommunicationRecording,
  CommunicationAnalysis 
} from '../../types/communication';

export const PracticeSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  
  const [session, setSession] = useState<CommunicationSessionWithPrompt | null>(null);
  const [recording, setRecording] = useState<CommunicationRecording | null>(null);
  const [analysis, setAnalysis] = useState<CommunicationAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'prompt' | 'record' | 'analyze'>('prompt');

  useEffect(() => {
    if (sessionId) {
      loadSession();
    }
  }, [sessionId]);

  const loadSession = async () => {
    try {
      setLoading(true);
      const sessionData = await communicationService.getSessionById(sessionId!);
      setSession(sessionData);
      
      // If session has recordings, load the latest one
      if (sessionData.status === 'completed') {
        // TODO: Load existing recordings and analysis
        setCurrentStep('analyze');
      } else {
        setCurrentStep('prompt');
      }
    } catch (err) {
      setError('Failed to load practice session');
      console.error('Session load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartRecording = () => {
    setCurrentStep('record');
  };

  const handleRecordingComplete = (audioBlob: Blob, duration: number) => {
    console.log('Recording completed:', { duration, size: audioBlob.size });
  };

  const handleUploadRecording = async (audioBlob: Blob, duration: number) => {
    try {
      setUploading(true);
      
      // Convert blob to file
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      
      // Upload recording
      const recordingData = await communicationService.uploadAudioRecording(
        sessionId!,
        audioFile,
        duration
      );
      
      setRecording(recordingData);
      
      // Wait a moment for processing to start
      setTimeout(async () => {
        try {
          const analysisData = await communicationService.getRecordingAnalysis(recordingData.id);
          setAnalysis(analysisData);
          setCurrentStep('analyze');
          
          // Update session status
          await communicationService.updateSession(sessionId!, {
            status: 'completed',
            overall_score: analysisData.overall_score || undefined
          });
          
        } catch (err) {
          console.error('Analysis load error:', err);
          // Analysis might still be processing, show recording uploaded state
          setCurrentStep('analyze');
        }
      }, 2000);
      
    } catch (err) {
      setError('Failed to upload recording');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleRetryRecording = () => {
    setRecording(null);
    setAnalysis(null);
    setCurrentStep('record');
  };

  const handleFinishSession = () => {
    navigate('/communication');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/communication')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Session not found</p>
          <button
            onClick={() => navigate('/communication')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/communication')}
            className="mr-4 p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeftIcon className="h-6 w-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {session.prompt?.title || 'Communication Practice'}
            </h1>
            <p className="text-gray-600">
              {session.session_type.replace('_', ' ')} • 
              {session.prompt && ` Level ${session.prompt.difficulty_level}`}
            </p>
          </div>
        </div>
        
        {/* Progress Steps */}
        <div className="flex items-center space-x-4">
          <div className={`flex items-center ${currentStep === 'prompt' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              currentStep === 'prompt' ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}>
              1
            </div>
            <span className="ml-2 text-sm font-medium">Prompt</span>
          </div>
          
          <div className={`flex items-center ${currentStep === 'record' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              currentStep === 'record' ? 'bg-blue-600 text-white' : 
              currentStep === 'analyze' ? 'bg-green-600 text-white' : 'bg-gray-200'
            }`}>
              {currentStep === 'analyze' ? <CheckCircleIcon className="h-5 w-5" /> : '2'}
            </div>
            <span className="ml-2 text-sm font-medium">Record</span>
          </div>
          
          <div className={`flex items-center ${currentStep === 'analyze' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              currentStep === 'analyze' ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}>
              3
            </div>
            <span className="ml-2 text-sm font-medium">Analyze</span>
          </div>
        </div>
      </div>

      {/* Content */}
      {currentStep === 'prompt' && (
        <div className="space-y-6">
          {/* Prompt Display */}
          {session.prompt && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-4">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Practice Scenario</h2>
                <p className="text-gray-600">{session.prompt.description}</p>
              </div>
              
              <div className="bg-blue-50 rounded-lg p-4 mb-4">
                <h3 className="font-medium text-blue-900 mb-2">Your Prompt:</h3>
                <p className="text-blue-800">{session.prompt.prompt_text}</p>
              </div>
              
              {session.prompt.time_limit && (
                <div className="flex items-center text-sm text-gray-500 mb-4">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  Suggested time limit: {Math.floor(session.prompt.time_limit / 60)} minutes
                </div>
              )}
              
              {session.prompt.evaluation_criteria && session.prompt.evaluation_criteria.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">Evaluation Criteria:</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                    {session.prompt.evaluation_criteria.map((criteria, index) => (
                      <li key={index}>{criteria}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {/* Instructions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Instructions</h2>
            <div className="space-y-3 text-gray-600">
              <p>1. Read the prompt carefully and take a moment to think about your response</p>
              <p>2. Click "Start Recording" when you're ready to begin</p>
              <p>3. Speak clearly and naturally - imagine you're in a real interview</p>
              <p>4. You can pause and resume recording if needed</p>
              <p>5. When finished, your recording will be analyzed for feedback</p>
            </div>
            
            <div className="mt-6">
              <button
                onClick={handleStartRecording}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Start Recording
              </button>
            </div>
          </div>
        </div>
      )}

      {currentStep === 'record' && (
        <div className="space-y-6">
          {/* Prompt Reminder */}
          {session.prompt && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">Remember your prompt:</h3>
              <p className="text-blue-800">{session.prompt.prompt_text}</p>
            </div>
          )}
          
          {/* Audio Recorder */}
          <AudioRecorder
            onRecordingComplete={handleRecordingComplete}
            onUpload={handleUploadRecording}
            maxDuration={session.prompt?.time_limit || 300}
            disabled={uploading}
          />
          
          {uploading && (
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-yellow-600 mr-3"></div>
                <p className="text-yellow-800">Uploading and analyzing your recording...</p>
              </div>
            </div>
          )}
        </div>
      )}

      {currentStep === 'analyze' && (
        <div className="space-y-6">
          {recording && !analysis && (
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                <p className="text-blue-800">Analyzing your recording... This may take a few moments.</p>
              </div>
            </div>
          )}
          
          {analysis && (
            <SpeechAnalysisDashboard 
              analysis={analysis}
              recording={recording}
            />
          )}
          
          <div className="flex justify-between">
            <button
              onClick={handleRetryRecording}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Record Again
            </button>
            
            <button
              onClick={handleFinishSession}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Finish Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
};