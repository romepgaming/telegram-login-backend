import os
import asyncpg

async def connect_db():
    return await asyncpg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE")
    )

async def save_session(phone, session_str):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO sessions (phone, session_string)
        VALUES ($1, $2)
        ON CONFLICT (phone) DO UPDATE SET session_string = EXCLUDED.session_string;
    """, phone, session_str)
    await conn.close()

async def load_session(phone):
    conn = await connect_db()
    row = await conn.fetchrow("SELECT session_string FROM sessions WHERE phone = $1", phone)
    await conn.close()
    return row['session_string'] if row else None

async def delete_session(phone):
    conn = await connect_db()
    await conn.execute("DELETE FROM sessions WHERE phone = $1", phone)
    await conn.close()
