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

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import REGISTER_BONUS, OWNER_ID, TAX_RATE, CLAIM_BONUS, MARRIED_TAX_RATE, SHOP_ITEMS, MIN_CLAIM_MEMBERS
from baka.utils import ensure_user_exists, get_mention, format_money, resolve_target, log_to_channel, stylize_text, track_group
from baka.database import users_collection, groups_collection
from baka.plugins.chatbot import ask_mistral_raw

# --- INVENTORY CALLBACK ---
async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("|")
    item_id = data[1]
    
    item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
    if not item: return await query.answer("❌ Error", show_alert=True)

    rarity = "⚪ Common"
    if item['price'] > 50000: rarity = "🔵 Rare"
    if item['price'] > 500000: rarity = "🟡 Legendary"
    if item['price'] > 10000000: rarity = "🔴 Godly"

    text = f"💎 {stylize_text(item['name'])}\n💰 {format_money(item['price'])}\n🌟 {rarity}\n🛡️ Safe (Until Death)"
    await query.answer(text, show_alert=True)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if users_collection.find_one({"user_id": user.id}): 
        return await update.message.reply_text(f"✨ <b>Ara?</b> {get_mention(user)}, already registered!", parse_mode=ParseMode.HTML)
    
    ensure_user_exists(user)
    users_collection.update_one({"user_id": user.id}, {"$set": {"balance": REGISTER_BONUS}})
    await update.message.reply_text(f"🎉 <b>Yayy!</b> {get_mention(user)} Registered!\n🎁 <b>Bonus:</b> <code>+{format_money(REGISTER_BONUS)}</code>", parse_mode=ParseMode.HTML)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target, error = await resolve_target(update, context)
    if not target and error == "No target": target = ensure_user_exists(update.effective_user)
    elif not target: return await update.message.reply_text(error, parse_mode=ParseMode.HTML)

    rank = users_collection.count_documents({"balance": {"$gt": target["balance"]}}) + 1
    status = "💖 Alive" if target['status'] == 'alive' else "💀 Dead"
    
    inventory = target.get('inventory', [])
    weapons = [i for i in inventory if i['type'] == 'weapon']
    armors = [i for i in inventory if i['type'] == 'armor']
    flex = [i for i in inventory if i['type'] == 'flex']
    
    best_w = max(weapons, key=lambda x: x['buff'])['name'] if weapons else "None"
    best_a = max(armors, key=lambda x: x['buff'])['name'] if armors else "None"
    
    kb = []
    row = []
    for item in flex:
        row.append(InlineKeyboardButton(item['name'], callback_data=f"inv_view|{item['id']}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row: kb.append(row)
    
    msg = (
        f"👤 <b>{get_mention(target)}</b>\n"
        f"👛 <b>{format_money(target['balance'])}</b> | 🏆 <b>#{rank}</b>\n"
        f"❤️ <b>{status}</b> | ⚔️ <b>{target['kills']} Kills</b>\n\n"
        f"🎒 <b>{stylize_text('Active Gear')}</b>:\n"
        f"🗡️ {best_w}\n🛡️ {best_a}\n\n"
        f"💎 <b>{stylize_text('Flex Collection')}</b>:"
    )
    if not flex: msg += "\n<i>Empty...</i>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb) if kb else None)

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rich = users_collection.find().sort("balance", -1).limit(10)
    kills = users_collection.find().sort("kills", -1).limit(10)
    def get_badge(i): return ["🥇","🥈","🥉"][i-1] if i<=3 else f"<code>{i}.</code>"

    msg = f"🏆 <b>{stylize_text('GLOBAL LEADERBOARD')}</b> 🏆\n\n💰 <b>{stylize_text('Top Richest')}</b>:\n"
    for i, d in enumerate(rich, 1): msg += f"{get_badge(i)} {get_mention(d)} » <b>{format_money(d['balance'])}</b>\n"
    
    msg += f"\n🩸 <b>{stylize_text('Top Killers')}</b>:\n"
    for i, d in enumerate(kills, 1): msg += f"{get_badge(i)} {get_mention(d)} » <b>{d.get('kills',0)} Kills</b>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# ... (Keep claim and give functions from previous version, they are fine) ...
# I am re-pasting them below for completeness.

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    ensure_user_exists(user)
    group_doc = groups_collection.find_one({"chat_id": chat.id})
    if not group_doc: return 
    if group_doc.get("claimed"): return await update.message.reply_text("❌ <b>Too late!</b> Claimed.", parse_mode=ParseMode.HTML)
    
    try: count = await context.bot.get_chat_member_count(chat.id)
    except: return await update.message.reply_text("⚠️ Admin Rights Needed!", parse_mode=ParseMode.HTML)

    if count < MIN_CLAIM_MEMBERS:
        roast = await ask_mistral_raw("Roaster", f"Roast {user.first_name} for claiming in a group with only {count} members.")
        return await update.message.reply_text(f"❌ <b>Failed!</b> Need {MIN_CLAIM_MEMBERS} members.\n🔥 {stylize_text(roast or 'Lol no.')}", parse_mode=ParseMode.HTML)
    
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": CLAIM_BONUS}})
    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"claimed": True}})
    await update.message.reply_text(f"💎 <b>Claimed {format_money(CLAIM_BONUS)}!</b>", parse_mode=ParseMode.HTML)

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    args = context.args
    if not args: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/give 100 @user</code>", parse_mode=ParseMode.HTML)
    amount = None
    target_str = None
    for arg in args:
        if arg.isdigit() and amount is None: amount = int(arg)
        else: target_str = arg
    if amount is None: return await update.message.reply_text("⚠️ Invalid Amount", parse_mode=ParseMode.HTML)

    target, error = await resolve_target(update, context, specific_arg=target_str)
    if not target: return await update.message.reply_text(error or "⚠️ Tag someone.", parse_mode=ParseMode.HTML)

    if amount <= 0 or sender['balance'] < amount or sender['user_id'] == target['user_id']: return await update.message.reply_text("⚠️ Invalid Transaction.", parse_mode=ParseMode.HTML)

    tax_rate = MARRIED_TAX_RATE if sender.get("partner_id") == target["user_id"] else TAX_RATE
    tax = int(amount * tax_rate)
    final = amount - tax
    
    users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": final}})
    users_collection.update_one({"user_id": OWNER_ID}, {"$inc": {"balance": tax}})

    msg = f"💸 <b>{stylize_text('Transfer Complete')}!</b>\n👤 From: {get_mention(sender)}\n👤 To: {get_mention(target)}\n💰 Sent: <code>{format_money(final)}</code>\n🏦 Tax: <code>{format_money(tax)}</code>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    await log_to_channel(context.bot, "transfer", {"user": sender['name'], "action": f"Sent {amount} to {target['name']}", "chat": "Economy"})