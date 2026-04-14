#!/usr/bin/env python3
"""
Migration script to add 'resolved' column to notifications table
Run this to add support for tracking resolved/settled equipment damage issues
"""

from database import SessionLocal, engine
from models import Notification
from sqlalchemy import Column, Boolean, inspect

def add_resolved_column():
    """Add resolved column to notifications table if it doesn't exist"""
    
    # Check if column exists
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('notifications')]
    
    if 'resolved' in columns:
        print("✓ 'resolved' column already exists in notifications table")
        return True
    
    try:
        # Add the column
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE notifications ADD COLUMN resolved BOOLEAN DEFAULT 0"
            )
        print("✓ Successfully added 'resolved' column to notifications table")
        
        # Verify the column was added
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('notifications')]
        if 'resolved' in columns:
            print("✓ Verification successful: 'resolved' column is now in the table")
            return True
        else:
            print("✗ Verification failed: 'resolved' column not found after migration")
            return False
            
    except Exception as e:
        print(f"✗ Error adding 'resolved' column: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting migration: add_resolved_to_notifications...")
    success = add_resolved_column()
    if success:
        print("\n✨ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
