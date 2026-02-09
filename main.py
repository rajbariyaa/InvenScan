import psycopg2

conn = psycopg2.connect(host="localhost", dbname = 'postgres', user = 'postgres', password = 'airm3', port = 5432)

cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS person(
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INT,
            gender CHAR);
            ''')

conn.commit()
cur.close()
conn.close()