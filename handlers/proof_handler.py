from database import (
    get_assigned_video_for_user, set_video_proof, get_owner_id_by_video,
    approve_proof, unblock_user, get_video_by_id, reject_proof
)
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
    media_type = None
    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    elif message.document:
        file_id = message.document.file_id
        media_type = "document"
    else:
        bot.send_message(user_id, "❌ Please upload a valid photo/video/document.")
        return

    # Store media as "type:file_id"
    set_video_proof(video['id'], f"{media_type}:{file_id}")
    owner_id = get_owner_id_by_video(video['id'])

    # Compose video info for caption
    txt = (
        f"🎬 *{video['title']}*\n"
        f"Duration: {video['duration']}s\n"
        f"Actions: {video['actions']}\n"
        f"Instructions: {video['instructions']}\n"
    )
    if video['method'] == "link" and video['link']:
        txt += f"\n🔗 [Watch Video]({video['link']})"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"proof_approve:{video['id']}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"proof_reject:{video['id']}")
    )

    bot.send_message(user_id, "Proof uploaded. Waiting for video owner's verification.")

    # Send the proof media + video info to owner with approve/reject
    if media_type == "photo":
        bot.send_photo(owner_id, file_id, caption=txt, parse_mode="Markdown", reply_markup=markup)
    elif media_type == "video":
        bot.send_video(owner_id, file_id, caption=txt, parse_mode="Markdown", reply_markup=markup)
    elif media_type == "document":
        bot.send_document(owner_id, file_id, caption=txt, parse_mode="Markdown", reply_markup=markup)

def handle_proof_callback(bot, call):
    action, video_id = call.data.split(":")
    video_id = int(video_id)
    video = get_video_by_id(video_id)
    if action == "proof_approve":
        approve_proof(video_id)
        unblock_user(video['assigned_to'])
        unblock_user(video['user_id'])
        bot.answer_callback_query(call.id, "Proof approved.")
        # Notify proof submitter
        bot.send_message(video['assigned_to'], "✅ Your proof has been approved! You can now get your next task with /match.")
        # Show video details to the owner for transparency
        txt = (
            f"✅ You have approved a helper for your video!\n\n"
            f"🎬 *{video['title']}*\n"
            f"Duration: {video['duration']}s\n"
            f"Actions: {video['actions']}\n"
            f"Instructions: {video['instructions']}\n"
        )
        if video['method'] == "link" and video['link']:
            txt += f"\n🔗 [Watch Video]({video['link']})"
        bot.send_message(video['user_id'], txt, parse_mode="Markdown")
    elif action == "proof_reject":
        reject_proof(video_id)
        bot.answer_callback_query(call.id, "Proof rejected.")
        bot.send_message(video['assigned_to'], "❌ Your proof was rejected. Please try again or contact the video owner.")
