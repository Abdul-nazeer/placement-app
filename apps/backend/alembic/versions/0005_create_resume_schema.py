"""Create resume analysis schema

Revision ID: 0005
Revises: 0004
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # Create resumes table
    op.create_table('resumes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Float(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('structured_data', sa.JSON(), nullable=True),
        sa.Column('ats_score', sa.Float(), nullable=True),
        sa.Column('analysis_results', sa.JSON(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('processing_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_user_id'), 'resumes', ['user_id'], unique=False)
    op.create_index(op.f('ix_resumes_processing_status'), 'resumes', ['processing_status'], unique=False)
    op.create_index(op.f('ix_resumes_created_at'), 'resumes', ['created_at'], unique=False)

    # Create resume_versions table
    op.create_table('resume_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Float(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('ats_score', sa.Float(), nullable=True),
        sa.Column('analysis_results', sa.JSON(), nullable=True),
        sa.Column('changes_made', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_versions_resume_id'), 'resume_versions', ['resume_id'], unique=False)
    op.create_index(op.f('ix_resume_versions_version_number'), 'resume_versions', ['version_number'], unique=False)

    # Create resume_templates table
    op.create_table('resume_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('preview_image', sa.String(length=500), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('popularity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ats_friendly_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_templates_category'), 'resume_templates', ['category'], unique=False)
    op.create_index(op.f('ix_resume_templates_industry'), 'resume_templates', ['industry'], unique=False)
    op.create_index(op.f('ix_resume_templates_is_active'), 'resume_templates', ['is_active'], unique=False)

    # Create resume_analysis_jobs table
    op.create_table('resume_analysis_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_analysis_jobs_resume_id'), 'resume_analysis_jobs', ['resume_id'], unique=False)
    op.create_index(op.f('ix_resume_analysis_jobs_status'), 'resume_analysis_jobs', ['status'], unique=False)
    op.create_index(op.f('ix_resume_analysis_jobs_job_type'), 'resume_analysis_jobs', ['job_type'], unique=False)

    # Add indexes for better query performance
    op.create_index('ix_resumes_ats_score', 'resumes', ['ats_score'], unique=False)
    op.create_index('ix_resumes_file_type', 'resumes', ['file_type'], unique=False)
    op.create_index('ix_resume_templates_popularity', 'resume_templates', ['popularity_score'], unique=False)
    op.create_index('ix_resume_templates_ats_score', 'resume_templates', ['ats_friendly_score'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('ix_resume_templates_ats_score', table_name='resume_templates')
    op.drop_index('ix_resume_templates_popularity', table_name='resume_templates')
    op.drop_index('ix_resumes_file_type', table_name='resumes')
    op.drop_index('ix_resumes_ats_score', table_name='resumes')
    
    # Drop tables
    op.drop_index(op.f('ix_resume_analysis_jobs_job_type'), table_name='resume_analysis_jobs')
    op.drop_index(op.f('ix_resume_analysis_jobs_status'), table_name='resume_analysis_jobs')
    op.drop_index(op.f('ix_resume_analysis_jobs_resume_id'), table_name='resume_analysis_jobs')
    op.drop_table('resume_analysis_jobs')
    
    op.drop_index(op.f('ix_resume_templates_is_active'), table_name='resume_templates')
    op.drop_index(op.f('ix_resume_templates_industry'), table_name='resume_templates')
    op.drop_index(op.f('ix_resume_templates_category'), table_name='resume_templates')
    op.drop_table('resume_templates')
    
    op.drop_index(op.f('ix_resume_versions_version_number'), table_name='resume_versions')
    op.drop_index(op.f('ix_resume_versions_resume_id'), table_name='resume_versions')
    op.drop_table('resume_versions')
    
    op.drop_index(op.f('ix_resumes_created_at'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_processing_status'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_user_id'), table_name='resumes')
    op.drop_table('resumes')