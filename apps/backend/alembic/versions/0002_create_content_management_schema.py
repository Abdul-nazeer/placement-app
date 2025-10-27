"""Create comprehensive content management schema

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table('companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('headquarters', sa.String(length=200), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('question_count', sa.Integer(), nullable=False),
        sa.Column('popularity_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=True)
    op.create_index(op.f('ix_companies_slug'), 'companies', ['slug'], unique=True)
    op.create_index('idx_companies_active_featured', 'companies', ['is_active', 'is_featured'])

    # Create categories table
    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('question_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)
    op.create_index(op.f('ix_categories_type'), 'categories', ['type'])
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'])
    op.create_index('idx_categories_type_active', 'categories', ['type', 'is_active'])
    op.create_index('idx_categories_parent_level', 'categories', ['parent_id', 'level'])

    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    op.create_index(op.f('ix_tags_slug'), 'tags', ['slug'], unique=True)
    op.create_index(op.f('ix_tags_type'), 'tags', ['type'])
    op.create_index('idx_tags_type_active', 'tags', ['type', 'is_active'])

    # Create question_collections table
    op.create_table('question_collections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=True),
        sa.Column('estimated_time', sa.Integer(), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('is_premium', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('question_count', sa.Integer(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('average_score', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_collections_name'), 'question_collections', ['name'])
    op.create_index(op.f('ix_question_collections_slug'), 'question_collections', ['slug'], unique=True)
    op.create_index(op.f('ix_question_collections_type'), 'question_collections', ['type'])
    op.create_index(op.f('ix_question_collections_company_id'), 'question_collections', ['company_id'])
    op.create_index(op.f('ix_question_collections_category_id'), 'question_collections', ['category_id'])
    op.create_index(op.f('ix_question_collections_created_by'), 'question_collections', ['created_by'])
    op.create_index('idx_question_collections_type_public', 'question_collections', ['type', 'is_public'])

    # Create enhanced questions table
    op.create_table('questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('hints', sa.JSON(), nullable=True),
        sa.Column('company_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('topic_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('skill_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('parent_question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('average_time', sa.Float(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_premium', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_type'), 'questions', ['type'])
    op.create_index(op.f('ix_questions_category'), 'questions', ['category'])
    op.create_index(op.f('ix_questions_subcategory'), 'questions', ['subcategory'])
    op.create_index(op.f('ix_questions_difficulty'), 'questions', ['difficulty'])
    op.create_index(op.f('ix_questions_status'), 'questions', ['status'])
    op.create_index(op.f('ix_questions_parent_question_id'), 'questions', ['parent_question_id'])
    op.create_index(op.f('ix_questions_created_by'), 'questions', ['created_by'])
    op.create_index(op.f('ix_questions_reviewed_by'), 'questions', ['reviewed_by'])
    
    # Create GIN indexes for arrays and full-text search
    op.create_index('idx_questions_company_tags', 'questions', ['company_tags'], postgresql_using='gin')
    op.create_index('idx_questions_topic_tags', 'questions', ['topic_tags'], postgresql_using='gin')
    op.create_index('idx_questions_skill_tags', 'questions', ['skill_tags'], postgresql_using='gin')
    op.create_index('idx_questions_search_vector', 'questions', ['search_vector'], postgresql_using='gin')
    
    # Create compound indexes for performance
    op.create_index('idx_questions_compound_filter', 'questions', ['type', 'category', 'difficulty', 'status'])
    op.create_index('idx_questions_analytics', 'questions', ['success_rate', 'average_time', 'usage_count'])

    # Create enhanced test_sessions table
    op.create_table('test_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('test_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('question_ids', postgresql.ARRAY(postgresql.UUID()), nullable=False),
        sa.Column('current_question_index', sa.Integer(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('time_per_question', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pause_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_pause_duration', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('max_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=True),
        sa.Column('correct_answers', sa.Integer(), nullable=False),
        sa.Column('incorrect_answers', sa.Integer(), nullable=False),
        sa.Column('skipped_answers', sa.Integer(), nullable=False),
        sa.Column('total_time_taken', sa.Integer(), nullable=True),
        sa.Column('allow_review', sa.Boolean(), nullable=False),
        sa.Column('show_results', sa.Boolean(), nullable=False),
        sa.Column('randomize_questions', sa.Boolean(), nullable=False),
        sa.Column('randomize_options', sa.Boolean(), nullable=False),
        sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('difficulty_levels', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('company_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('topic_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_sessions_user_id'), 'test_sessions', ['user_id'])
    op.create_index(op.f('ix_test_sessions_test_type'), 'test_sessions', ['test_type'])
    op.create_index(op.f('ix_test_sessions_status'), 'test_sessions', ['status'])
    op.create_index('idx_test_sessions_user_type', 'test_sessions', ['user_id', 'test_type'])
    op.create_index('idx_test_sessions_status_created', 'test_sessions', ['status', 'created_at'])
    op.create_index('idx_test_sessions_company_tags', 'test_sessions', ['company_tags'], postgresql_using='gin')
    op.create_index('idx_test_sessions_topic_tags', 'test_sessions', ['topic_tags'], postgresql_using='gin')

    # Create enhanced submissions table
    op.create_table('submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_type', sa.String(length=50), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=True),
        sa.Column('time_taken', sa.Integer(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('evaluation_attempts', sa.Integer(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('detailed_analysis', sa.JSON(), nullable=True),
        sa.Column('evaluated_by', sa.String(length=50), nullable=True),
        sa.Column('evaluation_time', sa.Float(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['test_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_user_id'), 'submissions', ['user_id'])
    op.create_index(op.f('ix_submissions_session_id'), 'submissions', ['session_id'])
    op.create_index(op.f('ix_submissions_question_id'), 'submissions', ['question_id'])
    op.create_index(op.f('ix_submissions_submission_type'), 'submissions', ['submission_type'])
    op.create_index(op.f('ix_submissions_status'), 'submissions', ['status'])
    op.create_index('idx_submissions_user_session', 'submissions', ['user_id', 'session_id'])
    op.create_index('idx_submissions_question_type', 'submissions', ['question_id', 'submission_type'])
    op.create_index('idx_submissions_evaluation', 'submissions', ['status', 'evaluated_at'])
    op.create_index('idx_submissions_performance', 'submissions', ['score', 'time_taken', 'is_correct'])
    op.create_index('idx_submissions_analytics', 'submissions', ['submission_type', 'is_correct', 'submitted_at'])

    # Create trigger function for updating search vector
    op.execute("""
        CREATE OR REPLACE FUNCTION update_question_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.explanation, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.company_tags, ' '), '')), 'D') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.topic_tags, ' '), '')), 'D') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.skill_tags, ' '), '')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to automatically update search vector
    op.execute("""
        CREATE TRIGGER trigger_update_question_search_vector
        BEFORE INSERT OR UPDATE ON questions
        FOR EACH ROW
        EXECUTE FUNCTION update_question_search_vector();
    """)

    # Create function to update question analytics
    op.execute("""
        CREATE OR REPLACE FUNCTION update_question_analytics()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update question usage count and analytics
            UPDATE questions 
            SET 
                usage_count = usage_count + 1,
                success_rate = CASE 
                    WHEN success_rate IS NULL THEN 
                        CASE WHEN NEW.is_correct THEN 100.0 ELSE 0.0 END
                    ELSE 
                        ((success_rate * (usage_count - 1)) + CASE WHEN NEW.is_correct THEN 100.0 ELSE 0.0 END) / usage_count
                END,
                average_time = CASE 
                    WHEN average_time IS NULL THEN NEW.time_taken
                    ELSE ((average_time * (usage_count - 1)) + NEW.time_taken) / usage_count
                END,
                updated_at = NOW()
            WHERE id = NEW.question_id;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to update question analytics on submission
    op.execute("""
        CREATE TRIGGER trigger_update_question_analytics
        AFTER INSERT ON submissions
        FOR EACH ROW
        WHEN (NEW.is_correct IS NOT NULL)
        EXECUTE FUNCTION update_question_analytics();
    """)


def downgrade() -> None:
    # Drop triggers and functions
    op.execute("DROP TRIGGER IF EXISTS trigger_update_question_analytics ON submissions;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_question_search_vector ON questions;")
    op.execute("DROP FUNCTION IF EXISTS update_question_analytics();")
    op.execute("DROP FUNCTION IF EXISTS update_question_search_vector();")
    
    # Drop tables in reverse order
    op.drop_table('submissions')
    op.drop_table('test_sessions')
    op.drop_table('questions')
    op.drop_table('question_collections')
    op.drop_table('tags')
    op.drop_table('categories')
    op.drop_table('companies')