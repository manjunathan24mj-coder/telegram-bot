import os
import json
from datetime import time
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@niftypulse2411")

TIMEZONE = ZoneInfo("Asia/Kolkata")

ADMIN_USERNAMES = {
    "Nifty_Pulse_01",
    "Finz8435"
}

DATA_FILE = "weekly_posts.json"

# =========================================================
# DAILY 5 POST TIMES (INDIA TIME)
# =========================================================

POST_TIMES = {
    1: time(8, 0, tzinfo=TIMEZONE),    # 8 AM
    2: time(10, 0, tzinfo=TIMEZONE),   # 10 AM
    3: time(12, 0, tzinfo=TIMEZONE),   # 12 PM
    4: time(14, 0, tzinfo=TIMEZONE),   # 2 PM
    5: time(20, 0, tzinfo=TIMEZONE),   # 8 PM
}

# =========================================================
# DATA FUNCTIONS
# =========================================================

def default_data():
    return {
        str(i): {
            "photo": None,
            "text": "",
            "url": ""
        }
        for i in range(1, 6)
    }


def load_data():

    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception:
        return default_data()

    return data


def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(update: Update):

    user = update.effective_user

    return bool(
        user and user.username in ADMIN_USERNAMES
    )

# =========================================================
# MENUS
# =========================================================

def main_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📅 Weekly Update Post",
                callback_data="weekly"
            )
        ],

        [
            InlineKeyboardButton(
                "🖼 Generate Daily Result Image",
                callback_data="daily_image"
            )
        ]

    ])


def posts_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "Post 1 - 8 AM",
                callback_data="post_1"
            )
        ],

        [
            InlineKeyboardButton(
                "Post 2 - 10 AM",
                callback_data="post_2"
            )
        ],

        [
            InlineKeyboardButton(
                "Post 3 - 12 PM",
                callback_data="post_3"
            )
        ],

        [
            InlineKeyboardButton(
                "Post 4 - 2 PM",
                callback_data="post_4"
            )
        ],

        [
            InlineKeyboardButton(
                "Post 5 - 8 PM",
                callback_data="post_5"
            )
        ],

        [
            InlineKeyboardButton(
                "➕ Add New Post",
                callback_data="add_new_post"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_main"
            )
        ]

    ])


def post_edit_menu(post_no):

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📷 Upload Photo",
                callback_data=f"upload_photo_{post_no}"
            )
        ],

        [
            InlineKeyboardButton(
                "📝 Upload Text",
                callback_data=f"upload_text_{post_no}"
            )
        ],

        [
            InlineKeyboardButton(
                "🔗 Upload URL",
                callback_data=f"upload_url_{post_no}"
            )
        ],

        [
            InlineKeyboardButton(
                "👁 Preview Post",
                callback_data=f"preview_post_{post_no}"
            )
        ],

        [
            InlineKeyboardButton(
                "🗑 Clear Post",
                callback_data=f"clear_post_{post_no}"
            )
        ],

        [
            InlineKeyboardButton(
                "➡️ Next Post",
                callback_data=f"next_post_{post_no}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="weekly"
            )
        ]

    ])


def daily_result_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_main"
            )
        ]

    ])

# =========================================================
# FONT
# =========================================================

def load_font(size, bold=False):

    font_paths = [

        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        "arialbd.ttf" if bold else "arial.ttf"
    ]

    for font_path in font_paths:

        try:
            return ImageFont.truetype(font_path, size)

        except Exception:
            pass

    return ImageFont.load_default()

# =========================================================
# RESULT IMAGE GENERATOR
# =========================================================

def create_result_image(
    trade_name,
    date_text,
    qty_text,
    avg_text,
    profit_text,
    ltp_text,
    percent_text
):

    output_path = "daily_result.png"

    img = Image.new(
        "RGB",
        (1200, 650),
        "#ffffff"
    )

    draw = ImageDraw.Draw(img)

    green = "#73a88d"
    grey = "#9c9c9c"
    line = "#ececec"

    font_trade = load_font(44, True)
    font_medium = load_font(34, True)
    font_small = load_font(28, True)
    font_profit = load_font(44, True)
    font_stamp = load_font(90, True)

    # CARD
    draw.rounded_rectangle(
        (25, 25, 1175, 625),
        radius=12,
        fill="white",
        outline="#efefef",
        width=3
    )

    # LEFT
    draw.text(
        (60, 70),
        trade_name,
        fill=grey,
        font=font_trade
    )

    draw.text(
        (60, 145),
        date_text,
        fill=grey,
        font=font_medium
    )

    draw.text(
        (60, 220),
        qty_text,
        fill=grey,
        font=font_small
    )

    # RIGHT
    draw.text(
        (850, 70),
        profit_text,
        fill=green,
        font=font_profit
    )

    draw.text(
        (700, 145),
        f"{ltp_text} {percent_text}",
        fill=green,
        font=font_medium
    )

    draw.text(
        (930, 220),
        avg_text,
        fill=grey,
        font=font_small
    )

    # LINE
    draw.line(
        (60, 320, 1140, 320),
        fill=line,
        width=3
    )

    # PROFIT STAMP
    stamp = Image.new(
        "RGBA",
        (550, 160),
        (255, 255, 255, 0)
    )

    sdraw = ImageDraw.Draw(stamp)

    sdraw.rounded_rectangle(
        (20, 25, 530, 135),
        radius=8,
        outline="#0aa36c",
        width=6
    )

    sdraw.text(
        (95, 30),
        "PROFIT",
        fill="#0aa36c",
        font=font_stamp
    )

    img.paste(
        stamp,
        (330, 390),
        stamp
    )

    img.save(output_path)

    return output_path

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ Access denied."
        )

        return

    await update.message.reply_text(
        "👋 Welcome Admin!\n\nChoose an option:",
        reply_markup=main_menu()
    )

# =========================================================
# PREVIEW
# =========================================================

async def send_preview(update, context, post_no):

    posts = load_data()

    post = posts.get(str(post_no))

    if not post:

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Empty post."
        )

        return

    caption_parts = []

    if post.get("text"):
        caption_parts.append(post["text"])

    if post.get("url"):
        caption_parts.append(f"\n🔗 {post['url']}")

    caption = "\n".join(caption_parts).strip()

    if post.get("photo"):

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=post["photo"],
            caption=caption if caption else None
        )

    elif caption:

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=caption
        )

# =========================================================
# BUTTON HANDLER
# =========================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if not is_admin(update):

        await query.edit_message_text(
            "❌ Access denied."
        )

        return

    data = query.data

    # BACK MAIN
    if data == "back_main":

        await query.edit_message_text(
            "👋 Welcome Admin!\n\nChoose an option:",
            reply_markup=main_menu()
        )

    # WEEKLY
    elif data == "weekly":

        await query.edit_message_text(
            "📅 Select Weekly Update Post:",
            reply_markup=posts_menu()
        )

    # ADD NEW POST
    elif data == "add_new_post":

        await query.edit_message_text(
            "➕ Select any post and upload new data.",
            reply_markup=posts_menu()
        )

    # EDIT POST
    elif data.startswith("post_"):

        post_no = int(data.split("_")[1])

        await query.edit_message_text(
            f"📌 Editing Post {post_no}\n\n"
            "Allowed formats:\n"
            "✅ Photo Only\n"
            "✅ Photo + Text\n"
            "✅ Photo + URL\n"
            "✅ Photo + Text + URL",
            reply_markup=post_edit_menu(post_no)
        )

    # PHOTO
    elif data.startswith("upload_photo_"):

        post_no = data.split("_")[-1]

        context.user_data["mode"] = "photo"
        context.user_data["post_no"] = post_no

        await query.edit_message_text(
            f"📷 Send photo for Post {post_no}"
        )

    # TEXT
    elif data.startswith("upload_text_"):

        post_no = data.split("_")[-1]

        context.user_data["mode"] = "text"
        context.user_data["post_no"] = post_no

        await query.edit_message_text(
            f"📝 Send text for Post {post_no}"
        )

    # URL
    elif data.startswith("upload_url_"):

        post_no = data.split("_")[-1]

        context.user_data["mode"] = "url"
        context.user_data["post_no"] = post_no

        await query.edit_message_text(
            f"🔗 Send URL for Post {post_no}"
        )

    # PREVIEW
    elif data.startswith("preview_post_"):

        post_no = data.split("_")[-1]

        await send_preview(
            update,
            context,
            post_no
        )

    # CLEAR
    elif data.startswith("clear_post_"):

        post_no = data.split("_")[-1]

        posts = load_data()

        posts[str(post_no)] = {
            "photo": None,
            "text": "",
            "url": ""
        }

        save_data(posts)

        await query.edit_message_text(
            f"🗑 Post {post_no} cleared.",
            reply_markup=post_edit_menu(post_no)
        )

    # NEXT
    elif data.startswith("next_post_"):

        current = int(data.split("_")[-1])

        next_post = 1 if current == 5 else current + 1

        await query.edit_message_text(
            f"📌 Editing Post {next_post}",
            reply_markup=post_edit_menu(next_post)
        )

    # DAILY RESULT
    elif data == "daily_image":

        context.user_data["mode"] = "daily_result"

        await query.edit_message_text(
            "🖼 Send result data:\n\n"
            "VEDL 310 CE\n"
            "NSE | 26 May 2026\n"
            "Qty 0 Overnight\n"
            "Avg 0.00\n"
            "+₹10,350.00\n"
            "LTP 19.90\n"
            "(+117.49%)",
            reply_markup=daily_result_menu()
        )

# =========================================================
# RECEIVE CONTENT
# =========================================================

async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ Access denied."
        )

        return

    mode = context.user_data.get("mode")
    post_no = context.user_data.get("post_no")

    if not mode:
        return

    # DAILY RESULT
    if mode == "daily_result":

        if not update.message.text:

            await update.message.reply_text(
                "❌ Send text only."
            )

            return

        lines = [
            line.strip()
            for line in update.message.text.split("\n")
            if line.strip()
        ]

        if len(lines) < 7:

            await update.message.reply_text(
                "❌ Wrong format."
            )

            return

        image_path = create_result_image(
            trade_name=lines[0],
            date_text=lines[1],
            qty_text=lines[2],
            avg_text=lines[3],
            profit_text=lines[4],
            ltp_text=lines[5],
            percent_text=lines[6]
        )

        with open(image_path, "rb") as img:

            await update.message.reply_photo(
                photo=img,
                caption="✅ Daily result generated."
            )

        with open(image_path, "rb") as img:

            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption="📊 Daily Result Update"
            )

        context.user_data.clear()

        return

    posts = load_data()

    # PHOTO
    if mode == "photo":

        if not update.message.photo:

            await update.message.reply_text(
                "❌ Send photo only."
            )

            return

        posts[post_no]["photo"] = (
            update.message.photo[-1].file_id
        )

        save_data(posts)

        await update.message.reply_text(
            f"✅ Photo saved for Post {post_no}",
            reply_markup=post_edit_menu(post_no)
        )

    # TEXT
    elif mode == "text":

        if not update.message.text:

            await update.message.reply_text(
                "❌ Send text only."
            )

            return

        posts[post_no]["text"] = update.message.text

        save_data(posts)

        await update.message.reply_text(
            f"✅ Text saved for Post {post_no}",
            reply_markup=post_edit_menu(post_no)
        )

    # URL
    elif mode == "url":

        if not update.message.text:

            await update.message.reply_text(
                "❌ Send URL only."
            )

            return

        posts[post_no]["url"] = update.message.text

        save_data(posts)

        await update.message.reply_text(
            f"✅ URL saved for Post {post_no}",
            reply_markup=post_edit_menu(post_no)
        )

    context.user_data.clear()

# =========================================================
# AUTO POST
# =========================================================

async def publish_post(context: ContextTypes.DEFAULT_TYPE):

    post_no = str(context.job.data)

    posts = load_data()

    post = posts.get(post_no)

    if not post:
        return

    caption_parts = []

    if post.get("text"):
        caption_parts.append(post["text"])

    if post.get("url"):
        caption_parts.append(f"\n🔗 {post['url']}")

    caption = "\n".join(caption_parts).strip()

    photo = post.get("photo")

    # PHOTO + TEXT/URL
    if photo and caption:

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=caption
        )

    # PHOTO ONLY
    elif photo:

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo
        )

    # TEXT ONLY
    elif caption:

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption
        )

# =========================================================
# SCHEDULE
# =========================================================

def schedule_jobs(app: Application):

    for post_no, post_time in POST_TIMES.items():

        app.job_queue.run_daily(
            publish_post,
            time=post_time,
            data=post_no,
            name=f"post_{post_no}"
        )

# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:

        raise ValueError(
            "BOT_TOKEN missing."
        )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    schedule_jobs(app)

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.TEXT,
            receive_content
        )
    )

    print("Bot Started...")

    app.run_polling()

# =========================================================

if __name__ == "__main__":
    main()
