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

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, get_mention, format_money
from baka.database import users_collection

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Real Telegram Dice."""
    user = ensure_user_exists(update.effective_user)
    chat_id = update.effective_chat.id
    
    if not context.args: 
        return await update.message.reply_text("🎲 <b>Usage:</b> <code>/dice [amount]</code>", parse_mode=ParseMode.HTML)
    
    try: bet = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Invalid bet.", parse_mode=ParseMode.HTML)
    
    if bet < 50: return await update.message.reply_text("⚠️ Min bet is $50.", parse_mode=ParseMode.HTML)
    if user['balance'] < bet: return await update.message.reply_text("📉 Not enough money.", parse_mode=ParseMode.HTML)
    
    # Send the native Dice
    msg = await context.bot.send_dice(chat_id, emoji='🎲')
    result = msg.dice.value # 1-6
    
    # Wait for animation
    await asyncio.sleep(3)
    
    if result > 3: # 4, 5, 6 Wins
        win_amt = bet 
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": win_amt}})
        await update.message.reply_text(
            f"🎲 <b>Result:</b> {result}\n🎉 <b>You Won!</b> +<code>{format_money(win_amt)}</code>",
            reply_to_message_id=msg.message_id,
            parse_mode=ParseMode.HTML
        )
    else: # 1, 2, 3 Loses
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
        await update.message.reply_text(
            f"🎲 <b>Result:</b> {result}\n💀 <b>You Lost!</b> -<code>{format_money(bet)}</code>",
            reply_to_message_id=msg.message_id,
            parse_mode=ParseMode.HTML
        )

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Real Telegram Slots."""
    user = ensure_user_exists(update.effective_user)
    chat_id = update.effective_chat.id
    bet = 100 # Fixed bet
    
    if user['balance'] < bet: return await update.message.reply_text("📉 Need $100 to spin.", parse_mode=ParseMode.HTML)
    
    users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
    
    # Send native Slot Machine
    msg = await context.bot.send_dice(chat_id, emoji='🎰')
    value = msg.dice.value 
    # Values: 1-64. 
    # 64 = 777 (Jackpot), 1 = all different, 43 = grapes/grapes/grapes etc.
    # Telegram logic is complex, simpler approximation:
    
    await asyncio.sleep(2) # Wait for spin
    
    # Winning logic based on Telegram API values
    if value == 64: # 777
        prize = bet * 10
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": prize}})
        text = f"🎰 <b>JACKPOT! (777)</b>\n🎉 You won <code>{format_money(prize)}</code>!"
    elif value in [1, 22, 43]: # 3 matching fruits usually
        prize = bet * 3
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": prize}})
        text = f"🎰 <b>Winner!</b>\n🎉 You won <code>{format_money(prize)}</code>!"
    else:
        text = f"🎰 <b>Lost!</b> Better luck next time."

    await update.message.reply_text(text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML)
