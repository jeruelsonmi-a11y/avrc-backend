"""
Migration script to add pit_number column to equipment table if it doesn't exist
"""
import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'avrc_db'
}

def add_pit_number_column():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Check if column exists
        check_column_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'equipment' 
            AND COLUMN_NAME = 'pit_number'
        """
        
        cursor.execute(check_column_query)
        result = cursor.fetchone()
        
        if result:
            print("✓ Column 'pit_number' already exists in equipment table")
        else:
            # Add the column
            print("Adding 'pit_number' column to equipment table...")
            alter_table_query = """
                ALTER TABLE equipment 
                ADD COLUMN pit_number VARCHAR(100) 
                AFTER item_number
            """
            cursor.execute(alter_table_query)
            connection.commit()
            print("✓ Successfully added 'pit_number' column to equipment table")
        
        cursor.close()
        connection.close()
        
    except Error as err:
        if err.errno == 2003:
            print(f"✗ Cannot connect to MySQL Server: {err}")
        else:
            print(f"✗ Error: {err}")

if __name__ == "__main__":
    add_pit_number_column()
