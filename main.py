import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = "8677546019:AAFWKxg0BBmv3UQ9W8443tX9kYSYy0c549E"
CHANNEL = "@niftypulse2411"

logging.basicConfig(level=logging.INFO)


def convert_time(time_str):
    """Convert 24h → 12h with AM/PM."""
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%I:%M %p")
    except:
        return "❌ Invalid time format. Use HH:MM (example: 18:30)"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot is running 24/7 on Render!\n"
        "Use /show_times 18:30 → to convert time."
    )


async def show_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Send like: /show_times 18:30")
        return

    time_24 = context.args[0]
    result = convert_time(time_24)
    await update.message.reply_text(f"⏱ Converted Time: {result}")


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Posting feature will be added soon.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show_times", show_times))
    app.add_handler(CommandHandler("post", post))

    print("Bot running on Render...")
    app.run_poling()


if __name__ == "__main__":
    main()
