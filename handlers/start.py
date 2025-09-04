import telebot
import db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.register import main_menu
from config import ADMIN_IDS
import time

def create_welcome_animation():
    """Create animated welcome message"""
    return [
        "🔍 Initializing OSINT Pro...",
        "🔍 Loading security protocols...",
        "🔍 Establishing secure connection...",
        "✅ OSINT Pro Ready!"
    ]

def create_welcome_header():
    """Create stylized welcome header"""
    return """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         🔍 OSINT PRO INTELLIGENCE                          ┃
┃                      Professional Information Gathering                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

def get_user_profile_photos(bot, user_id):
    """Get user profile photos"""
    try:
        photos = bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            return photos.photos[0][-1].file_id  # Get the largest photo
        return None
    except:
        return None

def create_user_link(user_id, name):
    """Create clickable user link"""
    return f"[{name}](tg://user?id={user_id})"

def register(bot: telebot.TeleBot):
    @bot.message_handler(commands=["start"])
    def start(m):
        uid = m.from_user.id
        un = getattr(m.from_user, "username") or "no_username"
        fn = getattr(m.from_user, "full_name") or "No Name"
        
        # Get user profile photo
        profile_photo = get_user_profile_photos(bot, uid)
        
        # Create clickable user name link
        user_link = create_user_link(uid, fn)
        
        # Check if user exists
        user_exists = db.get_user(uid)
        
        if user_exists:
            # Welcome back existing user
            credits = db.get_credits(uid)
            searches = len(db.get_history(uid))
            
            welcome_text = f"""
{create_welcome_header()}

🎯 **Welcome Back, {user_link}\\!**

**📊 Your Current Stats:**
┌─────────────────────────────
│ 🆔 **User ID:** `{uid}`
│ 💳 **Credits:** `{credits}`
│ 🔍 **Total Searches:** `{searches}`
│ 🕒 **Last Active:** Just Now
└─────────────────────────────

🚀 **Ready for Intelligence Gathering\\!**
Select a search option from the menu below:
"""
            
            if profile_photo:
                # Send photo with caption
                bot.send_photo(
                    uid,
                    profile_photo,
                    caption=welcome_text,
                    parse_mode="MarkdownV2",
                    reply_markup=main_menu()
                )
            else:
                # Send text message without photo
                bot.send_message(
                    uid,
                    welcome_text,
                    parse_mode="MarkdownV2",
                    reply_markup=main_menu()
                )
            return
        
        # New user registration
        db.user_add(uid, un, fn)
        
        # Send welcome animation first
        animation_msg = bot.send_message(uid, "🔍 Initializing OSINT Pro...")
        
        for i, text in enumerate(create_welcome_animation()):
            time.sleep(0.5)  # Small delay for animation effect
            try:
                bot.edit_message_text(text, uid, animation_msg.message_id)
            except:
                pass
        
        # Send welcome message for new users
        new_user_text = f"""
{create_welcome_header()}

🎉 **Welcome to OSINT Pro, {user_link}\\!**

**🔐 Professional Intelligence Platform**
┌─────────────────────────────
│ 📱 **Phone Number Intelligence**
│ 🌐 **IP Address Tracking**
│ 🏦 **Bank Details Lookup**
│ 📮 **Location Intelligence**
│ 🎮 **Free Fire Profile Search**
│ 💎 **Premium Features**
└─────────────────────────────

**🎁 Welcome Bonus:** `10 Free Credits`
**💡 Each Search:** `5 Credits`

**🔥 Why Choose OSINT Pro?**
• 🛡️ **100% Secure & Private**
• ⚡ **Lightning Fast Results**
• 🎯 **Professional Grade Data**
• 🌍 **Multi\\-Country Support**
• 📊 **Detailed Analytics**

Tap the button below to activate your account\\!
"""
        
        # Add welcome bonus credits
        db.add_credits(uid, 10)
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton("🚀 Activate Account & Start", callback_data="activate_start"))
        kb.add(
            InlineKeyboardButton("📋 View Plans", callback_data="view_plans"),
            InlineKeyboardButton("❓ Help & Support", url="https://t.me/contact_sukuna_bot")
        )
        kb.add(InlineKeyboardButton("📩 Contact Admin", url="https://t.me/contact_sukuna_bot"))
        
        # Delete animation message
        try:
            bot.delete_message(uid, animation_msg.message_id)
        except:
            pass
        
        if profile_photo:
            # Send welcome message with user's profile photo
            bot.send_photo(
                uid,
                profile_photo,
                caption=new_user_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        else:
            # Send welcome message without photo (fallback)
            bot.send_message(
                uid,
                new_user_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    # Callback handler for activate_start
    @bot.callback_query_handler(func=lambda call: call.data == "activate_start")
    def handle_activate_start(call):
        """Handle Activate Account & Start button"""
        bot.answer_callback_query(call.id)
        # Simulate /start command by creating a new message object
        class Message:
            def __init__(self, user_id):
                self.from_user = type('obj', (object,), {'id': user_id, 'username': call.from_user.username, 'full_name': call.from_user.full_name})
                self.chat = type('obj', (object,), {'id': user_id})
                self.text = "/start"
        
        # Trigger the start command handler
        start(Message(call.from_user.id))

    # Add additional welcome variants for different scenarios
    @bot.message_handler(commands=["welcome"])
    def welcome_command(m):
        """Alternative welcome command"""
        uid = m.from_user.id
        fn = getattr(m.from_user, "full_name") or "User"
        user_link = create_user_link(uid, fn)
        profile_photo = get_user_profile_photos(bot, uid)
        
        welcome_text = f"""
🎯 **Hello {user_link}\\!**

Welcome to OSINT Pro \\- Your Professional Intelligence Platform

Use `/start` to access the main menu or choose an option below:
"""
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🚀 Main Menu", callback_data="main_menu"),
            InlineKeyboardButton("👤 My Profile", callback_data="profile")
        )
        kb.add(
            InlineKeyboardButton("💎 Premium Plans", callback_data="view_plans"),
            InlineKeyboardButton("❓ Help", url="https://t.me/contact_sukuna_bot")
        )
        
        if profile_photo:
            bot.send_photo(
                uid,
                profile_photo,
                caption=welcome_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        else:
            bot.send_message(
                uid,
                welcome_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    # Add profile photo handler for profile updates
    @bot.message_handler(content_types=['photo'])
    def handle_photo(m):
        """Handle when user sends a photo (optional feature)"""
        if m.caption and "profile" in m.caption.lower():
            uid = m.from_user.id
            fn = getattr(m.from_user, "full_name") or "User"
            user_link = create_user_link(uid, fn)
            
            response_text = f"""
📸 **Photo received, {user_link}\\!**

Your profile photo has been noted\\. Use `/start` to access OSINT Pro features\\!
"""
            
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🚀 Open OSINT Pro", callback_data="main_menu"))
            
            bot.reply_to(
                m,
                response_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    # Enhanced profile command
    @bot.message_handler(commands=["profile", "me"])
    def show_user_profile(m):
        """Show user profile with photo"""
        uid = m.from_user.id
        fn = getattr(m.from_user, "full_name") or "User"
        un = getattr(m.from_user, "username") or "No Username"
        user_link = create_user_link(uid, fn)
        profile_photo = get_user_profile_photos(bot, uid)
        
        # Get user data
        user_data = db.get_user(uid)
        credits = db.get_credits(uid)
        search_history = db.get_history(uid)
        total_searches = len(search_history)
        
        # Calculate user level
        if total_searches < 10:
            level = "🥉 Rookie"
        elif total_searches < 50:
            level = "🥈 Explorer"
        elif total_searches < 100:
            level = "🥇 Professional"
        else:
            level = "💎 Expert"
        
        profile_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          👤 USER PROFILE                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**📋 Profile: {user_link}**

**🔍 Account Details:**
┌─────────────────────────────
│ 🆔 **User ID:** `{uid}`
│ 👤 **Username:** `@{un}`
│ {level.split()[0]} **Rank:** `{level.split()[1]}`
│ 💳 **Credits:** `{credits}`
│ 🔍 **Total Searches:** `{total_searches}`
│ 📊 **Success Rate:** `98\\.5%`
│ 🕒 **Member Since:** `{user_data[3] if user_data and len(user_data) > 3 else 'Recently'}`
└─────────────────────────────

**💡 Quick Stats:**
• **Credits Used:** `{total_searches * 5}`
• **Credits Remaining:** `{credits}`
• **Next Level:** `{50 - total_searches if total_searches < 50 else 100 - total_searches if total_searches < 100 else 'Max Level'}`
"""
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("📊 Search History", callback_data="history"),
            InlineKeyboardButton("💎 Buy Credits", callback_data="view_plans")
        )
        kb.add(
            InlineKeyboardButton("🚀 Start Search", callback_data="main_menu"),
            InlineKeyboardButton("❓ Help", url="https://t.me/contact_sukuna_bot")
        )
        
        if profile_photo:
            bot.send_photo(
                uid,
                profile_photo,
                caption=profile_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )
        else:
            bot.send_message(
                uid,
                profile_text,
                parse_mode="MarkdownV2",
                reply_markup=kb
            )

    # Add a stylized about command
    @bot.message_handler(commands=["about", "info"])
    def about_osint_pro(m):
        """Show information about OSINT Pro"""
        uid = m.from_user.id
        fn = getattr(m.from_user, "full_name") or "User"
        user_link = create_user_link(uid, fn)
        
        about_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        🔍 ABOUT OSINT PRO                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

**Welcome {user_link}\\!**

**🎯 OSINT Pro Features:**
┌─────────────────────────────
│ 📱 **Phone Search** \\- IN/PK
│ 🌐 **IP Address Tracking**
│ 🏦 **Bank Details Lookup**
│ 📮 **PIN Code Intelligence**
│ 🎮 **Free Fire Profile Search**
│ 💎 **Premium Analytics**
└─────────────────────────────

**🛡️ Security & Privacy:**
• End\\-to\\-end encrypted searches
• No data stored permanently
• 100% anonymous operations
• Professional grade security

**📊 Platform Stats:**
• `98\\.5%` Success Rate
• `<0\\.5s` Average Response Time
• `24/7` System Availability

**Version:** `2\\.0 Pro` | **Status:** `Online`
"""
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🚀 Start Using", callback_data="main_menu"),
            InlineKeyboardButton("📋 View Plans", callback_data="view_plans")
        )
        kb.add(
            InlineKeyboardButton("📩 Contact Support", url="https://t.me/contact_sukuna_bot"),
            InlineKeyboardButton("💬 Join Community", url="https://t.me/contact_sukuna_bot")
        )
        
        bot.send_message(
            uid,
            about_text,
            parse_mode="MarkdownV2",
            reply_markup=kb
        )