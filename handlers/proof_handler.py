from database import get_assigned_video_for_user, set_video_proof, get_owner_id_by_video
from telebot import types

def handle_proof(bot, message):
    user_id = message.from_user.id
    video = get_assigned_video_for_user(user_id)
    if not video:
        bot.send_message(user_id, "You have no assigned task right now.")
        return
    bot.send_message(user_id, "📤 Please upload your proof (photo, screenshot, or video) of helping.")

def handle_proof_document(bot, message):
    user_id = message.from_user.id
    video = get_assigned_video_for_user(user_id)
    if not video:
        bot.send_message(user_id, "You have no assigned task right now.")
        return
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        bot.send_message(user_id, "❌ Please upload a valid photo/video/document.")
        return
    set_video_proof(video['id'], file_id)
    owner_id = get_owner_id_by_video(video['id'])
    # Notify video owner for verification
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"proof_approve:{video['id']}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"proof_reject:{video['id']}")
    )
    bot.send_message(user_id, "Proof uploaded. Waiting for video owner's verification.")
    bot.send_message(owner_id, f"🔎 New proof submitted for your video '{video['title']}'. Please review and verify using /verify.", reply_markup=markup)

def handle_proof_callback(bot, call):
    action, video_id = call.data.split(":")
    video_id = int(video_id)
    if action == "proof_approve":
        from database import approve_proof, unblock_user, get_video_by_id
        approve_proof(video_id)
        video = get_video_by_id(video_id)
        unblock_user(video['assigned_to'])
        unblock_user(video['user_id'])
        bot.answer_callback_query(call.id, "Proof approved.")
        bot.send_message(video['assigned_to'], "✅ Your proof has been approved! You can now get your next task with /match.")
        bot.send_message(video['user_id'], f"✅ You have approved a helper for your video '{video['title']}'. You can now submit your next video or get a new task.")
    elif action == "proof_reject":
        from database import reject_proof, get_video_by_id
        reject_proof(video_id)
        video = get_video_by_id(video_id)
        bot.answer_callback_query(call.id, "Proof rejected.")
        bot.send_message(video['assigned_to'], "❌ Your proof was rejected. Please try again or contact the video owner.")