from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# Danh sách các kênh Dailymotion đã cho (dạng username)
CHANNELS = [
    "redmedia8",
    "shortdramamini",
    "thedramazone"
]

# Hàm tìm kiếm video theo tiêu đề
def search_dailymotion_video(title: str):
    results = []
    for channel in CHANNELS:
        url = f"https://api.dailymotion.com/user/{channel}/videos?fields=title,url"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("list", []):
                if title.lower() in item["title"].lower():
                    results.append(item["url"])
    return results

# Gửi tin nhắn khi bot khởi động
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào bạn! Hãy gửi tiêu đề video bạn muốn tìm.")

# Xử lý tin nhắn văn bản
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"Đang tìm kiếm video có tiêu đề: \"{query}\"...")
    results = search_dailymotion_video(query)
    if results:
        for link in results:
            await update.message.reply_text(link)
    else:
        await update.message.reply_text("Không tìm thấy video phù hợp.")

# Main bot
async def main():
    app = ApplicationBuilder().token(os.environ.get("7925727449:AAHNUFeLe7I3gylbGBBdlyoJmPxZa7fvmO8")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot đang chạy...")
    await app.run_polling()
