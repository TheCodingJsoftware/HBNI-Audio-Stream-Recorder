import os
import shutil
from urllib.parse import quote

import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Database settings
db_settings = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT", 5434)),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


async def insert_data_to_db(
    pool, file_name, download_url, date, description, length, host
):
    async with pool.acquire() as conn:
        query = """
        INSERT INTO audioarchives (filename, date, description, download_link, length, host, visit_count, latest_visit)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
        """
        await conn.execute(
            query, file_name, date, description, download_url, length, host, 0, None
        )


async def upload(
    file_name: str,
    file_path: str,
    host: str,
    description: str,
    date: str,
    length: float,
):
    pool = await asyncpg.create_pool(**db_settings)
    file_path = (
        file_path.replace("&amp;", "&")
        .replace("&Amp;", "&")
        .replace("&", "and")
        .replace("/", " or ")
    )
    shutil.copy2(
        file_path, os.getenv("STATIC_RECORDINGS_PATH", "/app/static/Recordings")
    )
    download_url = f"https://broadcasting.hbni.net/play_recording/{quote(file_name)}"
    await insert_data_to_db(
        pool, file_name, download_url, date, description, length, host
    )
    await pool.close()
