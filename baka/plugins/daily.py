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

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money
from baka.database import users_collection

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    now = datetime.utcnow()
    last = user.get("last_daily")
    
    if last and (now - last) < timedelta(hours=24):
        rem = timedelta(hours=24) - (now - last)
        return await update.message.reply_text(f"⏳ <b>Cooldown!</b> Wait {int(rem.total_seconds()//3600)}h.", parse_mode=ParseMode.HTML)
    
    streak = user.get("daily_streak", 0)
    if last and (now - last) > timedelta(hours=48): streak = 0 # Reset
    
    streak += 1
    reward = 500
    bonus = 10000 if streak % 7 == 0 else 0
    
    msg = f"📅 <b>Day {streak}!</b>\nReceived: <code>{format_money(reward)}</code>"
    if bonus: msg += f"\n🎉 <b>Weekly Bonus:</b> <code>{format_money(bonus)}</code>"
        
    users_collection.update_one(
        {"user_id": user['user_id']},
        {
            "$set": {"last_daily": now, "daily_streak": streak},
            "$inc": {"balance": reward + bonus}
        }
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
