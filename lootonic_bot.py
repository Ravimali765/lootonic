import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive
import os
import time
from telegram import Bot

keep_alive()

# ===== CONFIG =====
API_ID = int(os.getenv("API_ID", 28039031))
API_HASH = os.getenv("API_HASH", "fa809cd93f897a41fddc91df5cac9480"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "8346429967:AAHuuBZmYf7Yd9twpmbIpRH2odwp__7uLXo")
USER_CHAT_ID = int(os.getenv("USER_CHAT_ID", 123456789))  # tumhara Telegram ID jaha OTP milega

# Source channels
SOURCE_CHANNELS = ["@Classickweb", "@check00221"]
TARGET_CHANNEL = "@lootonic"
CONVERTER_BOT = "@lootonic_bot"
POST_INTERVAL = 60  # seconds

# ===== TELEGRAM CLIENT =====
client = TelegramClient(StringSession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ===== TELEGRAM BOT FOR OTP =====
bot = Bot(token=BOT_TOKEN)

def request_otp():
    """Send message to user and wait for OTP reply"""
    bot.send_message(USER_CHAT_ID, "Please enter OTP for login:")
    otp = None
    print("⏳ Waiting for OTP from Telegram user...")
    while otp is None:
        try:
            updates = bot.get_updates(timeout=5)
            for update in updates:
                if update.message and str(update.message.chat.id) == str(USER_CHAT_ID):
                    otp = update.message.text.strip()
                    bot.send_message(USER_CHAT_ID, f"✅ OTP received: {otp}")
                    return otp
        except Exception:
            time.sleep(2)

# ===== LINK CONVERSION =====
async def convert_link(original_url):
    try:
        await client.send_message(CONVERTER_BOT, original_url)
        await asyncio.sleep(5)
        async for message in client.iter_messages(CONVERTER_BOT, limit=1):
            return message.text.strip()
    except Exception as e:
        print(f"❌ Link conversion error: {e}")
        return original_url

# ===== URL EXTRACT =====
def extract_urls(text):
    return re.findall(r"(https?://[^\s]+)", text or "")

# ===== SAFE POSTING =====
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

# ===== HANDLER =====
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    msg = event.message
    urls = extract_urls(msg.text)
    if not urls:
        return

    print(f"📩 New message from @{getattr(event.chat, 'username', 'Unknown')}")

    converted_urls = []
    for url in urls:
        converted = await convert_link(url)
        converted_urls.append(converted)

    caption = msg.text
    for original, conv in zip(urls, converted_urls):
        caption = caption.replace(original, conv)

    await post_to_channel(msg, caption)
    await asyncio.sleep(POST_INTERVAL)

# ===== RUN CLIENT =====
print("🚀 Lootonic Auto-Poster Running...")
client.run_until_disconnected()

