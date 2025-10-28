# Pydantic schemas package

from .auth import (
    UserRegistration,
    UserLogin,
    UserResponse,
    UserProfileResponse,
    UserProfileUpdate,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    LogoutRequest,
    ErrorResponse
)

from .content import (
    # Category schemas
    CategoryCreate,
    CategoryUpdate,
    Category,
    
    # Tag schemas
    TagCreate,
    TagUpdate,
    Tag,
    
    # Company schemas
    CompanyCreate,
    CompanyUpdate,
    Company,
    
    # Question Collection schemas
    QuestionCollectionCreate,
    QuestionCollectionUpdate,
    QuestionCollection,
    
    # Question schemas
    QuestionCreate,
    QuestionUpdate,
    Question,
    
    # Test Session schemas
    TestSessionCreate,
    TestSessionUpdate,
    TestSession,
    
    # Submission schemas
    SubmissionCreate,
    SubmissionUpdate,
    Submission,
    
    # Search and filtering
    QuestionFilters,
    QuestionSearchResult,
    
    # Bulk operations
    BulkQuestionCreate,
    BulkQuestionUpdate,
    BulkOperationResult,
    
    # Analytics
    QuestionAnalytics,
    ContentAnalytics
)

from .coding import (
    # Enums
    DifficultyLevel,
    LanguageType,
    ExecutionStatus,
    
    # Test Case schemas
    TestCaseCreate,
    TestCaseUpdate,
    TestCase,
    
    # Coding Challenge schemas
    CodingChallengeCreate,
    CodingChallengeUpdate,
    CodingChallenge,
    CodingChallengeList,
    
    # Code Submission schemas
    CodeSubmissionCreate,
    CodeSubmissionUpdate,
    CodeSubmission,
    TestCaseResult,
    CodeExecutionResult,
    
    # Search and filtering
    CodingChallengeFilters,
    CodingChallengeSearchResult,
    
    # Analytics
    CodingChallengeAnalytics,
    UserCodingStats,
    
    # Bulk operations
    BulkChallengeCreate,
    
    # Code quality and plagiarism
    CodeQualityMetrics,
    PlagiarismResult
)

from .communication import (
    # Prompt schemas
    CommunicationPromptCreate,
    CommunicationPromptUpdate,
    CommunicationPrompt,
    
    # Session schemas
    CommunicationSessionCreate,
    CommunicationSessionUpdate,
    CommunicationSession,
    CommunicationSessionWithPrompt,
    
    # Recording and analysis schemas
    AudioUploadRequest,
    CommunicationRecording,
    CommunicationAnalysisCreate,
    CommunicationAnalysis,
    SpeechMetrics,
    LanguageMetrics,
    ContentMetrics,
    
    # Progress tracking
    CommunicationProgress,
    CommunicationProgressUpdate,
    
    # Dashboard and feedback
    CommunicationFeedback,
    CommunicationDashboard
)

from .resume import (
    # Resume data schemas
    ResumeSection,
    ContactInfo,
    WorkExperience,
    Education,
    Skill,
    StructuredResumeData,
    
    # Analysis schemas
    ATSAnalysis,
    ContentAnalysis,
    ResumeAnalysisResult,
    
    # CRUD schemas
    ResumeUpload,
    ResumeCreate,
    ResumeResponse,
    ResumeAnalysisResponse,
    
    # Version control
    ResumeVersionCreate,
    ResumeVersionResponse,
    
    # Templates
    ResumeTemplateResponse,
    
    # Optimization and comparison
    ResumeOptimizationRequest,
    ResumeComparisonRequest,
    ResumeComparisonResponse
)

from .interview import (
    # Interview session schemas
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionUpdate,
    InterviewSessionSummary,
    
    # Interview question schemas
    InterviewQuestionCreate,
    InterviewQuestionResponse,
    
    # Interview response schemas
    InterviewResponseCreate,
    InterviewResponseUpdate,
    InterviewResponseResponse,
    
    # Analytics and reporting
    InterviewAnalytics,
    
    # AI and real-time features
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    AIInterviewerMessage,
    WebSocketMessage,
    RealTimeProgress
)

__all__ = [
    # Auth schemas
    "UserRegistration",
    "UserLogin",
    "UserResponse",
    "UserProfileResponse",
    "UserProfileUpdate",
    "TokenResponse",
    "TokenRefresh",
    "PasswordChange",
    "LogoutRequest",
    "ErrorResponse",
    
    # Content management schemas
    "CategoryCreate",
    "CategoryUpdate",
    "Category",
    "TagCreate",
    "TagUpdate", 
    "Tag",
    "CompanyCreate",
    "CompanyUpdate",
    "Company",
    "QuestionCollectionCreate",
    "QuestionCollectionUpdate",
    "QuestionCollection",
    "QuestionCreate",
    "QuestionUpdate",
    "Question",
    "TestSessionCreate",
    "TestSessionUpdate",
    "TestSession",
    "SubmissionCreate",
    "SubmissionUpdate",
    "Submission",
    "QuestionFilters",
    "QuestionSearchResult",
    "BulkQuestionCreate",
    "BulkQuestionUpdate",
    "BulkOperationResult",
    "QuestionAnalytics",
    "ContentAnalytics",
    
    # Coding challenge schemas
    "DifficultyLevel",
    "LanguageType",
    "ExecutionStatus",
    "TestCaseCreate",
    "TestCaseUpdate",
    "TestCase",
    "CodingChallengeCreate",
    "CodingChallengeUpdate",
    "CodingChallenge",
    "CodingChallengeList",
    "CodeSubmissionCreate",
    "CodeSubmissionUpdate",
    "CodeSubmission",
    "TestCaseResult",
    "CodeExecutionResult",
    "CodingChallengeFilters",
    "CodingChallengeSearchResult",
    "CodingChallengeAnalytics",
    "UserCodingStats",
    "BulkChallengeCreate",
    "CodeQualityMetrics",
    "PlagiarismResult",
    
    # Communication assessment schemas
    "CommunicationPromptCreate",
    "CommunicationPromptUpdate",
    "CommunicationPrompt",
    "CommunicationSessionCreate",
    "CommunicationSessionUpdate",
    "CommunicationSession",
    "CommunicationSessionWithPrompt",
    "AudioUploadRequest",
    "CommunicationRecording",
    "CommunicationAnalysisCreate",
    "CommunicationAnalysis",
    "SpeechMetrics",
    "LanguageMetrics",
    "ContentMetrics",
    "CommunicationProgress",
    "CommunicationProgressUpdate",
    "CommunicationFeedback",
    "CommunicationDashboard",
    
    # Resume analysis schemas
    "ResumeSection",
    "ContactInfo",
    "WorkExperience",
    "Education",
    "Skill",
    "StructuredResumeData",
    "ATSAnalysis",
    "ContentAnalysis",
    "ResumeAnalysisResult",
    "ResumeUpload",
    "ResumeCreate",
    "ResumeResponse",
    "ResumeAnalysisResponse",
    "ResumeVersionCreate",
    "ResumeVersionResponse",
    "ResumeTemplateResponse",
    "ResumeOptimizationRequest",
    "ResumeComparisonRequest",
    "ResumeComparisonResponse",
    
    # Interview schemas
    "InterviewSessionCreate",
    "InterviewSessionResponse",
    "InterviewSessionUpdate",
    "InterviewSessionSummary",
    "InterviewQuestionCreate",
    "InterviewQuestionResponse",
    "InterviewResponseCreate",
    "InterviewResponseUpdate",
    "InterviewResponseResponse",
    "InterviewAnalytics",
    "QuestionGenerationRequest",
    "QuestionGenerationResponse",
    "AIInterviewerMessage",
    "WebSocketMessage",
    "RealTimeProgress"
]