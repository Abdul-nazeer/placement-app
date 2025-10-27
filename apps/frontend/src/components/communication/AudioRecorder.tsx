/**
 * Audio recorder component with real-time feedback
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  PauseIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';
import { RecordingState } from '../../types/communication';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob, duration: number) => void;
  onUpload?: (audioBlob: Blob, duration: number) => Promise<void>;
  maxDuration?: number; // in seconds
  disabled?: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  onUpload,
  maxDuration = 300, // 5 minutes default
  disabled = false
}) => {
  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0
  });
  const [isPlaying, setIsPlaying] = useState(false);
  const [uploading, setUploading] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      });
      
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        setRecordingState(prev => ({
          ...prev,
          audioBlob,
          audioUrl
        }));
        
        onRecordingComplete(audioBlob, recordingState.duration);
        
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start(1000); // Collect data every second
      
      setRecordingState(prev => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        duration: 0
      }));

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingState(prev => {
          const newDuration = prev.duration + 1;
          
          // Auto-stop at max duration
          if (newDuration >= maxDuration) {
            stopRecording();
            return prev;
          }
          
          return {
            ...prev,
            duration: newDuration
          };
        });
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      mediaRecorderRef.current.stop();
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      setRecordingState(prev => ({
        ...prev,
        isRecording: false,
        isPaused: false
      }));
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      if (recordingState.isPaused) {
        mediaRecorderRef.current.resume();
        // Resume timer
        timerRef.current = setInterval(() => {
          setRecordingState(prev => ({
            ...prev,
            duration: prev.duration + 1
          }));
        }, 1000);
      } else {
        mediaRecorderRef.current.pause();
        // Pause timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
      }
      
      setRecordingState(prev => ({
        ...prev,
        isPaused: !prev.isPaused
      }));
    }
  };

  const playRecording = () => {
    if (recordingState.audioUrl && audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleUpload = async () => {
    if (recordingState.audioBlob && onUpload) {
      try {
        setUploading(true);
        await onUpload(recordingState.audioBlob, recordingState.duration);
      } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload recording. Please try again.');
      } finally {
        setUploading(false);
      }
    }
  };

  const resetRecording = () => {
    if (recordingState.audioUrl) {
      URL.revokeObjectURL(recordingState.audioUrl);
    }
    
    setRecordingState({
      isRecording: false,
      isPaused: false,
      duration: 0
    });
    setIsPlaying(false);
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = (): number => {
    return (recordingState.duration / maxDuration) * 100;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="text-center">
        {/* Recording Status */}
        <div className="mb-6">
          {recordingState.isRecording ? (
            <div className="flex items-center justify-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${recordingState.isPaused ? 'bg-yellow-500' : 'bg-red-500 animate-pulse'}`}></div>
              <span className="text-lg font-medium text-gray-900">
                {recordingState.isPaused ? 'Paused' : 'Recording'}
              </span>
            </div>
          ) : recordingState.audioBlob ? (
            <div className="text-lg font-medium text-green-600">Recording Complete</div>
          ) : (
            <div className="text-lg font-medium text-gray-500">Ready to Record</div>
          )}
        </div>

        {/* Timer and Progress */}
        <div className="mb-6">
          <div className="text-3xl font-mono font-bold text-gray-900 mb-2">
            {formatDuration(recordingState.duration)}
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          
          <div className="text-sm text-gray-500">
            Max: {formatDuration(maxDuration)}
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex justify-center space-x-4 mb-6">
          {!recordingState.isRecording && !recordingState.audioBlob && (
            <button
              onClick={startRecording}
              disabled={disabled}
              className="flex items-center justify-center w-16 h-16 bg-red-600 text-white rounded-full hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <MicrophoneIcon className="h-8 w-8" />
            </button>
          )}

          {recordingState.isRecording && (
            <>
              <button
                onClick={pauseRecording}
                className="flex items-center justify-center w-12 h-12 bg-yellow-600 text-white rounded-full hover:bg-yellow-700 transition-colors"
              >
                {recordingState.isPaused ? (
                  <PlayIcon className="h-6 w-6" />
                ) : (
                  <PauseIcon className="h-6 w-6" />
                )}
              </button>
              
              <button
                onClick={stopRecording}
                className="flex items-center justify-center w-16 h-16 bg-gray-600 text-white rounded-full hover:bg-gray-700 transition-colors"
              >
                <StopIcon className="h-8 w-8" />
              </button>
            </>
          )}

          {recordingState.audioBlob && (
            <>
              <button
                onClick={playRecording}
                className="flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full hover:bg-green-700 transition-colors"
              >
                {isPlaying ? (
                  <PauseIcon className="h-6 w-6" />
                ) : (
                  <PlayIcon className="h-6 w-6" />
                )}
              </button>
              
              <button
                onClick={resetRecording}
                className="flex items-center justify-center w-12 h-12 bg-gray-600 text-white rounded-full hover:bg-gray-700 transition-colors"
              >
                <MicrophoneIcon className="h-6 w-6" />
              </button>
              
              {onUpload && (
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {uploading ? (
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  ) : (
                    <ArrowUpTrayIcon className="h-6 w-6" />
                  )}
                </button>
              )}
            </>
          )}
        </div>

        {/* Audio Element for Playback */}
        {recordingState.audioUrl && (
          <audio
            ref={audioRef}
            src={recordingState.audioUrl}
            onEnded={() => setIsPlaying(false)}
            className="hidden"
          />
        )}

        {/* Instructions */}
        <div className="text-sm text-gray-500">
          {!recordingState.isRecording && !recordingState.audioBlob && (
            <p>Click the microphone to start recording</p>
          )}
          {recordingState.isRecording && (
            <p>Click pause to pause or stop to finish recording</p>
          )}
          {recordingState.audioBlob && (
            <p>Play to review your recording or upload to analyze</p>
          )}
        </div>
      </div>
    </div>
  );
};