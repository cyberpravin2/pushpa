# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
#
# All rights reserved.
#
# This code is the intellectual property of @WTF_Phantom.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: king25258069@gmail.com

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from baka.utils import get_mention, track_group, log_to_channel
from baka.database import groups_collection

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles updates when the Bot's status changes in a chat.
    """
    if not update.my_chat_member: return
    
    new_member = update.my_chat_member.new_chat_member
    old_member = update.my_chat_member.old_chat_member
    chat = update.my_chat_member.chat
    user = update.my_chat_member.from_user
    
    # Track Group & User relationship
    track_group(chat, user)

    # Case 1: Bot Added or Promoted
    if new_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        if old_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]: return 

        link = "No Link (Not Admin)"
        if new_member.status == ChatMember.ADMINISTRATOR:
            try: link = await context.bot.export_chat_invite_link(chat.id)
            except: pass
        
        await log_to_channel(context.bot, "join", {
            "user": f"{get_mention(user)} (`{user.id}`)",
            "chat": f"{chat.title} (`{chat.id}`)",
            "link": link,
            "action": "Bot was added to a new group"
        })
    
    # Case 2: Bot Removed, Left, or Banned
    elif new_member.status in [ChatMember.LEFT, ChatMember.BANNED]:
        groups_collection.delete_one({"chat_id": chat.id})
        await log_to_channel(context.bot, "leave", {
            "user": f"{get_mention(user)} (`{user.id}`)",
            "chat": f"{chat.title} (`{chat.id}`)",
            "action": "Bot was kicked or left the group"
        })

# --- SAFE ASYNC TRACKER ---
async def group_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Async wrapper to track groups on every message.
    Used in Ryan.py to prevent crashes.
    """
    if update.effective_chat and update.effective_user:
        track_group(update.effective_chat, update.effective_user)