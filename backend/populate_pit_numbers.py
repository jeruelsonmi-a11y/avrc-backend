"""
Script to populate pit_number field with random 5-digit numbers for all equipment
"""
import mysql.connector
from mysql.connector import Error
import random

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'avrc_db'
}

def generate_random_pit_number():
    """Generate a random 5-digit PIT number (10000-99999)"""
    return str(random.randint(10000, 99999))

def populate_pit_numbers():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Get all equipment that doesn't have a pit_number yet
        select_query = """
            SELECT id, name, item_number 
            FROM equipment 
            WHERE pit_number IS NULL OR pit_number = ''
        """
        
        cursor.execute(select_query)
        equipment_list = cursor.fetchall()
        
        if not equipment_list:
            print("✓ All equipment already have PIT numbers assigned!")
            cursor.close()
            connection.close()
            return
        
        print(f"Found {len(equipment_list)} equipment without PIT numbers. Assigning random PIT numbers...")
        
        # Keep track of assigned PIT numbers to avoid duplicates
        used_pit_numbers = set()
        
        for equipment_id, equipment_name, item_number in equipment_list:
            # Generate unique PIT number
            pit_number = generate_random_pit_number()
            while pit_number in used_pit_numbers:
                pit_number = generate_random_pit_number()
            
            used_pit_numbers.add(pit_number)
            
            # Update equipment with new PIT number
            update_query = "UPDATE equipment SET pit_number = %s WHERE id = %s"
            cursor.execute(update_query, (pit_number, equipment_id))
            print(f"  ✓ {equipment_name} (ID: {equipment_id}, Item #: {item_number}) → PIT No. {pit_number}")
        
        connection.commit()
        print(f"\n✓ Successfully assigned PIT numbers to {len(equipment_list)} equipment!")
        
        cursor.close()
        connection.close()
        
    except Error as err:
        if err.errno == 2003:
            print(f"✗ Cannot connect to MySQL Server: {err}")
        else:
            print(f"✗ Error: {err}")
    except Exception as err:
        print(f"✗ Unexpected error: {err}")

if __name__ == "__main__":
    populate_pit_numbers()
