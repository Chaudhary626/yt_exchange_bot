from database import get_videos_with_proof_for_owner, get_video_by_id
from telebot import types

def handle_verify(bot, message):
    user_id = message.from_user.id
    videos = get_videos_with_proof_for_owner(user_id)
    if not videos:
        bot.send_message(user_id, "No proofs to verify for your videos.")
        return
    for v in videos:
        txt = (
            f"🎬 *{v['title']}*\n"
            f"Duration: {v['duration']}s\n"
            f"Actions: {v['actions']}\n"
            f"Instructions: {v['instructions']}\n"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"proof_approve:{v['id']}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"proof_reject:{v['id']}")
        )
        bot.send_message(user_id, txt, parse_mode="Markdown", reply_markup=markup)

def handle_verify_callback(bot, call):
    # This is handled in proof_handler for approve/reject
    pass