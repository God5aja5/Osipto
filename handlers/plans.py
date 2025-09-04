# handlers/plans.py
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def register(bot: telebot.TeleBot):

    # Custom MarkdownV2 escape
    def escape_markdown_v2(text):
        escape_chars = r"\_*[]()~`>#+-=|{}.!"
        for c in escape_chars:
            text = text.replace(c, f"\\{c}")
        return text

    # Safe edit message to avoid errors
    def safe_edit_message(c, text, kb):
        escaped_text = escape_markdown_v2(text)
        try:
            if c.message.text != escaped_text or c.message.reply_markup != kb:
                bot.edit_message_text(
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    text=escaped_text,
                    parse_mode="MarkdownV2",
                    reply_markup=kb
                )
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(c.message.chat.id, escaped_text, parse_mode="MarkdownV2", reply_markup=kb)

    @bot.message_handler(commands=["plans"])
    def send_plans(m: Message):
        header = """┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      💎 OSINT PRO PREMIUM PLANS                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""
        
        text = f"""{header}

🚀 **Unlock Professional Intelligence Gathering!**

**⚡ Search Cost:** `5 Credits = ₹3 per search`

**💼 Premium Credit Packages:**
┌─────────────────────────────
│ 🔹 Starter Pack ₹60 → `100 Credits` (20 searches)
│ 🔹 Explorer Pack ₹150 → `250 Credits` (50 searches)
│ 🔹 Professional Pack ₹300 → `500 Credits` (100 searches)
│ 🔹 Expert Pack ₹450 → `750 Credits` (150 searches)
│ 🔹 Master Pack ₹600 → `1000 Credits` (200 searches)
└─────────────────────────────
"""
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🔹 ₹60 - 100 Credits", callback_data="plan_60"),
            InlineKeyboardButton("🔹 ₹150 - 250 Credits", callback_data="plan_150")
        )
        kb.add(
            InlineKeyboardButton("🔹 ₹300 - 500 Credits", callback_data="plan_300"),
            InlineKeyboardButton("🔹 ₹450 - 750 Credits", callback_data="plan_450")
        )
        kb.add(
            InlineKeyboardButton("🔥 ₹600 - 1000 Credits", callback_data="plan_600")
        )
        kb.add(
            InlineKeyboardButton("📩 Contact Admin", url="https://t.me/contact_sukuna_bot"),
            InlineKeyboardButton("💬 Support Group", url="https://t.me/SILENT_IS_HERE")
        )
        kb.add(
            InlineKeyboardButton("🎁 Redeem Gift Code", callback_data="redeem_code"),
            InlineKeyboardButton("📊 Payment History", callback_data="payment_history")
        )

        bot.send_message(m.chat.id, escape_markdown_v2(text), parse_mode="MarkdownV2", reply_markup=kb)

    # Plan selection handlers
    @bot.callback_query_handler(func=lambda c: c.data.startswith("plan_"))
    def handle_plan_selection(c):
        plan_data = {
            "plan_60": {"price": "₹60", "credits": "100", "searches": "20"},
            "plan_150": {"price": "₹150", "credits": "250", "searches": "50"},
            "plan_300": {"price": "₹300", "credits": "500", "searches": "100"},
            "plan_450": {"price": "₹450", "credits": "750", "searches": "150"},
            "plan_600": {"price": "₹600", "credits": "1000", "searches": "200"}
        }
        
        plan = plan_data.get(c.data)
        if not plan:
            return bot.answer_callback_query(c.id, "❌ Invalid plan selected")
        
        confirmation_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        💳 PLAN CONFIRMATION                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**🎯 Selected Plan Details:**
┌─────────────────────────────
│ 💰 **Price:** `{plan['price']}`
│ 💳 **Credits:** `{plan['credits']}`
│ 🔍 **Searches:** `{plan['searches']}`
│ ⚡ **Per Search:** `₹3`
│ 🎁 **Validity:** `Lifetime`
└─────────────────────────────

**📋 What's Included:**
• Instant credit activation
• All premium features unlocked
• 24/7 customer support
• Data export capabilities
• Priority processing

**💳 Payment Instructions:**
1\\. Contact admin using button below
2\\. Share your User ID: `{c.from_user.id}`
3\\. Make payment via UPI/Bank Transfer
4\\. Credits will be added instantly

**🔒 100% Secure Transaction Guaranteed**

Ready to proceed with this plan?
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("📩 Contact Admin Now", url="https://t.me/contact_sukuna_bot")
        )
        kb.add(
            InlineKeyboardButton("🔙 Choose Different Plan", callback_data="back_to_plans"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_purchase")
        )

        safe_edit_message(c, confirmation_text, kb)

    @bot.callback_query_handler(func=lambda c: c.data == "back_to_plans")
    def back_to_plans(c):
        send_plans(c.message)

    @bot.callback_query_handler(func=lambda c: c.data == "cancel_purchase")
    def cancel_purchase(c):
        bot.answer_callback_query(c.id, "❌ Purchase cancelled")
        
        cancel_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        ❌ PURCHASE CANCELLED                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**Purchase has been cancelled\\.**

**🎯 Still need credits?**
• Check our flexible plans anytime
• Contact support for custom packages
• Use referral program for bonus credits

**💡 Remember:** Each search costs only `5 credits`

Want to explore other options?
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("💎 View Plans", callback_data="back_to_plans"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        )
        safe_edit_message(c, cancel_text, kb)

    @bot.callback_query_handler(func=lambda c: c.data == "redeem_code")
    def redeem_code(c):
        redeem_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        🎁 REDEEM GIFT CODE                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**🎯 How to Redeem Gift Codes:**

**📝 Steps:**
1\\. Get your gift code from admin/promotion
2\\. Use `/redeem <your_code>` command
3\\. Credits will be added automatically

**💡 Gift Code Types:**
• Welcome bonus codes
• Promotional offers
• Referral rewards
• Contest prizes

**🔍 Need a Gift Code?**
Contact admin or participate in our promotions!
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("📩 Contact Admin", url="https://t.me/contact_sukuna_bot"),
            InlineKeyboardButton("🔙 Back to Plans", callback_data="back_to_plans")
        )
        safe_edit_message(c, redeem_text, kb)

    @bot.callback_query_handler(func=lambda c: c.data == "payment_history")
    def payment_history(c):
        history_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                       📊 PAYMENT HISTORY                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**💳 Your Transaction History:**

**📋 Recent Transactions:**
┌─────────────────────────────
│ 📅 **No transactions found**
│ 
│ 🎁 **Welcome Bonus:** `10 Credits`
│ 📅 **Date:** Account creation
│ ✅ **Status:** Completed
└─────────────────────────────

**📊 Summary:**
• **Total Purchased:** `₹0`
• **Total Credits:** `10` (Welcome bonus)
• **Credits Used:** `0`
• **Balance:** `10 Credits`

**💡 Ready to make your first purchase?**
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("💎 Buy Credits", callback_data="back_to_plans"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")
        )
        safe_edit_message(c, history_text, kb)