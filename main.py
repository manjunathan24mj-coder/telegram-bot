import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# ============================================================
# BOT CONFIG
# ============================================================
TOKEN = "8677546019:AAFWKxg0BBmv3UQ9W8443tX9kYSYy0c549E"
CHANNEL = "@niftypulse2411"

ADMIN_ID = 1797446047    # Only admin can use bot


# ============================================================
# STORAGE
# ============================================================
weekly_updates = {
    1: {"photo": None, "text": None, "url": None},
    2: {"photo": None, "text": None, "url": None},
    3: {"photo": None, "text": None, "url": None},
    4: {"photo": None, "text": None, "url": None},
    5: {"photo": None, "text": None, "url": None},
}

user_state = {}   # Tracks admin operations


# ============================================================
# ADMIN CHECK
# ============================================================
def is_admin(user_id: int):
    return user_id == ADMIN_ID


# ============================================================
# START COMMAND
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Weekly Updates", callback_data="weekly")]
    ]

    await update.message.reply_text(
        "🤖 Welcome to Auto Posting Bot!\n\n"
        "Manage weekly auto-post updates easily.\n"
        "Choose an option below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# WEEKLY MENU
# ============================================================
async def weekly(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📝 Post 1", callback_data="edit_1")],
        [InlineKeyboardButton("📝 Post 2", callback_data="edit_2")],
        [InlineKeyboardButton("📝 Post 3", callback_data="edit_3")],
        [InlineKeyboardButton("📝 Post 4", callback_data="edit_4")],
        [InlineKeyboardButton("📝 Post 5", callback_data="edit_5")],
        [InlineKeyboardButton("⬅️ Back", callback_data="start_menu")]
    ]

    await query.edit_message_text(
        "Select a post to update 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# POST EDIT MENU
# ============================================================
async def edit_post(update, context):
    query = update.callback_query
    post_id = int(query.data.split("_")[1])

    context.user_data["post_id"] = post_id

    keyboard = [
        [InlineKeyboardButton("🖼 Upload Photo", callback_data="add_photo")],
        [InlineKeyboardButton("✏️ Add Text", callback_data="add_text")],
        [InlineKeyboardButton("🔗 Add URL", callback_data="add_url")],
        [InlineKeyboardButton("➡ Next Post", callback_data=f"edit_{post_id+1}" if post_id < 5 else "weekly")],
        [InlineKeyboardButton("⬅ Back", callback_data="weekly")],
    ]

    await query.edit_message_text(
        f"Editing Weekly Post {post_id}\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# BUTTON HANDLER
# ============================================================
async def button_handler(update, context):
    query = update.callback_query
    uid = query.from_user.id

    if not is_admin(uid):
        await query.answer("Not allowed!", show_alert=True)
        return

    post_id = context.user_data.get("post_id")

    if query.data == "add_photo":
        user_state[uid] = "photo"
        await query.edit_message_text("📸 Send the photo…")

    elif query.data == "add_text":
        user_state[uid] = "text"
        await query.edit_message_text("✏️ Send the text…")

    elif query.data == "add_url":
        user_state[uid] = "url"
        await query.edit_message_text("🔗 Send the URL…")


# ============================================================
# SAVE USER INPUT
# ============================================================
async def save_input(update, context):
    uid = update.message.from_user.id

    if uid not in user_state:
        return

    post_id = context.user_data.get("post_id")
    mode = user_state[uid]

    if mode == "photo" and update.message.photo:
        weekly_updates[post_id]["photo"] = update.message.photo[-1].file_id
        await update.message.reply_text("✅ Photo saved!")

    elif mode == "text":
        weekly_updates[post_id]["text"] = update.message.text
        await update.message.reply_text("✅ Text saved!")

    elif mode == "url":
        weekly_updates[post_id]["url"] = update.message.text
        await update.message.reply_text("✅ URL saved!")

    del user_state[uid]


# ============================================================
# AUTO POSTING FUNCTION
# ============================================================
async def auto_post(context):
    post_num = context.job.data
    data = weekly_updates[post_num]

    caption = ""

    if data["text"]:
        caption += data["text"] + "\n"

    if data["url"]:
        caption += "\n🔗 " + data["url"]

    if data["photo"]:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=data["photo"],
            caption=caption if caption else None
        )
    else:
        await context.bot.send_message(
            chat_id=CHANNEL,
            text=caption if caption else f"Post {post_num}"
        )


# ============================================================
# SHOW TIME COMMAND
# ============================================================
async def show_times(update, context):
    await update.message.reply_text(
        "🕒 Fixed Posting Times:\n\n"
        "1️⃣ 8:00 AM\n"
        "2️⃣ 10:00 AM\n"
        "3️⃣ 12:00 PM\n"
        "4️⃣ 2:00 PM\n"
        "5️⃣ 8:00 PM"
    )


# ============================================================
# MAIN APPLICATION
# ============================================================
def main():
    app = Application.builder().token(TOKEN).build()

    jq = app.job_queue

    # Scheduled auto post times
    jq.run_daily(auto_post, time=datetime.time(8, 0), data=1)
    jq.run_daily(auto_post, time=datetime.time(10, 0), data=2)
    jq.run_daily(auto_post, time=datetime.time(12, 0), data=3)
    jq.run_daily(auto_post, time=datetime.time(14, 0), data=4)
    jq.run_daily(auto_post, time=datetime.time(20, 0), data=5)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show_times", show_times))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(weekly, pattern="weekly"))
    app.add_handler(CallbackQueryHandler(edit_post, pattern="edit_"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="add_"))

    # Messages
    app.add_handler(MessageHandler(filters.ALL, save_input))

    print("🚀 Bot Running on Render…")
    app.run_polling()


if __name__ == "__main__":
    main()
