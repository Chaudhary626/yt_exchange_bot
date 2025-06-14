from database import get_or_create_user

def handle_start(bot, message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    is_new = get_or_create_user(user_id, username)
    text = (
        "👋 Welcome to the YouTube Engagement Exchange Bot!\n\n"
        "🔁 *How it works:*\n"
        "1. Submit your YouTube video using /submit (max 5).\n"
        "2. Help others by watching/liking/commenting (use /match to get a task).\n"
        "3. Upload proof via /proof.\n"
        "4. Get your video shown to others after helping!\n\n"
        "Anti-fraud, timeouts, and fair exchange enforced.\n\n"
        "Use /submit, /match, /proof, /verify, /videos, /report at any time.\n"
    )
    bot.send_message(user_id, text, parse_mode="Markdown")