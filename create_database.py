import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        ID INTEGER PRIMARY KEY
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS WantToVisit (
        ID INTEGER,
        Place TEXT,
        FOREIGN KEY (ID) REFERENCES Users (ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Visited (
        ID INTEGER,
        Place TEXT,
        FOREIGN KEY (ID) REFERENCES Users (ID)
    )
''')

conn.commit()

conn.close()
