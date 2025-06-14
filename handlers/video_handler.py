from database import get_user_videos, remove_video
from telebot import types

def handle_videos(bot, message):
    user_id = message.from_user.id
    videos = get_user_videos(user_id)
    if not videos:
        bot.send_message(user_id, "You have not submitted any videos.")
        return
    for v in videos:
        txt = (
            f"🎬 *{v['title']}*\n"
            f"Duration: {v['duration']}s\n"
            f"Status: {v['status']}\n"
            f"Actions: {v['actions']}\n"
            f"Method: {v['method']}\n"
            f"Instructions: {v['instructions']}\n"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Remove", callback_data=f"remove_video:{v['id']}"))
        bot.send_photo(user_id, v['thumbnail'], caption=txt, parse_mode="Markdown", reply_markup=markup)

def handle_remove_video_callback(bot, call):
    user_id = call.from_user.id
    video_id = int(call.data.split(":")[1])
    remove_video(video_id, user_id)
    bot.answer_callback_query(call.id, "Video removed.")
    bot.edit_message_text("✅ Video removed.", chat_id=call.message.chat.id, message_id=call.message.message_id)