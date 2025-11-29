# scripts/restore_content.py
import json
import glob
from pathlib import Path
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'dbname': 'ai_content_db',
    'user': 'postgres',
    'password': 'PostgreSQL_16',
    'host': 'localhost',
    'port': 5432
}

JASON_USER_ID = 'cmigirxo300002gd2cfu43tu'

def restore_content():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True  # Each statement commits immediately
    cur = conn.cursor()
    
    # Ensure Jason's user exists
    try:
        cur.execute("""
            INSERT INTO "User" (id, email, name, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (email) DO NOTHING
        """, (JASON_USER_ID, 'robinsonjason761@gmail.com', 'Jason Robinson'))
    except Exception as e:
        print(f"User creation error (may already exist): {e}")
    
    # Find all JSON files
    json_files = glob.glob('generated_content/week_*/*.json')
    
    imported = 0
    skipped = 0
    errors = 0
    
    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract metadata
            metadata = data.get('metadata', {})
            title = data.get('title', 'Untitled')
            content = data.get('content', '')
            content_html = data.get('contentHtml', '')
            
            # Check if already exists
            cur.execute('SELECT id FROM "Content" WHERE title = %s AND "userId" = %s', (title, JASON_USER_ID))
            if cur.fetchone():
                skipped += 1
                continue
            
            # Insert
            # Line 54-62, replace with:
            cur.execute("""
                INSERT INTO "Content" (id, "userId", title, content, "contentHtml", status, type, metadata, "createdAt", "updatedAt")
                VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                JASON_USER_ID,
                title,
                content,
                content_html,
                'completed',
                metadata.get('template_type', 'article'),
                json.dumps(metadata)
            ))
            imported += 1
            
        except Exception as e:
            errors += 1
            print(f"Error importing {Path(json_path).name}: {e}")
    
    cur.close()
    conn.close()
    
    print(f"\n✅ Imported: {imported}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")

if __name__ == '__main__':
    restore_content()