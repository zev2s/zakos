
import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("Панель управления ботом активна.")
    else:
        await update.message.reply_text(
            "Привет! Отправь сообщение, и оно будет доставлено администратору.\n"
            "Твой Telegram ID и username (если установлен) будут ему доступны."
        )


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    username = f"@{user.username}" if user.username else "Не указан"

    text = (
        "📩 НОВОЕ СООБЩЕНИЕ\n\n"
        f"👤 Username: {username}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 Сообщение:\n{message.text}\n\n"
        "↩️ Ответь на это сообщение, чтобы отправить ответ."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await message.reply_text("✅ Сообщение отправлено!")


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.reply_to_message:
        return

    original = message.reply_to_message.text or ""
    match = re.search(r"🆔 ID: (\d+)", original)

    if not match:
        return

    user_id = int(match.group(1))

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message.text
        )
        await message.reply_text("✅ Ответ отправлен!")
    except Exception:
        await message.reply_text("❌ Не удалось доставить сообщение.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.User(user_id=ADMIN_ID) & filters.TEXT & ~filters.COMMAND,
            admin_reply
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~filters.User(user_id=ADMIN_ID),
            receive_message
        )
    )

    print("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
