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
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.utils import ensure_user_exists, resolve_target, get_mention, format_money, stylize_text
from baka.database import users_collection
from baka.config import DIVORCE_COST
from baka.plugins.chatbot import ask_mistral_raw

# ... (Helpers remain same) ...
def get_progress_bar(percent):
    filled = int(percent / 10)
    bar = "█" * filled + "▒" * (10 - filled)
    return bar
def get_love_comment(percent):
    if percent < 30: return "💔 Terrible!"
    if percent < 80: return "💖 Cute!"
    return "🔥 Soulmates!"

async def couple_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE: return await update.message.reply_text("❌ Group Only!", parse_mode=ParseMode.HTML)

    user1 = ensure_user_exists(user)
    target, _ = await resolve_target(update, context)
    if target: user2 = target
    else:
        try:
            pipeline = [{"$match": {"seen_groups": chat.id, "user_id": {"$ne": user.id}}}, {"$sample": {"size": 1}}]
            results = list(users_collection.aggregate(pipeline))
            if not results: return await update.message.reply_text("😔 Forever Alone.", parse_mode=ParseMode.HTML)
            user2 = results[0]
        except: return
    
    percent = random.randint(0, 100)
    await update.message.reply_text(
        f"💘 <b>{stylize_text('Couple Matcher')}</b>\n\n🔻 {get_mention(user1)}\n🔺 {get_mention(user2)}\n\n💟 <b>Score:</b> {percent}%\n<code>{get_progress_bar(percent)}</code>\n💭 <i>{get_love_comment(percent)}</i>",
        parse_mode=ParseMode.HTML
    )

async def propose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    if sender.get("partner_id"): return await update.message.reply_text("❌ Married!", parse_mode=ParseMode.HTML)
    
    target_arg = context.args[0] if context.args else None
    target, error = await resolve_target(update, context, specific_arg=target_arg)
    if not target: return await update.message.reply_text(error or "Usage: <code>/propose @user</code>", parse_mode=ParseMode.HTML)
    if target['user_id'] == sender['user_id'] or target.get('partner_id'): return await update.message.reply_text("💔 Invalid.", parse_mode=ParseMode.HTML)

    s_id, t_id = sender['user_id'], target['user_id']
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💍 Accept", callback_data=f"marry_y|{s_id}|{t_id}"), InlineKeyboardButton("🗑️ Reject", callback_data=f"marry_n|{s_id}|{t_id}")]])
    
    msg = await update.message.reply_text(f"💘 <b>{stylize_text('Proposal')}!</b>\n\n👤 {get_mention(sender)} loves {get_mention(target)}!\n<i>Will you marry them?</i>\n⏳ 30s...", reply_markup=kb, parse_mode=ParseMode.HTML)
    
    async def delete():
        await asyncio.sleep(30)
        try: await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text="❌ Expired.", parse_mode=ParseMode.HTML)
        except: pass
    asyncio.create_task(delete())

async def marry_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_arg = context.args[0] if context.args else None
    target, _ = await resolve_target(update, context, specific_arg=target_arg)
    user = target if target else ensure_user_exists(update.effective_user)
    
    pid = user.get("partner_id")
    if pid:
        p = users_collection.find_one({"user_id": pid})
        status = f"💍 Married to {get_mention(p) if p else pid}"
    else: status = "🦅 Single"
    
    await update.message.reply_text(f"📊 <b>Status:</b>\n👤 {get_mention(user)}\n{status}", parse_mode=ParseMode.HTML)

async def divorce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if not user.get("partner_id"): return await update.message.reply_text("🤷‍♂️ Single.", parse_mode=ParseMode.HTML)
    if user['balance'] < DIVORCE_COST: return await update.message.reply_text(f"❌ Cost: {format_money(DIVORCE_COST)}", parse_mode=ParseMode.HTML)
    
    pid = user["partner_id"]
    users_collection.update_one({"user_id": user["user_id"]}, {"$set": {"partner_id": None}, "$inc": {"balance": -DIVORCE_COST}})
    users_collection.update_one({"user_id": pid}, {"$set": {"partner_id": None}})
    await update.message.reply_text(f"💔 <b>Divorced!</b> Paid {format_money(DIVORCE_COST)}.", parse_mode=ParseMode.HTML)

async def proposal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("|")
    action, p_id, t_id = data[0], int(data[1]), int(data[2])
    
    if query.from_user.id != t_id: return await query.answer("❌ Not for you!", show_alert=True)
    
    if action == "marry_y":
        users_collection.update_one({"user_id": p_id}, {"$set": {"partner_id": t_id}})
        users_collection.update_one({"user_id": t_id}, {"$set": {"partner_id": p_id}})
        await query.message.edit_text(f"💍 <b>{stylize_text('Just Married')}!</b>\n<a href='tg://user?id={p_id}'>P1</a> ❤️ <a href='tg://user?id={t_id}'>P2</a>\n✨ 5% Tax Perk Active!", parse_mode=ParseMode.HTML)
    elif action == "marry_n":
        roast = await ask_mistral_raw("Roaster", "Roast a rejected proposal.")
        await query.message.edit_text(f"❌ <b>Rejected!</b>\n🔥 {stylize_text(roast or 'Ouch.')}", parse_mode=ParseMode.HTML)