import psycopg2


def create_table():
    try:
        con = psycopg2.connect(host="localhost", dbname="TASK", user="postgres", password="pgsql", port=5432)
        print("Connection Established To PgVector..")
        cur = con.cursor()
        
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    else:
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id SERIAL PRIMARY KEY,
                chunk TEXT,
                embedding VECTOR(1536)
            );
        """)
        con.commit()
        print("Table Created Successfully..")
    finally:
        if cur:
            cur.close()
        if con:
            con.close()
        print("Connection Closed..")

def insert_inpgvector(data : dict):
    try:
        con = psycopg2.connect(host="localhost", dbname="TASK", user="postgres", password="pgsql", port=5432)
        print("Connection Established To PgVector..")
        cur = con.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    else:
        for item in data:
            chunk_text = item["content"]
            vector_data = item["embedding"]
            
            cur.execute("""
                INSERT INTO document_embeddings (chunk, embedding)
                VALUES (%s, %s);
            """, (chunk_text, vector_data))
        con.commit()
        print("All Chunk With Embedding Inserted & Commited To DB..")
    finally:
        if cur:
            cur.close()
        if con:
            con.close()
        print("Connection Closed..")
