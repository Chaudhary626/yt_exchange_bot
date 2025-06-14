from database import get_user_video_count, submit_video, get_user_videos, remove_video
from telebot import types

def handle_submit(bot, message):
    user_id = message.from_user.id
    if get_user_video_count(user_id) >= 5:
        bot.send_message(user_id, "❌ You can only have 5 videos at a time. Remove one using /videos.")
        return

    msg = bot.send_message(user_id, "🎬 Send the *Title* of your YouTube video:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: submit_title(bot, m, {}))

def submit_title(bot, message, data):
    data['title'] = message.text.strip()
    msg = bot.send_message(message.chat.id, "🖼️ Send the *Thumbnail URL*:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: submit_thumbnail(bot, m, data))

def submit_thumbnail(bot, message, data):
    data['thumbnail'] = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏱️ Send the *Duration* in seconds (max 300):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: submit_duration(bot, m, data))

def submit_duration(bot, message, data):
    try:
        duration = int(message.text.strip())
        if duration > 300:
            raise Exception("Too long")
        data['duration'] = duration
    except:
        bot.send_message(message.chat.id, "❌ Please enter a valid duration in seconds (max 300).")
        return
    msg = bot.send_message(message.chat.id, "🔗 Send the *YouTube link* (or 'manual' if you want manual method):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: submit_link_method(bot, m, data))

def submit_link_method(bot, message, data):
    val = message.text.strip()
    if val.lower() == 'manual':
        data['method'] = 'manual'
        data['link'] = ""
    else:
        data['method'] = 'link'
        data['link'] = val
    msg = bot.send_message(message.chat.id, "💡 What actions are required? (Like/Comment/Subscribe, e.g. 'Like,Subscribe')", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: submit_actions(bot, m, data))

def submit_actions(bot, message, data):
    data['actions'] = message.text.strip()
    msg = bot.send_message(message.chat.id, "📝 Add any instructions for helpers (or 'none'):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: submit_instructions(bot, m, data))

def submit_instructions(bot, message, data):
    data['instructions'] = message.text.strip()
    submit_video(
        user_id=message.from_user.id,
        title=data['title'],
        thumbnail=data['thumbnail'],
        duration=data['duration'],
        link=data['link'],
        actions=data['actions'],
        method=data['method'],
        instructions=data['instructions']
    )
    bot.send_message(message.chat.id, "✅ Video submitted! Use /videos to view or remove.")

def handle_remove_video(bot, message):
    user_id = message.from_user.id
    videos = get_user_videos(user_id)
    if not videos:
        bot.send_message(user_id, "You have no videos to remove.")
        return
    markup = types.InlineKeyboardMarkup()
    for v in videos:
        markup.add(types.InlineKeyboardButton(f"Remove {v['title']}", callback_data=f"remove_video:{v['id']}"))
    bot.send_message(user_id, "Select a video to remove:", reply_markup=markup)

def handle_remove_video_callback(bot, call):
    user_id = call.from_user.id
    video_id = int(call.data.split(":")[1])
    remove_video(video_id, user_id)
    bot.answer_callback_query(call.id, "Video removed.")
    bot.edit_message_text("✅ Video removed.", chat_id=call.message.chat.id, message_id=call.message.message_id)

def handle_submit_callback(bot, call):
    pass  # Not needed for submit currently