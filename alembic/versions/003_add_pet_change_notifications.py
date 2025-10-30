"""Add pet change notifications trigger.

Revision ID: 003
Revises: 002
Create Date: 2025-10-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create trigger and function for pet change notifications."""
    # Create the notification function
    op.execute("""
        CREATE OR REPLACE FUNCTION notify_pet_changes()
        RETURNS trigger AS $$
        DECLARE
            payload json;
            record_data json;
        BEGIN
            -- Prepare the data based on operation
            IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                record_data = row_to_json(NEW);
            ELSIF TG_OP = 'DELETE' THEN
                record_data = row_to_json(OLD);
            END IF;
            
            -- Create the payload
            payload = json_build_object(
                'operation', TG_OP,
                'table', TG_TABLE_NAME,
                'timestamp', current_timestamp,
                'data', record_data
            );
            
            -- Send notification
            PERFORM pg_notify('pet_changes', payload::text);
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create the trigger
    op.execute("""
        CREATE TRIGGER pet_changes_trigger
        AFTER INSERT OR UPDATE OR DELETE
        ON pets
        FOR EACH ROW
        EXECUTE FUNCTION notify_pet_changes();
    """)


def downgrade() -> None:
    """Remove trigger and function for pet change notifications."""
    # Drop the trigger first
    op.execute("DROP TRIGGER IF EXISTS pet_changes_trigger ON pets;")
    
    # Drop the function
    op.execute("DROP FUNCTION IF EXISTS notify_pet_changes();")