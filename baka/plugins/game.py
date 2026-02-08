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
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, PROTECT_2D_COST, REVIVE_COST, AUTO_REVIVE_HOURS, OWNER_ID
from baka.utils import ensure_user_exists, resolve_target, is_protected, get_active_protection, format_time, format_money, get_mention, check_auto_revive, stylize_text
from baka.database import users_collection
from baka.plugins.chatbot import ask_mistral_raw

# --- AI NARRATION ---
async def get_narrative(action_type, attacker_mention, target_mention):
    if action_type == 'kill':
        prompt = "Write a funny, savage kill message where 'P1' kills 'P2'. Max 15 words. Use Hinglish."
    elif action_type == 'rob':
        prompt = "Write a funny robbery message where 'P1' steals from 'P2'. Max 15 words. Use Hinglish."
    else: return "P1 interaction P2."
    res = await ask_mistral_raw("Game Narrator", prompt, 50)
    text = res if res and "P1" in res else f"P1 {action_type} P2!"
    return text.replace("P1", attacker_mention).replace("P2", target_mention)

# --- KILL ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = ensure_user_exists(update.effective_user)
    target, error = await resolve_target(update, context)
    if not target: return await update.message.reply_text(error if error else "⚠️ <b>Reply</b> or <b>Tag</b> to kill!", parse_mode=ParseMode.HTML)

    # Checks
    if target.get('is_bot'): return await update.message.reply_text("🤖 <b>Bot Shield!</b> Can't kill robots.", parse_mode=ParseMode.HTML)
    if target['user_id'] == OWNER_ID: return await update.message.reply_text("🙊 <b>Senpai Shield!</b> Can't kill the Owner.", parse_mode=ParseMode.HTML)
    if attacker['status'] == 'dead': return await update.message.reply_text("💀 <b>You are dead!</b> Wait 6h or /revive.", parse_mode=ParseMode.HTML)
    if target['user_id'] == attacker['user_id']: return await update.message.reply_text("🤔 Don't kill yourself.", parse_mode=ParseMode.HTML)
    if target['status'] == 'dead': return await update.message.reply_text("⚰️ <b>Already dead!</b>", parse_mode=ParseMode.HTML)
    
    expiry = get_active_protection(target)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(f"🛡️ <b>Blocked!</b> Target is protected for <code>{format_time(rem)}</code>.", parse_mode=ParseMode.HTML)

    # Logic
    base_reward = random.randint(100, 200)
    buff = sum(i['buff'] for i in attacker.get('inventory', []) if i['type'] == 'weapon')
    final_reward = int(base_reward * (1 + buff))
    
    # Loot Item (50%)
    stolen_item_text = ""
    t_inv = target.get('inventory', [])
    if t_inv and random.random() < 0.50:
        item = random.choice(t_inv)
        users_collection.update_one({"user_id": target["user_id"]}, {"$pull": {"inventory": {"id": item['id']}}})
        users_collection.update_one({"user_id": attacker["user_id"]}, {"$push": {"inventory": item}})
        stolen_item_text = f"\n🎒 <b>{stylize_text('Looted')}:</b> {item['name']}"

    # Execute
    users_collection.update_one({"user_id": target["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker["user_id"]}, {"$inc": {"kills": 1, "balance": final_reward}})

    narration = await get_narrative("kill", get_mention(attacker), get_mention(target))
    buff_text = f"(+{int(buff*100)}% Buff)" if buff > 0 else ""

    await update.message.reply_text(
        f"🔪 <b>{stylize_text('MURDER')}!</b>\n\n"
        f"📝 <i>{narration}</i>\n\n"
        f"😈 <b>{stylize_text('Killer')}:</b> {get_mention(attacker)}\n"
        f"💀 <b>{stylize_text('Victim')}:</b> {get_mention(target)}\n"
        f"💵 <b>{stylize_text('Loot')}:</b> <code>{format_money(final_reward)}</code> {buff_text}{stolen_item_text}", 
        parse_mode=ParseMode.HTML
    )

# --- ROB ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text("⚠️ <code>/rob 100 @user</code>", parse_mode=ParseMode.HTML)
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Invalid Amount", parse_mode=ParseMode.HTML)

    target_arg = context.args[1] if len(context.args) > 1 else None
    target, error = await resolve_target(update, context, specific_arg=target_arg)
    if not target: return await update.message.reply_text(error or "⚠️ Tag victim", parse_mode=ParseMode.HTML)

    if target.get('is_bot') or target['user_id'] == OWNER_ID: return await update.message.reply_text("🛡️ Protected Entity.", parse_mode=ParseMode.HTML)
    if attacker['status'] == 'dead': return await update.message.reply_text("💀 Dead men steal no coins.", parse_mode=ParseMode.HTML)
    if target['user_id'] == attacker['user_id']: return await update.message.reply_text("🤦‍♂️ No.", parse_mode=ParseMode.HTML)
    
    expiry = get_active_protection(target)
    if expiry:
        rem = expiry - datetime.utcnow()
        return await update.message.reply_text(f"🛡️ <b>Shielded!</b> Protected for <code>{format_time(rem)}</code>.", parse_mode=ParseMode.HTML)

    if target['balance'] < amount: return await update.message.reply_text("📉 Too poor.", parse_mode=ParseMode.HTML)

    # Block
    block_chance = sum(i['buff'] for i in target.get('inventory', []) if i['type'] == 'armor')
    if random.random() < block_chance:
        return await update.message.reply_text(f"🛡️ <b>BLOCKED!</b> {get_mention(target)}'s armor stopped you!", parse_mode=ParseMode.HTML)

    # Loot Item (Dead Only)
    stolen_item_text = ""
    if target['status'] == 'dead':
        t_inv = target.get('inventory', [])
        if t_inv and random.random() < 0.20:
            item = random.choice(t_inv)
            users_collection.update_one({"user_id": target["user_id"]}, {"$pull": {"inventory": {"id": item['id']}}})
            users_collection.update_one({"user_id": attacker["user_id"]}, {"$push": {"inventory": item}})
            stolen_item_text = f"\n🎒 <b>{stylize_text('Looted Corpse')}:</b> {item['name']}"

    # Execute
    users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": attacker["user_id"]}, {"$inc": {"balance": amount}})
    
    att_link = get_mention(attacker)
    tar_link = get_mention(target)
    narration = await get_narrative("rob", att_link, tar_link)
    
    header = f"🧟 <b>{stylize_text('GRAVE ROBBERY')}!</b>" if target['status'] == 'dead' else f"💰 <b>{stylize_text('ROBBERY')}!</b>"

    await update.message.reply_text(
        f"{header}\n\n"
        f"📝 <i>{narration}</i>\n\n"
        f"😈 <b>{stylize_text('Thief')}:</b> {att_link}\n"
        f"💸 <b>{stylize_text('Stolen')}:</b> <code>{format_money(amount)}</code>{stolen_item_text}", 
        parse_mode=ParseMode.HTML
    )

# --- PROTECT ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text(f"🛡️ <b>Usage:</b> <code>/protect 1d</code>", parse_mode=ParseMode.HTML)

    dur = context.args[0].lower()
    if dur == '1d': cost, days = PROTECT_1D_COST, 1
    elif dur == '2d': cost, days = PROTECT_2D_COST, 2
    else: return await update.message.reply_text("⚠️ 1d or 2d only!", parse_mode=ParseMode.HTML)

    target_arg = context.args[1] if len(context.args) > 1 else None
    target, _ = await resolve_target(update, context, specific_arg=target_arg)
    if not target: target = sender
    is_self = target['user_id'] == sender['user_id']

    if not is_self and sender.get("partner_id") != target["user_id"]:
         return await update.message.reply_text("⛔ You can only protect yourself or your partner!", parse_mode=ParseMode.HTML)

    expiry = get_active_protection(target)
    if expiry:
        rem = expiry - datetime.utcnow()
        msg = f"🛡️ <b>Already Safe!</b> Expires in <code>{format_time(rem)}</code>."
        if not is_self: msg = f"🛡️ <b>Safe!</b> {get_mention(target)} has <code>{format_time(rem)}</code> left."
        return await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    
    if sender['balance'] < cost: return await update.message.reply_text(f"❌ <b>Poor!</b> Need <code>{format_money(cost)}</code>.", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -cost}})
    expiry_dt = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one({"user_id": target["user_id"]}, {"$set": {"protection_expiry": expiry_dt}})
    
    partner_id = target.get("partner_id")
    extra = ""
    if partner_id:
        users_collection.update_one({"user_id": partner_id}, {"$set": {"protection_expiry": expiry_dt}})
        extra = "\n💞 <b>Bonus:</b> Partner also protected!"

    if is_self: await update.message.reply_text(f"🛡️ <b>{stylize_text('Shield Active')}!</b> Safe for {days} days.{extra}", parse_mode=ParseMode.HTML)
    else: await update.message.reply_text(f"🛡️ <b>{stylize_text('Guardian')}!</b> You protected {get_mention(target)}.{extra}", parse_mode=ParseMode.HTML)

async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reviver = ensure_user_exists(update.effective_user)
    target, _ = await resolve_target(update, context)
    if not target: target = reviver

    if target['status'] == 'alive': return await update.message.reply_text("✨ Alive!", parse_mode=ParseMode.HTML)
    
    if check_auto_revive(target):
        return await update.message.reply_text("✨ <b>Miracle!</b> Auto-revived just now.", parse_mode=ParseMode.HTML)

    if reviver['balance'] < REVIVE_COST: return await update.message.reply_text(f"❌ Need <code>{format_money(REVIVE_COST)}</code>.", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": reviver["user_id"]}, {"$inc": {"balance": -REVIVE_COST}})
    users_collection.update_one({"user_id": OWNER_ID}, {"$inc": {"balance": REVIVE_COST}})
    users_collection.update_one({"user_id": target["user_id"]}, {"$set": {"status": "alive", "death_time": None}})
    await update.message.reply_text(f"💖 <b>{stylize_text('Revived')}!</b> Paid {format_money(REVIVE_COST)}.", parse_mode=ParseMode.HTML)
