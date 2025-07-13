import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

# Danh sách các kênh Dailymotion đã cho (dạng username)
CHANNELS = []
import difflib
def search_global_dailymotion_videos(query: str, limit: int = 100):
    results = []
    url = f"https://api.dailymotion.com/videos?search={query}&fields=title,url&limit={limit}&sort=relevance"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for item in data.get("list", []):
            results.append(f"{item['title']}\n{item['url']}")
    return results

# Hàm tìm kiếm video theo tiêu đề
def search_dailymotion_video(title: str):
    results = []
    fuzzy_results = []

    for channel in CHANNELS:
        url = f"https://api.dailymotion.com/user/{channel}/videos?fields=title,url&limit=100"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("list", []):
                video_title = item["title"]
                video_url = item["url"]
                lower_title = video_title.lower()
                lower_query = title.lower()

                if lower_query in lower_title:
                    results.append(video_url)
                else:
                    similarity = difflib.SequenceMatcher(None, lower_query, lower_title).ratio()
                    if similarity > 0.3:
                        fuzzy_results.append((similarity, video_url))

    if results:
        return results
    else:
        # Sắp xếp fuzzy_results theo điểm giống nhau
        fuzzy_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in fuzzy_results]


# Gửi tin nhắn khi bot khởi động
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there! Please send the video title you want to search.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /find video title to search.")
    await update.message.reply_text("Use /search video title to global search.")

async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a video title. Usage: /find Spoiled By My Billionaire")
        return

    query = " ".join(context.args)
    #await update.message.reply_text(f"Searching for videos with the title: \"{query}\"...")
    results = search_dailymotion_video(query)

    if results:
        for link in results[:2]:  # Giới hạn gửi 2 kết quả
            await update.message.reply_text(link)
    else:
        await update.message.reply_text("No videos found matching your search.")
        
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a video title. Usage: /search Spoiled By My Billionaire")
        return

    query = " ".join(context.args)
    #await update.message.reply_text(f"Searching for videos with the title: \"{query}\"...")
    results = search_global_dailymotion_videos(query)

    if results:
        for link in results[:2]:  # Giới hạn gửi 2 kết quả
            await update.message.reply_text(link)
    else:
        await update.message.reply_text("No videos found matching your search.")
# Handle search command
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # If the user sends "/help"
    if text.lower() == "/help":
        await update.message.reply_text("Send the command: /find video title to search for videos.")
    
    # If the message starts with "/find"
    elif text.startswith("/find"):
        query = text[len("/find "):]
        await update.message.reply_text(f"Searching for the title: \"{query}\"...")
        results = search_dailymotion_video(query)
        
        # If results are found
        if results:
            for link in results:
                await update.message.reply_text(link)
        else:
            await update.message.reply_text("No videos found matching your search.")

# Main bot
async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("⚠️ BOT_TOKEN is not set in .env!")
        return
    app = ApplicationBuilder().token(os.environ.get("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("find", find_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    await app.run_polling()
import asyncio
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
