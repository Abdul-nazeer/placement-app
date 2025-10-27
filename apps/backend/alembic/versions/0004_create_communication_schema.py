"""Create communication schema

Revision ID: 0004
Revises: 0003
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create communication_prompts table
    op.create_table('communication_prompts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('evaluation_criteria', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create communication_sessions table
    op.create_table('communication_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=False),
        sa.Column('prompt_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prompt_id'], ['communication_prompts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create communication_recordings table
    op.create_table('communication_recordings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('audio_file_path', sa.String(length=500), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('processing_status', sa.String(length=20), nullable=False),
        sa.Column('analysis_results', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['communication_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create communication_analyses table
    op.create_table('communication_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recording_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('words_per_minute', sa.Float(), nullable=True),
        sa.Column('pause_frequency', sa.Float(), nullable=True),
        sa.Column('average_pause_duration', sa.Float(), nullable=True),
        sa.Column('filler_word_count', sa.Integer(), nullable=True),
        sa.Column('filler_word_percentage', sa.Float(), nullable=True),
        sa.Column('grammar_score', sa.Float(), nullable=True),
        sa.Column('vocabulary_complexity', sa.Float(), nullable=True),
        sa.Column('sentence_structure_score', sa.Float(), nullable=True),
        sa.Column('clarity_score', sa.Float(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('coherence_score', sa.Float(), nullable=True),
        sa.Column('fluency_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('filler_words_detected', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recording_id'], ['communication_recordings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create communication_progress table
    op.create_table('communication_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('skill_category', sa.String(length=50), nullable=False),
        sa.Column('current_level', sa.Float(), nullable=False),
        sa.Column('sessions_completed', sa.Integer(), nullable=False),
        sa.Column('total_practice_time', sa.Integer(), nullable=False),
        sa.Column('last_session_date', sa.DateTime(), nullable=True),
        sa.Column('improvement_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_communication_sessions_user_id', 'communication_sessions', ['user_id'])
    op.create_index('idx_communication_sessions_status', 'communication_sessions', ['status'])
    op.create_index('idx_communication_sessions_type', 'communication_sessions', ['session_type'])
    op.create_index('idx_communication_recordings_session_id', 'communication_recordings', ['session_id'])
    op.create_index('idx_communication_recordings_status', 'communication_recordings', ['processing_status'])
    op.create_index('idx_communication_progress_user_skill', 'communication_progress', ['user_id', 'skill_category'])
    op.create_index('idx_communication_prompts_category', 'communication_prompts', ['category'])
    op.create_index('idx_communication_prompts_difficulty', 'communication_prompts', ['difficulty_level'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_communication_prompts_difficulty')
    op.drop_index('idx_communication_prompts_category')
    op.drop_index('idx_communication_progress_user_skill')
    op.drop_index('idx_communication_recordings_status')
    op.drop_index('idx_communication_recordings_session_id')
    op.drop_index('idx_communication_sessions_type')
    op.drop_index('idx_communication_sessions_status')
    op.drop_index('idx_communication_sessions_user_id')
    
    # Drop tables
    op.drop_table('communication_progress')
    op.drop_table('communication_analyses')
    op.drop_table('communication_recordings')
    op.drop_table('communication_sessions')
    op.drop_table('communication_prompts')