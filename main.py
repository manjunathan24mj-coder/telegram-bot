import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===================== CONFIG =====================
TOKEN = os.getenv("8677546019:AAEyhPOBvbHf5zvWgAk9fngnRL86GrukwRk")
CHANNEL = os.getenv("CHANNEL", "@niftypulse2411")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ===================== STORAGE =====================
weekly_updates = {
    i: {"photo": None, "text": None, "url": None}
    for i in range(1, 6)
}

user_state = {}

# ===================== HELPERS =====================
def is_admin(user_id: int):
    return user_id == ADMIN_ID


# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Weekly Updates", callback_data="weekly")]
    ]

    await update.message.reply_text(
        "🤖 Auto Posting Bot\nSelect option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ===================== WEEKLY MENU =====================
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(f"📝 Post {i}", callback_data=f"edit_{i}")]
        for i in range(1, 6)
    ]
    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="start")])

    await query.edit_message_text(
        "Select post:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ===================== EDIT MENU =====================
async def edit_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    post_id = int(query.data.split("_")[1])
    context.user_data["post_id"] = post_id

    keyboard = [
        [InlineKeyboardButton("🖼 Photo", callback_data="add_photo")],
        [InlineKeyboardButton("✏ Text", callback_data="add_text")],
        [InlineKeyboardButton("🔗 URL", callback_data="add_url")],
        [InlineKeyboardButton("⬅ Back", callback_data="weekly")],
    ]

    await query.edit_message_text(
        f"Editing Post {post_id}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ===================== BUTTON HANDLER =====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if not is_admin(uid):
        await query.answer("Not allowed", show_alert=True)
        return

    if "post_id" not in context.user_data:
        await query.edit_message_text("⚠ Select post first")
        return

    if query.data == "add_photo":
        user_state[uid] = "photo"
        await query.edit_message_text("📸 Send photo")

    elif query.data == "add_text":
        user_state[uid] = "text"
        await query.edit_message_text("✏ Send text")

    elif query.data == "add_url":
        user_state[uid] = "url"
        await query.edit_message_text("🔗 Send URL")


# ===================== SAVE INPUT =====================
async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not is_admin(uid):
        return

    if uid not in user_state:
        return

    if "post_id" not in context.user_data:
        return

    post_id = context.user_data["post_id"]
    mode = user_state[uid]

    text = update.message.text

    if mode == "photo" and update.message.photo:
        weekly_updates[post_id]["photo"] = update.message.photo[-1].file_id
        await update.message.reply_text("✅ Photo saved")

    elif mode == "text" and text:
        weekly_updates[post_id]["text"] = text
        await update.message.reply_text("✅ Text saved")

    elif mode == "url" and text:
        weekly_updates[post_id]["url"] = text
        await update.message.reply_text("✅ URL saved")

    user_state.pop(uid, None)


# ===================== AUTO POST =====================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    post_num = context.job.data
    data = weekly_updates.get(post_num)

    if not data:
        return

    caption = ""
    if data["text"]:
        caption += data["text"] + "\n"
    if data["url"]:
        caption += "\n🔗 " + data["url"]

    if data["photo"]:
        await context.bot.send_photo(
            chat_id=CHANNEL,
            photo=data["photo"],
            caption=caption or None,
        )
    else:
        await context.bot.send_message(
            chat_id=CHANNEL,
            text=caption or f"Post {post_num}",
        )


# ===================== SHOW TIME =====================
async def show_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕒 Schedule:\n"
        "1️⃣ 8 AM\n2️⃣ 10 AM\n3️⃣ 12 PM\n4️⃣ 2 PM\n5️⃣ 8 PM"
    )


# ===================== MAIN =====================
def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN missing")

    app = Application.builder().token(TOKEN).build()

    job = app.job_queue

    job.run_daily(auto_post, time=datetime.time(8, 0), data=1)
    job.run_daily(auto_post, time=datetime.time(10, 0), data=2)
    job.run_daily(auto_post, time=datetime.time(12, 0), data=3)
    job.run_daily(auto_post, time=datetime.time(14, 0), data=4)
    job.run_daily(auto_post, time=datetime.time(20, 0), data=5)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show_times", show_times))

    app.add_handler(CallbackQueryHandler(weekly, pattern="weekly"))
    app.add_handler(CallbackQueryHandler(edit_post, pattern="edit_"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="add_"))

    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, save_input))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
