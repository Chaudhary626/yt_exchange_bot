from database import add_report, get_video_by_id
from config import ADMIN_IDS

def handle_report(bot, message):
    msg = bot.send_message(message.chat.id, "Send the Video ID or paste the link you want to report:")
    bot.register_next_step_handler(msg, lambda m: report_reason(bot, m))

def report_reason(bot, message):
    video_id = None
    try:
        video_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "Invalid video id.")
        return
    msg = bot.send_message(message.chat.id, "Describe the reason for reporting:")
    bot.register_next_step_handler(msg, lambda m: report_submit(bot, m, video_id))

def report_submit(bot, message, video_id):
    reason = message.text.strip()
    user_id = message.from_user.id
    add_report(video_id, user_id, reason)
    # Notify admins
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"🚨 Report submitted!\nVideo ID: {video_id}\nBy: {user_id}\nReason: {reason}")
    bot.send_message(user_id, "✅ Report submitted. Thank you.")

def handle_report_callback(bot, call):
    pass  # Extend for inline report button if needed