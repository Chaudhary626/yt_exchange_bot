from database import get_pending_videos_to_assign, assign_video_to_user, get_assigned_video_for_user, user_is_blocked, unblock_user
from telebot import types

def handle_match(bot, message):
    user_id = message.from_user.id
    # Check if user is blocked (for incomplete tasks)
    if user_is_blocked(user_id):
        bot.send_message(user_id, "⏳ You are temporarily blocked from getting new tasks. Complete/verify your current task or wait 15 mins.")
        return

    # Check if user already has an assigned video that is not completed
    assigned = get_assigned_video_for_user(user_id)
    if assigned:
        bot.send_message(user_id, "You already have a task assigned! Use /proof after completing it, or /report if needed.")
        return

    # Find a pending video to assign
    candidates = get_pending_videos_to_assign(user_id)
    if not candidates:
        bot.send_message(user_id, "No available videos to help with at the moment. Try again later.")
        return
    video = candidates[0]
    assign_video_to_user(video['id'], user_id)
    txt = (
        f"🎬 *{video['title']}*\n"
        f"Duration: {video['duration']}s\n"
        f"Actions: {video['actions']}\n"
        f"Instructions: {video['instructions']}\n"
    )
    if video['method'] == 'link':
        txt += f"\n🔗 [Watch Video]({video['link']})"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Next Task", callback_data="next_task:"))
    bot.send_photo(user_id, video['thumbnail'], caption=txt, parse_mode="Markdown", reply_markup=markup)

def handle_next_task_callback(bot, call):
    user_id = call.from_user.id
    # Unblock user if eligible, assign next match
    unblock_user(user_id)
    bot.answer_callback_query(call.id, "You can now get your next task!")
    bot.send_message(user_id, "Use /match to get a new video task.")
