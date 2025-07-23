import os
import asyncpg

# Fungsi koneksi ke PostgreSQL
async def connect_db():
    return await asyncpg.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE")
    )

# 🔧 Inisialisasi tabel jika belum ada
async def init_db():
    conn = await connect_db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            phone TEXT PRIMARY KEY,
            session_string TEXT NOT NULL
        );
    """)
    await conn.close()

# Simpan atau update session
async def save_session(phone, session_str):
    conn = await connect_db()
    await conn.execute("""
        INSERT INTO sessions (phone, session_string)
        VALUES ($1, $2)
        ON CONFLICT (phone) DO UPDATE SET session_string = EXCLUDED.session_string;
    """, phone, session_str)
    await conn.close()

# Ambil session dari DB
async def load_session(phone):
    conn = await connect_db()
    row = await conn.fetchrow("SELECT session_string FROM sessions WHERE phone = $1", phone)
    await conn.close()
    return row['session_string'] if row else None

# Hapus session berdasarkan nomor
async def delete_session(phone):
    conn = await connect_db()
    await conn.execute("DELETE FROM sessions WHERE phone = $1", phone)
    await conn.close()
