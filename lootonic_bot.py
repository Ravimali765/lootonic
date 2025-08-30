import re
import asyncio
from telethon import TelegramClient, events

# ===== CONFIG =====
API_ID = 28039031
API_HASH = "fa809cd93f897a41fddc91df5cac9480"

# Source channels se messages lene ke liye
SOURCE_CHANNELS = [
    "@Classickweb",
    "@check00221"
]

TARGET_CHANNEL = "@lootonic"
CONVERTER_BOT = "@lootonic_bot"
POST_INTERVAL = 60  # seconds between posts

# ===== TELEGRAM CLIENT =====
client = TelegramClient("lootonic_user", API_ID, API_HASH)


# Link conversion via @ekconverter1bot
async def convert_link(original_url):
    try:
        await client.send_message(CONVERTER_BOT, original_url)
        await asyncio.sleep(5)  # wait for bot reply

        async for message in client.iter_messages(CONVERTER_BOT, limit=1):
            converted_link = message.text.strip()
            return converted_link
    except Exception as e:
        print(f"❌ Link conversion error: {e}")
        return original_url


# Detect URLs in message
def extract_urls(text):
    return re.findall(r'(https?://[^\s]+)', text or "")


# Safe posting (fix for photo/text/webpage issue)
async def post_to_channel(msg, caption):
    try:
        if msg.photo:  # agar image hai
            await client.send_file(TARGET_CHANNEL, msg.photo, caption=caption)
        elif msg.document:  # agar koi file hai
            await client.send_file(TARGET_CHANNEL, msg.document, caption=caption)
        else:  # sirf text / webpage
            await client.send_message(TARGET_CHANNEL, caption)
        print(f"✅ Posted message to {TARGET_CHANNEL}")
    except Exception as e:
        print(f"❌ Error posting: {e}")


# Handle new messages from source channels
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    msg = event.message
    urls = extract_urls(msg.text)
    if not urls:
        return

    print(f"📩 New message from @{getattr(event.chat, 'username', 'Unknown')}")

    # Convert each URL via bot
    converted_urls = []
    for url in urls:
        converted = await convert_link(url)
        converted_urls.append(converted)

    # Prepare caption
    caption = msg.text
    for original, conv in zip(urls, converted_urls):
        caption = caption.replace(original, conv)

    # Post message
    await post_to_channel(msg, caption)

    # Wait interval
    await asyncio.sleep(POST_INTERVAL)


# ===== RUN CLIENT =====
async def main():
    await client.start()  # user login first time
    print("🚀 Lootonic Auto-Poster Running...")
    await client.run_until_disconnected()


asyncio.run(main())
