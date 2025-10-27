"""Create coding challenge schema

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    difficulty_enum = postgresql.ENUM('easy', 'medium', 'hard', name='difficultylevel')
    difficulty_enum.create(op.get_bind())
    
    language_enum = postgresql.ENUM('python', 'java', 'cpp', 'javascript', name='languagetype')
    language_enum.create(op.get_bind())
    
    execution_status_enum = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed', 'timeout', 'memory_exceeded', 
        name='executionstatus'
    )
    execution_status_enum.create(op.get_bind())
    
    # Create coding_challenges table
    op.create_table(
        'coding_challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('difficulty', difficulty_enum, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('topic_tags', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('company_tags', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('time_limit', sa.Integer, server_default='5000'),
        sa.Column('memory_limit', sa.Integer, server_default='256'),
        sa.Column('template_code', postgresql.JSONB, server_default='{}'),
        sa.Column('solution_approach', sa.Text),
        sa.Column('hints', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('is_active', sa.Boolean, server_default='true'),
    )
    
    # Create indexes for coding_challenges
    op.create_index('idx_coding_challenges_difficulty', 'coding_challenges', ['difficulty'])
    op.create_index('idx_coding_challenges_category', 'coding_challenges', ['category'])
    op.create_index('idx_coding_challenges_topic_tags', 'coding_challenges', ['topic_tags'], postgresql_using='gin')
    op.create_index('idx_coding_challenges_company_tags', 'coding_challenges', ['company_tags'], postgresql_using='gin')
    op.create_index('idx_coding_challenges_active', 'coding_challenges', ['is_active'])
    op.create_index('idx_coding_challenges_created_at', 'coding_challenges', ['created_at'])
    
    # Create test_cases table
    op.create_table(
        'test_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coding_challenges.id'), nullable=False),
        sa.Column('input_data', sa.Text, nullable=False),
        sa.Column('expected_output', sa.Text, nullable=False),
        sa.Column('is_sample', sa.Boolean, server_default='false'),
        sa.Column('is_hidden', sa.Boolean, server_default='true'),
        sa.Column('weight', sa.Float, server_default='1.0'),
        sa.Column('explanation', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes for test_cases
    op.create_index('idx_test_cases_challenge_id', 'test_cases', ['challenge_id'])
    op.create_index('idx_test_cases_sample', 'test_cases', ['is_sample'])
    op.create_index('idx_test_cases_hidden', 'test_cases', ['is_hidden'])
    
    # Create code_submissions table
    op.create_table(
        'code_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coding_challenges.id'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_sessions.id')),
        sa.Column('language', language_enum, nullable=False),
        sa.Column('code', sa.Text, nullable=False),
        sa.Column('status', execution_status_enum, server_default='pending'),
        sa.Column('score', sa.Float, server_default='0.0'),
        sa.Column('total_test_cases', sa.Integer, server_default='0'),
        sa.Column('passed_test_cases', sa.Integer, server_default='0'),
        sa.Column('execution_time', sa.Float),
        sa.Column('memory_usage', sa.Float),
        sa.Column('test_results', postgresql.JSONB, server_default='[]'),
        sa.Column('compilation_error', sa.Text),
        sa.Column('runtime_error', sa.Text),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('executed_at', sa.DateTime(timezone=True)),
    )
    
    # Create indexes for code_submissions
    op.create_index('idx_code_submissions_user_id', 'code_submissions', ['user_id'])
    op.create_index('idx_code_submissions_challenge_id', 'code_submissions', ['challenge_id'])
    op.create_index('idx_code_submissions_session_id', 'code_submissions', ['session_id'])
    op.create_index('idx_code_submissions_status', 'code_submissions', ['status'])
    op.create_index('idx_code_submissions_language', 'code_submissions', ['language'])
    op.create_index('idx_code_submissions_submitted_at', 'code_submissions', ['submitted_at'])
    op.create_index('idx_code_submissions_score', 'code_submissions', ['score'])
    
    # Create code_executions table
    op.create_table(
        'code_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('code_submissions.id'), nullable=False),
        sa.Column('container_id', sa.String(255)),
        sa.Column('language', language_enum, nullable=False),
        sa.Column('cpu_time', sa.Float),
        sa.Column('wall_time', sa.Float),
        sa.Column('memory_peak', sa.Float),
        sa.Column('security_violations', postgresql.JSONB, server_default='[]'),
        sa.Column('resource_violations', postgresql.JSONB, server_default='[]'),
        sa.Column('stdout', sa.Text),
        sa.Column('stderr', sa.Text),
        sa.Column('exit_code', sa.Integer),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes for code_executions
    op.create_index('idx_code_executions_submission_id', 'code_executions', ['submission_id'])
    op.create_index('idx_code_executions_language', 'code_executions', ['language'])
    op.create_index('idx_code_executions_created_at', 'code_executions', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('code_executions')
    op.drop_table('code_submissions')
    op.drop_table('test_cases')
    op.drop_table('coding_challenges')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS executionstatus')
    op.execute('DROP TYPE IF EXISTS languagetype')
    op.execute('DROP TYPE IF EXISTS difficultylevel')