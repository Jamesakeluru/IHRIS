import pymysql

# Connect to the database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='James&akan2success',
    database='yutees_ihris_db'
)

cursor = connection.cursor()

# Insert sample inventory items
insert_items = """
INSERT INTO inventory (item_name, item_type, serial_number) VALUES
('Security Shirt', 'Uniform', 'SHIRT001'),
('Security Trousers', 'Uniform', 'TROUS001'),
('Radio Set', 'Radio', 'RADIO001'),
('Security Boots', 'Boots', 'BOOTS001'),
('Security Shirt', 'Uniform', 'SHIRT002'),
('Security Trousers', 'Uniform', 'TROUS002'),
('Radio Set', 'Radio', 'RADIO002'),
('Security Boots', 'Boots', 'BOOTS002');
"""

try:
    cursor.execute(insert_items)
    connection.commit()
    print("Sample inventory items inserted successfully.")
except pymysql.Error as e:
    print(f"Error inserting data: {e}")
finally:
    cursor.close()
    connection.close()