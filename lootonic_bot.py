import re
import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ===== CONFIG =====
API_ID = int(os.getenv("API_ID", "28039031"))
API_HASH = os.getenv("API_HASH", "fa809cd93f897a41fddc91df5cac9480")
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render me set karo, warna local test ke liye None

SOURCE_CHANNELS = [
    "@Classickweb",
    "@check00221",
    "@TrickXpert",
    "@realearnkaro",
    "@magixdeals",
    "@dealspoint"
]

TARGET_CHANNEL = "@lootonic"
CONVERTER_BOT = "@lootonic_bot"
POST_INTERVAL = 60  # seconds between posts

# ===== TELEGRAM CLIENT =====
client = TelegramClient(StringSession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ===== FUNCTIONS =====
async def convert_link(original_url):
    try:
        await client.send_message(CONVERTER_BOT, original_url)
        await asyncio.sleep(5)  # wait for bot reply
        async for message in client.iter_messages(CONVERTER_BOT, limit=1):
            return message.text.strip()
    except Exception as e:
        print(f"❌ Link conversion error: {e}")
        return original_url

def extract_urls(text):
    return re.findall(r'(https?://[^\s]+)', text or "")

async def post_to_channel(msg, caption):
    try:
        if msg.photo:
            await client.send_file(TARGET_CHANNEL, msg.photo, caption=caption)
        elif msg.document:
            await client.send_file(TARGET_CHANNEL, msg.document, caption=caption)
        else:
            await client.send_message(TARGET_CHANNEL, caption)
        print(f"✅ Posted message to {TARGET_CHANNEL}")
    except Exception as e:
        print(f"❌ Error posting: {e}")

# ===== EVENT HANDLER =====
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    msg = event.message
    urls = extract_urls(msg.text)
    if not urls:
        return

    print(f"📩 New message from @{getattr(event.chat, 'username', 'Unknown')}")

    converted_urls = []
    for url in urls:
        converted_urls.append(await convert_link(url))

    caption = msg.text
    for original, conv in zip(urls, converted_urls):
        caption = caption.replace(original, conv)

    await post_to_channel(msg, caption)
    await asyncio.sleep(POST_INTERVAL)

# ===== RUN BOT =====
print("🚀 Lootonic Auto-Poster Running...")
client.run_until_disconnected()

