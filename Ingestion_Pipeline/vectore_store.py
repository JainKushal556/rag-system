import psycopg2
from dotenv import load_dotenv
load_dotenv()
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
        sslmode=os.getenv("DB_SSLMODE", "prefer")
    )

def create_table():
    cur = None
    con = None
    try:
        con = get_db_connection()
        print("Connection Established To PgVector..")
        cur = con.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    else:
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS rag_v1_embeddings (
                id SERIAL PRIMARY KEY,
                chunk TEXT,
                embedding VECTOR(1536)
            );
            CREATE TABLE IF NOT EXISTS uploaded_documents (
                id SERIAL PRIMARY KEY,
                filename TEXT UNIQUE NOT NULL,
                filesize_bytes BIGINT NOT NULL,
                uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        con.commit()
        print("Tables Created Successfully (rag_v1_embeddings & uploaded_documents)..")
    finally:
        if cur:
            cur.close()
        if con:
            con.close()
        print("Connection Closed..")

def record_uploaded_document(filename: str, filesize: int):
    cur = None
    con = None
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO uploaded_documents (filename, filesize_bytes, uploaded_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (filename) 
            DO UPDATE SET filesize_bytes = EXCLUDED.filesize_bytes, uploaded_at = CURRENT_TIMESTAMP;
        """, (filename, filesize))
        con.commit()
    except psycopg2.Error as e:
        print(f"Error recording document metadata: {e}")
    finally:
        if cur: cur.close()
        if con: con.close()

def get_uploaded_documents():
    cur = None
    con = None
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("""
            SELECT filename, filesize_bytes, uploaded_at
            FROM uploaded_documents
            ORDER BY uploaded_at DESC;
        """)
        return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching uploaded documents: {e}")
        return []
    finally:
        if cur: cur.close()
        if con: con.close()

def insert_inpgvector(data : dict):
    cur = None
    con = None
    try:
        con = get_db_connection()
        print("Connection Established To PgVector..")
        cur = con.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    else:
        for item in data:
            chunk_text = item["content"]
            vector_data = item["embedding"]
            
            cur.execute("""
                INSERT INTO rag_v1_embeddings (chunk, embedding)
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

