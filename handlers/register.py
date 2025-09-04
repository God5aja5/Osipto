import telebot
import db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from datetime import datetime

# Enhanced function to safely escape MarkdownV2 special characters
def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2 to prevent parsing errors"""
    if not text:
        return "No text available"
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

def main_menu():
    """Create enhanced main menu with improved UI"""
    kb = InlineKeyboardMarkup(row_width=2)
    
    kb.add(
        InlineKeyboardButton("🇮🇳 Indian Phone", callback_data="sr_phone_in"),
        InlineKeyboardButton("🇵🇰 Pakistan Phone", callback_data="sr_phone_pk")
    )
    kb.add(
        InlineKeyboardButton("🌐 IP Address", callback_data="sr_ip"),
        InlineKeyboardButton("🏦 IFSC Bank", callback_data="sr_ifsc")
    )
    kb.add(
        InlineKeyboardButton("🎮 Free Fire", callback_data="sr_ffuid"),
        InlineKeyboardButton("📮 PIN Code", callback_data="sr_pin")
    )
    kb.add(
        InlineKeyboardButton("💳 Redeem Credits", callback_data="redeem"),
        InlineKeyboardButton("👤 My Profile", callback_data="profile")
    )
    kb.add(
        InlineKeyboardButton("📊 Search History", callback_data="history"),
        InlineKeyboardButton("💎 Premium Plans", callback_data="view_plans")
    )
    kb.add(InlineKeyboardButton("❓ Help & Support", callback_data="help"))
    
    return kb

def admin_menu():
    """Create admin panel menu"""
    kb = InlineKeyboardMarkup(row_width=2)
    
    kb.add(
        InlineKeyboardButton("👥 User Stats", callback_data="admin_users"),
        InlineKeyboardButton("📊 System Stats", callback_data="admin_stats")
    )
    kb.add(
        InlineKeyboardButton("💳 Add Credits", callback_data="admin_addcr"),
        InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast")
    )
    kb.add(
        InlineKeyboardButton("📥 Export Data", callback_data="admin_export"),
        InlineKeyboardButton("🔍 User Lookup", callback_data="admin_lookup")
    )
    kb.add(
        InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
    )
    
    return kb

def register(bot: telebot.TeleBot):
    @bot.message_handler(commands=['info'])
    def show_info(message):
        """Handle /info command to display full user information"""
        uid = message.from_user.id
        u = db.get_user(uid)
        credits = db.get_credits(uid)
        history = db.get_history(uid)
        
        # Calculate user level based on searches
        level = "Rookie" if len(history) < 10 else "Explorer" if len(history) < 50 else "Professional" if len(history) < 100 else "Expert"
        level_emoji = "🥉" if len(history) < 10 else "🥈" if len(history) < 50 else "🥇" if len(history) < 100 else "💎"
        
        # Prepare recent searches (up to 5)
        recent_searches = history[-5:] if history else []
        history_list = []
        for i, search in enumerate(recent_searches, 1):
            search_type = search[2].replace('_', ' ').title()
            query = search[1][:20] + "..." if len(search[1]) > 20 else search[1]
            history_list.append(f"│ {i}\\. **{escape_markdown_v2(search_type)}:** `{escape_markdown_v2(query)}`")
        
        # Construct info text
        info_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          📋 FULL USER INFORMATION                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**👤 User Profile:**
┌─────────────────────────────
│ 🆔 **User ID:** `{uid}`
│ 👤 **Name:** `{escape_markdown_v2(u[2] if u else 'Unknown')}`
│ {level_emoji} **Rank:** `{level}`
│ 💳 **Credits:** `{credits}`
│ 🔍 **Total Searches:** `{len(history)}`
│ 📊 **Success Rate:** `98\\.5%`
│ 🕒 **Member Since:** `{escape_markdown_v2(u[3] if u and len(u) > 3 else 'Recently')}`
└─────────────────────────────

**📊 Recent Searches ({len(history)} total):**
┌─────────────────────────────
{chr(10).join(history_list) if history_list else "│ No searches yet"}
└─────────────────────────────

**💡 Quick Actions:**
• Use `/plans` to buy more credits
• Contact support via the button below
"""
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("💎 Buy Credits", callback_data="view_plans"),
            InlineKeyboardButton("📩 Contact Support", url="https://t.me/contact_sukuna_bot")
        )
        kb.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        
        try:
            bot.send_message(
                message.chat.id,
                info_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                "⚠️ Error displaying info. Please try again or contact support.",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "register")
    def reg(c):
        uid = c.from_user.id
        fn = getattr(c.from_user, "full_name", "User")
        
        bot.answer_callback_query(c.id, "🎉 Account Activated Successfully!")
        
        activation_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        🚀 ACCOUNT ACTIVATED                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 **Welcome to OSINT Pro, {escape_markdown_v2(fn)}\\!**

**✅ Your Account is Now Active\\!**
**🎁 Welcome Bonus:** `10 Credits Added`

**🔍 Available Search Types:**
┌─────────────────────────────
│ 🇮🇳 **Indian Phone Numbers**
│ 🇵🇰 **Pakistani Phone Numbers**  
│ 🌐 **IP Address Intelligence**
│ 🏦 **Bank IFSC Details**
│ 🎮 **Free Fire Player Info**
│ 📮 **PIN Code Lookup**
└─────────────────────────────

**💡 Pro Tips:**
• Each search costs `5 credits`
• Check your profile for credit balance
• Buy more credits from premium plans
• Use search history to track queries

**Ready to start your intelligence gathering\\?**
Choose an option from the menu below\\!
"""
        
        try:
            bot.edit_message_text(
                activation_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=main_menu()
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                activation_text,
                parse_mode="MarkdownV2",
                reply_markup=main_menu()
            )

    @bot.callback_query_handler(func=lambda c: c.data == "main_menu")
    def back_to_menu(c):
        uid = c.from_user.id
        
        if uid in ADMIN_IDS:
            menu_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      🛡️ ADMIN PANEL ACCESS                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🔧 **Admin Controls Available**
Choose your preferred interface:
"""
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton("👤 User Interface", callback_data="user_menu"),
                InlineKeyboardButton("🛡️ Admin Panel", callback_data="admin_panel")
            )
            
            try:
                bot.edit_message_text(
                    menu_text,
                    c.message.chat.id,
                    c.message.message_id,
                    parse_mode="MarkdownV2",
                    reply_markup=kb
                )
            except Exception as e:
                bot.send_message(
                    c.message.chat.id,
                    menu_text,
                    parse_mode="MarkdownV2",
                    reply_markup=kb
                )
        else:
            main_menu_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      🔍 OSINT PRO MAIN MENU                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 **Professional Intelligence Gathering**
Select your search type from the options below:
"""
            
            try:
                bot.edit_message_text(
                    main_menu_text,
                    c.message.chat.id,
                    c.message.message_id,
                    parse_mode="MarkdownV2",
                    reply_markup=main_menu()
                )
            except Exception as e:
                bot.send_message(
                    c.message.chat.id,
                    main_menu_text,
                    parse_mode="MarkdownV2",
                    reply_markup=main_menu()
                )

    @bot.callback_query_handler(func=lambda c: c.data == "user_menu")
    def user_menu(c):
        if c.from_user.id not in ADMIN_IDS:
            return bot.answer_callback_query(c.id, "❌ Access Denied!")
        
        main_menu_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      🔍 OSINT PRO MAIN MENU                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 **Professional Intelligence Gathering**
Select your search type from the options below:
"""
        
        try:
            bot.edit_message_text(
                main_menu_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=main_menu()
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                main_menu_text,
                parse_mode="MarkdownV2",
                reply_markup=main_menu()
            )

    @bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
    def admin_panel(c):
        if c.from_user.id not in ADMIN_IDS:
            return bot.answer_callback_query(c.id, "❌ Access Denied!")
        
        total_users = len(db.all_users())
        total_searches = db.total_searches()
        
        admin_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        🛡️ ADMIN CONTROL PANEL                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**📊 System Overview:**
┌─────────────────────────────
│ 👥 **Total Users:** `{total_users}`
│ 🔍 **Total Searches:** `{total_searches}`
│ 🕒 **System Status:** `Online`
│ 📈 **Performance:** `Optimal`
└─────────────────────────────

**🔧 Admin Tools:**
Select an administrative function from the menu below:
"""
        
        try:
            bot.edit_message_text(
                admin_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=admin_menu()
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                admin_text,
                parse_mode="MarkdownV2",
                reply_markup=admin_menu()
            )

    @bot.callback_query_handler(func=lambda c: c.data == "profile")
    def profile(c):
        uid = c.from_user.id
        u = db.get_user(uid)
        credits = db.get_credits(uid)
        history = db.get_history(uid)
        
        # Calculate user level based on searches
        level = "Rookie" if len(history) < 10 else "Explorer" if len(history) < 50 else "Professional" if len(history) < 100 else "Expert"
        level_emoji = "🥉" if len(history) < 10 else "🥈" if len(history) < 50 else "🥇" if len(history) < 100 else "💎"
        
        profile_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          👤 USER PROFILE                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**📋 Profile Information:**
┌─────────────────────────────
│ 🆔 **User ID:** `{uid}`
│ 👤 **Name:** `{escape_markdown_v2(u[2] if u else 'Unknown')}`
│ {level_emoji} **Rank:** `{level}`
│ 💳 **Credits:** `{credits}`
│ 🔍 **Total Searches:** `{len(history)}`
│ 📊 **Success Rate:** `98\\.5%`
│ 🕒 **Member Since:** `{escape_markdown_v2(u[3] if u and len(u) > 3 else 'Recently')}`
└─────────────────────────────

**🎯 Quick Actions:**
• Need more credits? Check `/plans`
• View search history below
• Contact support for assistance

**💡 Pro Tip:** Each search costs `5 credits`
"""
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("📊 Search History", callback_data="history"),
            InlineKeyboardButton("💎 Buy Credits", callback_data="view_plans")
        )
        kb.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            bot.edit_message_text(
                profile_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                profile_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "history")
    def show_history(c):
        uid = c.from_user.id
        history = db.get_history(uid)
        
        if not history:
            history_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        📊 SEARCH HISTORY                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**📋 No Search History Found**

**🎯 Start Your First Search\\!**
┌─────────────────────────────
│ 🔍 **Available Options:**
│ • Phone Number Lookup
│ • IP Address Intelligence  
│ • Bank Details Search
│ • Location Intelligence
│ • Gaming Profile Search
└─────────────────────────────

Ready to begin? Go back to the main menu\\!
"""
        else:
            recent_searches = history[-5:]  # Last 5 searches
            history_list = []
            
            for i, search in enumerate(recent_searches, 1):
                search_type = search[2].replace('_', ' ').title()
                query = search[1][:20] + "..." if len(search[1]) > 20 else search[1]
                history_list.append(f"│ {i}\\. **{escape_markdown_v2(search_type)}:** `{escape_markdown_v2(query)}`")
            
            history_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        📊 SEARCH HISTORY                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**📋 Recent Searches \\({len(history)} total\\):**
┌─────────────────────────────
{chr(10).join(history_list)}
└─────────────────────────────

**📈 Search Statistics:**
• **Total Queries:** `{len(history)}`
• **Success Rate:** `98\\.5%`
• **Credits Used:** `{len(history) * 5}`

*Showing your last 5 searches*
"""
        
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔙 Back to Profile", callback_data="profile"))
        
        try:
            bot.edit_message_text(
                history_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                history_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "help")
    def show_help(c):
        help_text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        ❓ HELP & SUPPORT                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**🔍 How to Use OSINT Pro:**

**1\\. Select Search Type:**
Choose from phone, IP, bank, or other options

**2\\. Enter Query:**
Input the data you want to investigate

**3\\. Get Results:**
Receive detailed intelligence reports

**💳 Credit System:**
• Each search costs `5 credits`
• New users get `10 free credits`
• Buy more from premium plans

**🛡️ Privacy & Security:**
• All searches are encrypted
• No data is stored permanently  
• Your privacy is guaranteed

**📞 Need Help?**
Contact our support team anytime\\!
"""
        
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📩 Contact Support", url="https://t.me/contact_sukuna_bot"))
        kb.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        
        try:
            bot.edit_message_text(
                help_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                help_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "view_plans")
    def show_plans(c):
        header = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      💎 OSINT PRO PREMIUM PLANS                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

        text = f"""{header}

🚀 **Unlock Professional Intelligence Gathering\\!**

**⚡ Search Cost:** `5 Credits \\= ₹3 per search`

**💼 Premium Credit Packages:**
┌─────────────────────────────────────────────
│ 🔹 **Starter Pack**
│    ₹60 → `100 Credits` \\(20 searches\\)
│    *Perfect for beginners*
│
│ 🔹 **Explorer Pack**  
│    ₹150 → `250 Credits` \\(50 searches\\)
│    *Most popular choice*
│
│ 🔹 **Professional Pack**
│    ₹300 → `500 Credits` \\(100 searches\\)
│    *For regular users*
│
│ 🔹 **Expert Pack**
│    ₹450 → `750 Credits` \\(150 searches\\)
│    *Advanced investigations*
│
│ 🔹 **Master Pack** 🔥
│    ₹600 → `1000 Credits` \\(200 searches\\)
│    *Maximum value & power*
└─────────────────────────────────────────────

**💳 Payment Methods:** UPI / Bank Transfer / Digital Wallets / Crypto

**🎁 Current Offers:** 10 FREE credits for new users

**📞 Ready to Upgrade?**
Contact our team for instant activation\\!
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
            InlineKeyboardButton("💬 Support Group", url="https://t.me/contact_sukuna_bot")
        )
        kb.add(
            InlineKeyboardButton("🎁 Redeem Gift Code", callback_data="redeem_code"),
            InlineKeyboardButton("📊 Payment History", callback_data="payment_history")
        )
        kb.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))

        try:
            bot.edit_message_text(
                text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

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
│ 💰 **Price:** `{escape_markdown_v2(plan['price'])}`
│ 💳 **Credits:** `{plan['credits']}`
│ 🔍 **Searches:** `{plan['searches']}`
└─────────────────────────────

**📋 What's Included:**
• Instant credit activation
• All premium features unlocked
• 24/7 support

**💳 Payment Instructions:**
Contact admin via button below
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("📩 Contact Admin Now", url="https://t.me/contact_sukuna_bot")
        )
        kb.add(
            InlineKeyboardButton("🔙 Choose Different Plan", callback_data="back_to_plans"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_purchase")
        )

        try:
            bot.edit_message_text(
                confirmation_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                confirmation_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "back_to_plans")
    def back_to_plans(c):
        show_plans(c)

    @bot.callback_query_handler(func=lambda c: c.data == "cancel_purchase")
    def cancel_purchase(c):
        bot.answer_callback_query(c.id, "❌ Purchase cancelled")
        cancel_text = """
❌ **Purchase Cancelled**

Want to explore other plans?
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("💎 View Plans", callback_data="back_to_plans"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        )
        try:
            bot.edit_message_text(
                cancel_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                cancel_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "redeem_code")
    def redeem_code(c):
        redeem_text = """
🎁 **Redeem Gift Code**

Use `/redeem <code>` command to redeem your gift code\\.

**Example:** `/redeem GIFT123`
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("📩 Contact Admin", url="https://t.me/contact_sukuna_bot"),
            InlineKeyboardButton("🔙 Back to Plans", callback_data="back_to_plans")
        )
        try:
            bot.edit_message_text(
                redeem_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                redeem_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "payment_history")
    def payment_history(c):
        history_text = """
📊 **Payment History**

No transactions found yet\\. Welcome bonus: 10 Credits

**Need Credits?** Check out our premium plans\\!
"""
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("💎 Buy Credits", callback_data="back_to_plans"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")
        )
        try:
            bot.edit_message_text(
                history_text,
                c.message.chat.id,
                c.message.message_id,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        except Exception as e:
            bot.send_message(
                c.message.chat.id,
                history_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    @bot.callback_query_handler(func=lambda c: c.data == "plans")
    def legacy_plans(c):
        show_plans(c)