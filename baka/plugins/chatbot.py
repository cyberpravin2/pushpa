import httpx
import random
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction, ChatType
from baka.config import MISTRAL_API_KEY, GROQ_API_KEY, CODESTRAL_API_KEY
from baka.database import chatbot_collection
from baka.utils import stylize_text


# ================= CONFIG =================

MAX_HISTORY = 8
DEFAULT_MODEL = "mistral"

MODELS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama3-70b-8192",
        "key": GROQ_API_KEY
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-large-latest",
        "key": MISTRAL_API_KEY
    },
    "codestral": {
        "url": "https://codestral.mistral.ai/v1/chat/completions",
        "model": "codestral-latest",
        "key": CODESTRAL_API_KEY
    }
}

FALLBACK_RESPONSES = [
    "Achha ji 😊",
    "Hmm… aur batao?",
    "Okk okk!",
    "Sahi hai",
    "Interesting",
]

print("MISTRAL KEY:", bool(MISTRAL_API_KEY))
print("GROQ KEY:", bool(GROQ_API_KEY))
print("CODESTRAL KEY:", bool(CODESTRAL_API_KEY))


# ================= SAFE API CALL =================

async def call_model_api(provider, messages, max_tokens):
    conf = MODELS.get(provider)

    if not conf:
        print("❌ Missing model config:", provider)
        return None

    if not conf.get("key"):
        print("❌ Missing API key:", provider)
        return None

    headers = {
        "Authorization": f"Bearer {conf['key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": conf["model"],
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": max_tokens,
        "top_p": 0.9
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(conf["url"], json=payload, headers=headers)

            print(f"📡 {provider} STATUS:", resp.status_code)

            if resp.status_code != 200:
                print("❌ API ERROR:", resp.text)
                return None

            data = resp.json()

            if "choices" not in data:
                print("❌ BAD RESPONSE:", data)
                return None

            return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"🔥 {provider} CRASH:", e)
        return None


# ================= AI RESPONSE ENGINE =================

async def get_ai_response(chat_id, user_input, user_name, selected_model=DEFAULT_MODEL):

    code_keywords = [
        "code", "python", "html", "css", "javascript",
        "fix", "error", "debug", "function", "class", "import"
    ]

    is_code = any(k in user_input.lower() for k in code_keywords)

    if is_code:
        active_model = "codestral"
        max_tokens = 4096
        system_prompt = "You are a professional coding assistant."
    else:
        active_model = selected_model
        max_tokens = 200
        system_prompt = "You are a friendly Hinglish chatbot."

    # ===== MEMORY LOAD =====
    doc = chatbot_collection.find_one({"chat_id": chat_id}) or {}
    history = doc.get("history", [])

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history[-MAX_HISTORY:]:
        messages.append(msg)

    messages.append({"role": "user", "content": user_input})

    # ===== MODEL FALLBACK CHAIN =====
    reply = None

    reply = await call_model_api(active_model, messages, max_tokens)

    if not reply:
        reply = await call_model_api("mistral", messages, max_tokens)

    if not reply:
        reply = await call_model_api("groq", messages, max_tokens)

    if not reply:
        print("⚠️ ALL MODELS FAILED")
        return random.choice(FALLBACK_RESPONSES), is_code

    # ===== SAVE MEMORY =====
    new_history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": reply}
    ]

    if len(new_history) > MAX_HISTORY * 2:
        new_history = new_history[-MAX_HISTORY*2:]

    chatbot_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"history": new_history}},
        upsert=True
    )

    return reply, is_code


# ================= MESSAGE HANDLER =================

async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message
    if not msg or not msg.text:
        return

    text = msg.text.strip()

    await context.bot.send_chat_action(
        chat_id=msg.chat.id,
        action=ChatAction.TYPING
    )

    doc = chatbot_collection.find_one({"chat_id": msg.chat.id})
    pref_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL

    reply, is_code = await get_ai_response(
        msg.chat.id,
        text,
        msg.from_user.first_name,
        pref_model
    )

    if is_code:
        await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
    else:
        await msg.reply_text(stylize_text(reply))
