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

import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.database import groups_collection
from baka.utils import get_mention, ensure_user_exists
from baka.config import WELCOME_IMG_URL, BOT_NAME, START_IMG_URL, SUPPORT_GROUP

async def welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable/Disable Welcomes."""
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("🍼 <b>This command works in grp only baby!</b>", parse_mode=ParseMode.HTML)
    
    member = await chat.get_member(user.id)
    if member.status not in ['administrator', 'creator']:
        return await update.message.reply_text("❌ <b>Admin only!</b>", parse_mode=ParseMode.HTML)

    if not args:
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/welcome on</code> or <code>off</code>", parse_mode=ParseMode.HTML)
    
    state = args[0].lower()
    if state in ['on', 'enable', 'yes']:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"welcome_enabled": True}}, upsert=True)
        await update.message.reply_text("✅ <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐄𝐧𝐚𝐛𝐥𝐞𝐝!</b>", parse_mode=ParseMode.HTML)
    elif state in ['off', 'disable', 'no']:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"welcome_enabled": False}}, upsert=True)
        await update.message.reply_text("❌ <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐃𝐢𝐬𝐚𝐛𝐥𝐞𝐝!</b>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("⚠️ Invalid option. Use <code>on</code> or <code>off</code>.", parse_mode=ParseMode.HTML)

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    for member in update.message.new_chat_members:
        # --- 🤖 BOT ADDED TO GROUP ---
        if member.id == context.bot.id:
            adder = update.message.from_user
            ensure_user_exists(adder)
            
            groups_collection.update_one({"chat_id": chat.id}, {"$set": {"welcome_enabled": True, "title": chat.title}}, upsert=True)
            
            txt = (
                f"🌸 <b>𝐀𝐫𝐢𝐠𝐚𝐭𝐨 {get_mention(adder)}!</b>\n\n"
                f"Thanks for adding <b>{chat.title}</b>! ✨\n\n"
                f"🎁 <b>First Time Bonus:</b>\n"
                f"Type <code>/claim</code> fast to get 2,000 Coins!\n"
                f"(Only the first person gets it!)"
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_GROUP)]])
            
            # Use Welcome Image (gyi5iu.jpg) for this interaction
            try: await update.message.reply_photo(WELCOME_IMG_URL, caption=txt, parse_mode=ParseMode.HTML, reply_markup=kb)
            except: await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=kb)

        # --- 👤 USER JOINED GROUP ---
        else:
            ensure_user_exists(member)
            group_data = groups_collection.find_one({"chat_id": chat.id})
            
            if group_data and group_data.get("welcome_enabled"):
                greetings = ["Hello", "Hiii", "Welcome", "Kon'nichiwa"]
                greet = random.choice(greetings)
                txt = f"👋 <b>{greet} {get_mention(member)}!</b>\n\nWelcome to <b>{chat.title}</b> 🌸\nDon't forget to /register!"
                try: await update.message.reply_photo(WELCOME_IMG_URL, caption=txt, parse_mode=ParseMode.HTML)
                except: await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
