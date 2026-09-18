import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()


top_k = 2
def chunk_retriver(embedding : list):
    try:
        con = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        print("Connection Established To PgVector..")
        cur = con.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    else:
        sql_query = """
                SELECT 
                    id, 
                    chunk, 
                    1 - (embedding <=> %s::vector) AS similarity
                FROM rag_v1_embeddings
                ORDER BY embedding <=> %s::vector ASC
                LIMIT %s;
            """
        cur.execute(sql_query, (embedding, embedding, top_k))
        results = cur.fetchall()    
        # print(f"Top {top_k} results for query: '{query_text}'\n" + "="*50)
        # for row in results:
        #     doc_id, chunk_text, score = row
        #     print(f"[ID: {doc_id}] (Score: {score:.4f})")
        #     print(f"Content: {chunk_text}\n" + "-"*40)
        return results
    finally:
        cur.close()
        con.close()
        print("Connection Closed..")