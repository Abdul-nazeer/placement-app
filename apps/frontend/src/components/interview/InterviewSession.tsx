import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  MicrophoneIcon,
  VideoCameraIcon,
  ClockIcon,
  ArrowRightIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { InterviewService } from '../../services/interview';
import {
  InterviewSessionWithDetails,
  InterviewQuestion,
  InterviewResponse,
  InterviewStatus,
  VideoRecordingState,
  InterviewTimer,
  AIInterviewerMessage
} from '../../types/interview';

export const InterviewSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  
  // Session state
  const [session, setSession] = useState<InterviewSessionWithDetails | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Interview state
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [aiMessage, setAiMessage] = useState<AIInterviewerMessage | null>(null);
  
  // Recording state
  const [videoState, setVideoState] = useState<VideoRecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    recordedChunks: []
  });
  
  // Timer state
  const [timer, setTimer] = useState<InterviewTimer>({
    totalTime: 0,
    elapsedTime: 0,
    questionTime: 0,
    isRunning: false,
    isPaused: false
  });
  
  // Response state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [thinkingTime, setThinkingTime] = useState(0);
  const [questionStartTime, setQuestionStartTime] = useState<Date | null>(null);
  
  // Refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const thinkingTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (sessionId) {
      loadSession();
    }
    
    return () => {
      stopAllTimers();
      stopRecording();
    };
  }, [sessionId]);

  useEffect(() => {
    if (interviewStarted && !timer.isRunning) {
      startTimer();
    }
  }, [interviewStarted]);

  const loadSession = async () => {
    try {
      setLoading(true);
      const sessionData = await InterviewService.getSession(sessionId!);
      setSession(sessionData);
      
      if (sessionData.status === InterviewStatus.IN_PROGRESS) {
        setInterviewStarted(true);
        setCurrentQuestionIndex(sessionData.current_question_index);
        
        if (sessionData.questions.length > sessionData.current_question_index) {
          setCurrentQuestion(sessionData.questions[sessionData.current_question_index]);
        } else {
          await loadNextQuestion();
        }
      } else if (sessionData.status === InterviewStatus.COMPLETED) {
        navigate(`/interview/results/${sessionId}`);
        return;
      }
      
      // Load AI welcome message
      if (sessionData.status === InterviewStatus.SCHEDULED) {
        const welcomeMessage = await InterviewService.getAIMessage(sessionId!, 'introduction');
        setAiMessage(welcomeMessage);
      }
      
    } catch (err) {
      setError('Failed to load interview session');
      console.error('Session load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadNextQuestion = async () => {
    try {
      const question = await InterviewService.getNextQuestion(sessionId!);
      setCurrentQuestion(question);
      setQuestionStartTime(new Date());
      setThinkingTime(0);
      
      // Start thinking timer
      if (thinkingTimerRef.current) {
        clearInterval(thinkingTimerRef.current);
      }
      thinkingTimerRef.current = setInterval(() => {
        setThinkingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('Failed to load next question:', err);
      setError('Failed to load next question');
    }
  };

  const startInterview = async () => {
    try {
      await InterviewService.startSession(sessionId!);
      setInterviewStarted(true);
      
      if (!currentQuestion) {
        await loadNextQuestion();
      }
      
      // Initialize camera if video recording is enabled
      if (session?.enable_video_recording) {
        await initializeCamera();
      }
      
    } catch (err) {
      setError('Failed to start interview');
      console.error('Start interview error:', err);
    }
  };

  const initializeCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: session?.enable_video_recording,
        audio: session?.enable_audio_recording
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      setVideoState(prev => ({ ...prev, mediaStream: stream }));
      
    } catch (err) {
      console.error('Camera initialization error:', err);
      setError('Failed to access camera/microphone');
    }
  };

  const startRecording = () => {
    if (!videoState.mediaStream) return;
    
    try {
      const mediaRecorder = new MediaRecorder(videoState.mediaStream);
      const chunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        setVideoState(prev => ({ ...prev, recordedChunks: chunks }));
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      
      setVideoState(prev => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        duration: 0
      }));
      
      // Stop thinking timer when recording starts
      if (thinkingTimerRef.current) {
        clearInterval(thinkingTimerRef.current);
      }
      
    } catch (err) {
      console.error('Recording start error:', err);
      setError('Failed to start recording');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && videoState.isRecording) {
      mediaRecorderRef.current.pause();
      setVideoState(prev => ({ ...prev, isPaused: true }));
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && videoState.isPaused) {
      mediaRecorderRef.current.resume();
      setVideoState(prev => ({ ...prev, isPaused: false }));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && videoState.isRecording) {
      mediaRecorderRef.current.stop();
      setVideoState(prev => ({
        ...prev,
        isRecording: false,
        isPaused: false
      }));
    }
  };

  const submitResponse = async () => {
    if (!currentQuestion) return;
    
    try {
      setIsSubmitting(true);
      
      // Stop recording if active
      if (videoState.isRecording) {
        stopRecording();
        
        // Wait for recording to stop and process
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      const responseData = {
        response_duration: videoState.duration,
        thinking_time: thinkingTime
      };
      
      // Submit response
      let response: InterviewResponse;
      
      if (videoState.recordedChunks.length > 0) {
        const recordingBlob = new Blob(videoState.recordedChunks, { type: 'video/webm' });
        const recordingFile = new File([recordingBlob], 'response.webm', { type: 'video/webm' });
        
        if (session?.enable_video_recording) {
          response = await InterviewService.uploadVideoRecording(
            sessionId!,
            currentQuestion.id,
            recordingFile,
            videoState.duration,
            thinkingTime
          );
        } else {
          response = await InterviewService.uploadAudioRecording(
            sessionId!,
            currentQuestion.id,
            recordingFile,
            videoState.duration,
            thinkingTime
          );
        }
      } else {
        response = await InterviewService.submitResponse(
          sessionId!,
          currentQuestion.id,
          responseData
        );
      }
      
      // Move to next question or complete interview
      const nextIndex = currentQuestionIndex + 1;
      
      if (nextIndex >= (session?.question_count || 0)) {
        await completeInterview();
      } else {
        setCurrentQuestionIndex(nextIndex);
        await loadNextQuestion();
        
        // Reset recording state
        setVideoState(prev => ({
          ...prev,
          recordedChunks: [],
          duration: 0
        }));
      }
      
    } catch (err) {
      setError('Failed to submit response');
      console.error('Submit response error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const completeInterview = async () => {
    try {
      await InterviewService.completeSession(sessionId!);
      navigate(`/interview/results/${sessionId}`);
    } catch (err) {
      setError('Failed to complete interview');
      console.error('Complete interview error:', err);
    }
  };

  const startTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }
    
    timerIntervalRef.current = setInterval(() => {
      setTimer(prev => ({
        ...prev,
        elapsedTime: prev.elapsedTime + 1,
        questionTime: prev.questionTime + 1
      }));
      
      if (videoState.isRecording) {
        setVideoState(prev => ({
          ...prev,
          duration: prev.duration + 1
        }));
      }
    }, 1000);
    
    setTimer(prev => ({ ...prev, isRunning: true }));
  };

  const stopAllTimers = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }
    if (thinkingTimerRef.current) {
      clearInterval(thinkingTimerRef.current);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
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
            onClick={() => navigate('/interview')}
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
            onClick={() => navigate('/interview')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">{session.title}</h1>
              <p className="text-sm text-gray-600">
                {session.company_name && `${session.company_name} • `}
                {session.position_title}
              </p>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Progress */}
              <div className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {session.question_count}
              </div>
              
              {/* Timer */}
              <div className="flex items-center text-sm text-gray-600">
                <ClockIcon className="h-4 w-4 mr-1" />
                {formatTime(timer.elapsedTime)}
              </div>
              
              {/* Progress Bar */}
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentQuestionIndex + 1) / session.question_count) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!interviewStarted ? (
          /* Pre-Interview Screen */
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Start?</h2>
              
              {aiMessage && (
                <div className="bg-blue-50 rounded-lg p-4 mb-6">
                  <p className="text-blue-800">{aiMessage.text}</p>
                </div>
              )}
              
              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-center text-gray-600">
                  <ClockIcon className="h-5 w-5 mr-2" />
                  Duration: {session.total_duration} minutes
                </div>
                <div className="flex items-center justify-center text-gray-600">
                  <DocumentTextIcon className="h-5 w-5 mr-2" />
                  Questions: {session.question_count}
                </div>
                {session.enable_video_recording && (
                  <div className="flex items-center justify-center text-gray-600">
                    <VideoCameraIcon className="h-5 w-5 mr-2" />
                    Video recording enabled
                  </div>
                )}
              </div>
              
              <button
                onClick={startInterview}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Start Interview
              </button>
            </div>
          </div>
        ) : (
          /* Interview Screen */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Video/Camera Section */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Video</h3>
                
                <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video mb-4">
                  {session.enable_video_recording ? (
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <MicrophoneIcon className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                  
                  {/* Recording Indicator */}
                  {videoState.isRecording && (
                    <div className="absolute top-4 left-4 flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
                      <span className="text-white text-sm font-medium">
                        REC {formatTime(videoState.duration)}
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Recording Controls */}
                <div className="flex justify-center space-x-3">
                  {!videoState.isRecording ? (
                    <button
                      onClick={startRecording}
                      className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Start Recording
                    </button>
                  ) : (
                    <>
                      {!videoState.isPaused ? (
                        <button
                          onClick={pauseRecording}
                          className="flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                        >
                          <PauseIcon className="h-4 w-4 mr-2" />
                          Pause
                        </button>
                      ) : (
                        <button
                          onClick={resumeRecording}
                          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          <PlayIcon className="h-4 w-4 mr-2" />
                          Resume
                        </button>
                      )}
                      
                      <button
                        onClick={stopRecording}
                        className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                      >
                        <StopIcon className="h-4 w-4 mr-2" />
                        Stop
                      </button>
                    </>
                  )}
                </div>
                
                {/* Thinking Time */}
                {thinkingTime > 0 && !videoState.isRecording && (
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600">
                      Thinking time: {formatTime(thinkingTime)}
                    </p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Question Section */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6">
                {currentQuestion ? (
                  <>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Question {currentQuestionIndex + 1}
                      </h3>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                        {currentQuestion.category.replace('_', ' ')}
                      </span>
                    </div>
                    
                    <div className="mb-6">
                      <p className="text-gray-900 text-lg leading-relaxed">
                        {currentQuestion.question_text}
                      </p>
                    </div>
                    
                    {currentQuestion.context_information && (
                      <div className="bg-gray-50 rounded-lg p-4 mb-6">
                        <h4 className="font-medium text-gray-900 mb-2">Context:</h4>
                        <p className="text-gray-700">{currentQuestion.context_information}</p>
                      </div>
                    )}
                    
                    {currentQuestion.evaluation_criteria.length > 0 && (
                      <div className="mb-6">
                        <h4 className="font-medium text-gray-900 mb-2">Evaluation Criteria:</h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                          {currentQuestion.evaluation_criteria.map((criteria, index) => (
                            <li key={index}>{criteria}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-600">
                        Expected duration: {Math.floor(currentQuestion.expected_duration / 60)} minutes
                      </div>
                      
                      <button
                        onClick={submitResponse}
                        disabled={isSubmitting || (!videoState.recordedChunks.length && !videoState.isRecording)}
                        className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isSubmitting ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Submitting...
                          </>
                        ) : (
                          <>
                            {currentQuestionIndex + 1 >= session.question_count ? (
                              <>
                                <CheckCircleIcon className="h-4 w-4 mr-2" />
                                Complete Interview
                              </>
                            ) : (
                              <>
                                <ArrowRightIcon className="h-4 w-4 mr-2" />
                                Next Question
                              </>
                            )}
                          </>
                        )}
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading next question...</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};