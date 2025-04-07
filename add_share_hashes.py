import asyncio
import os
from urllib.parse import unquote, urlparse

import aiohttp
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

FILEBROWSER_URL = os.getenv("FILEBROWSER_URL")
FILEBROWSER_USERNAME = os.getenv("FILEBROWSER_USERNAME")
FILEBROWSER_PASSWORD = os.getenv("FILEBROWSER_PASSWORD")
FILEBROWSER_UPLOAD_PATH = os.getenv("FILEBROWSER_UPLOAD_PATH", "HBNI-Audio/Recordings")

# Global dict of filebrowser items {name: full_path}
FILEBROWSER_ITEMS = {}


async def get_filebrowser_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FILEBROWSER_URL}/api/login",
            json={"username": FILEBROWSER_USERNAME, "password": FILEBROWSER_PASSWORD},
        ) as response:
            token = await response.text()
            return token.strip()


async def get_public_share_url(file_relative_path: str, token: str) -> str:
    headers = {"X-Auth": token.strip(), "accept": "*/*"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FILEBROWSER_URL}/api/share/{file_relative_path}",
            headers=headers,
            json={"path": f"/{file_relative_path}"},
        ) as response:
            if response.status != 200:
                body = await response.text()
                raise Exception(
                    f"Failed to create share link: {response.status} - {body}"
                )
            data = await response.json()
            return data["hash"]


async def list_filebrowser_items():
    global FILEBROWSER_ITEMS
    token = await get_filebrowser_token()
    headers = {"X-Auth": token, "Accept": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{FILEBROWSER_URL}/api/resources/{FILEBROWSER_UPLOAD_PATH}",
            headers=headers,
        ) as response:
            if response.status != 200:
                body = await response.text()
                raise Exception(f"Failed to list items: {response.status} - {body}")
            data = await response.json()

    items = data.get("items", [])
    FILEBROWSER_ITEMS = {
        item["name"]: item["path"].lstrip("/") for item in items if not item["isDir"]
    }

    print(f"📂 Loaded {len(FILEBROWSER_ITEMS)} files from FileBrowser.")


def extract_filename_from_download_link(download_link: str) -> str:
    path = urlparse(download_link).path
    return unquote(os.path.basename(path)).replace("&amp;", "&").replace("&Amp;", "&")


async def list_audioarchives():
    await list_filebrowser_items()
    token = await get_filebrowser_token()
    pool = await asyncpg.create_pool(**db_settings)

    async with pool.acquire() as conn:
        query = """
        SELECT * FROM audioarchives
        WHERE download_link LIKE '%play_recording%'
        ORDER BY date DESC;
        """
        rows = await conn.fetch(query)
        print(f"🎵 Found {len(rows)} rows missing share_hash:")

        for row in rows:
            download_link = row["download_link"]
            filename = extract_filename_from_download_link(download_link)
            current_hash = row["share_hash"]

            # if current_hash:
            #     print(f"✅ Already has share_hash: {filename} → {current_hash}")
            #     continue

            filebrowser_path = FILEBROWSER_ITEMS.get(filename)
            if not filebrowser_path:
                print(f"⚠️ File not found in FileBrowser: {filename}")
                continue

            try:
                share_hash = await get_public_share_url(filebrowser_path, token)
                update_query = (
                    "UPDATE audioarchives SET share_hash = $1 WHERE download_link = $2;"
                )
                await conn.execute(update_query, share_hash, download_link)
                print(f"✅ Added share_hash for: {filename} → {share_hash}")
            except Exception as e:
                print(f"❌ Failed to create share for {filename}: {str(e)}")

    await pool.close()


if __name__ == "__main__":
    asyncio.run(list_audioarchives())
