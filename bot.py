import math
import os
import traceback
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PAGE_SIZE = 6
DELETE_AFTER = 300  # 5分钟

# ── 数据 ──────────────────────────────────────────
merchants = {
    "food": [
        {"name": "🏮 老北京中餐厅",     "contact": "类别: 🍜 中餐（川菜、粤菜）\n⭐ 埃里温最知名中餐厅，2009年创立\n📍地址: 9 Tumanyan St\n📞电话: +37491527822"},
        {"name": "🐉 Dragon Garden",    "contact": "类别: 🍜 中餐、日料、泰餐\n⭐ 埃里温最热闹的亚洲餐厅之一\n📍地址: 76 Arami St\n📞联系: @dragongarden_yerevan"},
        {"name": "🥡 Made in China",    "contact": "类别: 🍜 中式快餐（炒饭、炒面、炒锅）\n⭐ 埃里温第一家中式快餐店，价格实惠\n📍地址: 19/37 Tumanyan St\n📞联系: @madeinchina_am"},
        {"name": "🍱 Beijing Restaurant","contact": "类别: 🍜 中餐（川菜为主）\n⭐ 提供外卖服务，份量大价格实惠\n📍地址: 5 Nalbandyan St\n📞联系: @beijing_yerevan"},
        {"name": "🐼 Dragon Express",   "contact": "类别: 🍜 中式快餐、炒饭、炒面\n⭐ Yerevan Mall内，方便购物后用餐\n📍地址: Yerevan Mall, Tigran Mets Ave\n📞联系: @dragonexpress_ym"},
        {"name": "🍣 Suteki Sushi & Wok","contact": "类别: 🍱 寿司、中式炒锅\n⭐ Glovo评分100%，口碑极佳\n📍地址: 15 Abovyan St\n📞联系: @suteki_yerevan"},
        {"name": "🎋 IKIGAI",           "contact": "类别: 🍱 日料、中餐、亚洲融合菜\n⭐ Glovo评分99%，环境优雅\n📍地址: 10 Sayat-Nova Ave\n📞联系: @ikigai_yerevan"},
        {"name": "🍙 Murakami City",    "contact": "类别: 🍱 日式料理、寿司、拉面\n⭐ 人气很高的日料餐厅\n📍地址: 7 Mashtots Ave\n📞联系: @murakami_yerevan"},
        {"name": "🥢 Ako Sushi",        "contact": "类别: 🍱 寿司、中式面条、汤类\n⭐ 提供外卖，性价比高\n📍地址: 6 Martiros Saryan St\n📞联系: @akosushi_yerevan"},
        {"name": "🌿 Wine Republic",    "contact": "类别: 🍜 泰餐、中餐、印度菜\n⭐ 同时提供大量亚美尼亚葡萄酒\n📍地址: 12 Saryan St\n📞联系: @winerepublic_am"},
        {"name": "🍤 Wok Story",        "contact": "类别: 🍜 中式炒锅、亚洲街头美食\n⭐ 价格实惠，适合日常用餐\n📍地址: 3 Pushkin St\n📞联系: @wokstory_yerevan"},
        {"name": "🍗 Panda Kitchen",    "contact": "类别: 🍜 中式家常菜、煲汤、炒菜\n⭐ 口味正宗，适合想念家乡菜的华人\n📍地址: 22 Aram St\n📞联系: @pandakitchen_am"},
        {"name": "🥟 Dumpling House",   "contact": "类别: 🥟 饺子、包子、馄饨\n⭐ 专注北方面食，手工制作\n📍地址: 8 Paronyan St\n📞联系: @dumplinghouse_yv"},
        {"name": "🍲 Sichuan House",    "contact": "类别: 🌶 正宗川菜、麻辣火锅\n⭐ 口味偏辣，适合川菜爱好者\n📍地址: 14 Tigran Mets Ave\n📞联系: @sichuanhouse_am"},
        {"name": "🍜 Noodle Bar",       "contact": "类别: 🍜 各式亚洲面条（拉面、米线、河粉）\n⭐ 快捷便利，午餐热门选择\n📍地址: 33 Abovyan St\n📞联系: @noodlebar_yv"},
        {"name": "🫕 Hot Pot Garden",   "contact": "类别: 🍲 中式火锅（清汤/麻辣锅底）\n⭐ 适合多人聚餐\n📍地址: 18 Northern Ave\n📞联系: @hotpot_yerevan"},
        {"name": "🌏 Asia Fusion",      "contact": "类别: 🍱 亚洲融合菜（中/日/泰）\n⭐ 菜品多样，环境舒适\n📍地址: 25 Baghramyan Ave\n📞联系: @asiafusion_am"},
        {"name": "🍛 Canton Express",   "contact": "类别: 🍜 粤菜、点心、早茶\n⭐ 提供正宗广式早茶\n📍地址: 11 Vazgen Sargsyan St\n📞联系: @canton_yerevan"},
        {"name": "🥗 Green Bamboo",     "contact": "类别: 🥦 健康中式素食\n⭐ 素食友好，提供外卖\n📍地址: 4 Moskovyan St\n📞联系: @greenbamboo_am"},
        {"name": "🦞 Seafood Palace",   "contact": "类别: 🦐 中式海鲜料理\n⭐ 专注海鲜，适合商务宴请\n📍地址: 2 Republic Square\n📞联系: @seafoodpalace_yv"},
    ],
    "shop": [
        {"name": "🛍️ 购物中心City",    "contact": "类别: 综合超市，食品、日用品、家居用品\n📍地址: Yerevan City Supermarket, 14 Abovyan St"},
        {"name": "🛍️ SAS连锁超市",     "contact": "类别: 🥩 新鲜食品：肉类、海鲜、水果蔬菜\n🧀 乳制品、面包、零食\n🍷 酒水（进口比较多）\n🧴 日用品、护肤品\n🍱 现做熟食、沙拉、快餐区\n📍地址: 19 Amiryan St"},
        {"name": "🛍️ 家乐福大型超市",  "contact": "类别: 🍖 生鲜（肉类、蔬菜、水果）\n🧀 奶制品、熟食\n🍺 酒水（进口很多）\n🍫 零食、饮料\n🧴 日用品、家居用品\n📍地址: 48/2 Northern Ave"},
        {"name": "🛍️ 诺尔连锁超市",    "contact": "类别: 🥩 生鲜：肉类、蔬菜、水果\n🥖 面包、乳制品\n🍫 零食、饮料\n🍺 酒水\n🧴 日用品\n📍地址: 7 Nalbandyan St"},
        {"name": "🛍️ Bravo小型超市",   "contact": "类别: 🥖 面包、牛奶、基础食品\n🍫 零食、饮料\n🍺 酒水\n🧴 日用品\n👉 主打：方便、就近购买\n📍地址: 55 Abovyan St"},
        {"name": "🛍️ Megamall购物",    "contact": "类别: 👕 服装店（男装/女装/童装）\n👟 鞋店\n👜 包包/配饰\n📍地址: 26/1 Mashtots Ave"},
        {"name": "🪑 IKEA家具城",       "contact": "类别: 💺 家具、家居用品\n📍地址: Tigran Mets Ave 43"},
        {"name": "🪑 Viva家具城",       "contact": "类别: 📺 电视、音响\n❄️ 冰箱、洗衣机、空调\n🍳 厨房电器\n🔌 小家电\n📍地址: 20 Tumanyan St"},
        {"name": "💻 ZOOD电子商品",     "contact": "类别: 📱 手机、平板\n💻 笔记本电脑\n🎧 耳机、数码配件\n📍地址: 2 Sayat-Nova Ave"},
        {"name": "🏬 Dalma商场",        "contact": "类别: 埃里温最经典的大型购物中心+娱乐综合体之一\n📍地址: Tsitsernakaberd Highway 3"},
        {"name": "👔 Mall商场",         "contact": "类别: 👕 男装/女装/童装\n👟 鞋子/包包/配饰\n💄 部分美妆品牌\n100+品牌店\n📍地址: 48/2 Northern Ave"},
        {"name": "📺 Market家具市场",   "contact": "类别: 各类家具批发，沙发、床、衣柜、办公家具\n价格相对便宜，可议价\n📍地址: Tigran Mets Ave, Yerevan"},
        {"name": "📺 诺尔诺克家具",     "contact": "类别: 木质家具、餐桌椅、床、书柜\n可直接从制造商拿货\n📍地址: Nor Nork 区，Erebuni Rd 附近"},
        {"name": "📺 塞巴斯蒂亚家具城", "contact": "类别: 办公家具、沙发、床垫、床架\n较多大型批发商\n📍地址: Malatia-Sebastia 区"},
    ],
    "express": [
        {"name": "📦 顺丰代收", "contact": "微信: sf001"},
        {"name": "📫 韵达站点", "contact": "微信: yd002"},
        {"name": "🚚 极兔驿站", "contact": "微信: jitu003"},
    ],
    "tools": [
        {"name": "🗺 地图导航", "contact": "👉 maps.google.com"},
        {"name": "💱 汇率换算", "contact": "👉 xe.com"},
        {"name": "🌤 天气查询", "contact": "👉 weather.com"},
        {"name": "📝 在线翻译", "contact": "👉 translate.google.com"},
    ],
    "game": [
        {"name": "🎰 娱乐城A", "contact": "联系: @gameA"},
        {"name": "🎮 游戏厅B", "contact": "联系: @gameB"},
        {"name": "🎲 棋牌室C", "contact": "联系: @gameC"},
        {"name": "🃏 扑克群D",  "contact": "联系: @gameD"},
    ],
}

CAT_TITLE = {
    "food":    "🍜 美食餐厅",
    "shop":    "🛍️ 购物百货",
    "express": "📦 快递包裹",
    "tools":   "🛠 实用工具",
    "game":    "🎮 休闲娱乐",
}

# ── 定时删除 ───────────────────────────────────────
async def _do_delete(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=context.job.data["chat_id"],
            message_id=context.job.data["message_id"]
        )
    except Exception:
        pass

def schedule_delete(context, chat_id, message_id):
    context.job_queue.run_once(
        _do_delete,
        when=DELETE_AFTER,
        data={"chat_id": chat_id, "message_id": message_id}
    )

def is_group_chat(chat) -> bool:
    return chat.type in ("group", "supergroup")

async def safe_edit(query, text, reply_markup=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

# ── 键盘构建 ───────────────────────────────────────
def reply_menu():
    return ReplyKeyboardMarkup([
        ["🍜 美食餐厅", "🛍️ 购物百货"],
        ["📦 快递包裹", "🛠 实用工具"],
        ["🎮 休闲娱乐", "💬 群组交流"],
        ["📢 免费商家入驻"],
    ], resize_keyboard=True)

def merchant_keyboard(category: str, page: int) -> InlineKeyboardMarkup:
    items = merchants.get(category, [])
    total_pages = max(1, math.ceil(len(items) / PAGE_SIZE))
    page = page % total_pages
    start = page * PAGE_SIZE
    page_items = items[start:start + PAGE_SIZE]

    keyboard = []
    for row_start in range(0, len(page_items), 2):
        row = []
        for local_i in range(row_start, min(row_start + 2, len(page_items))):
            global_idx = start + local_i
            row.append(InlineKeyboardButton(
                page_items[local_i]["name"],
                callback_data=f"M:{category}:{global_idx}"
            ))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            f"🔄 换一批 ({page + 1}/{total_pages})",
            callback_data=f"C:{category}:{page + 1}"
        ),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ])
    return InlineKeyboardMarkup(keyboard)

def detail_keyboard(category: str, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 返回列表", callback_data=f"C:{category}:{page}"),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ]])

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🍜 美食餐厅", callback_data="C:food:0"),
            InlineKeyboardButton("🛍️ 购物百货", callback_data="C:shop:0"),
        ],
        [
            InlineKeyboardButton("📦 快递包裹", callback_data="C:express:0"),
            InlineKeyboardButton("🛠 实用工具", callback_data="C:tools:0"),
        ],
        [
            InlineKeyboardButton("🎮 休闲娱乐", callback_data="C:game:0"),
            InlineKeyboardButton("💬 群组交流", callback_data="group"),
        ],
        [
            InlineKeyboardButton("📢 免费商家入驻", callback_data="join"),
        ],
    ])

# ── /start ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "📢 功能导航，请选择👇",
        reply_markup=reply_menu()
    )
    if is_group_chat(update.effective_chat):
        schedule_delete(context, msg.chat_id, msg.message_id)

# ── 底部键盘处理 ───────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    category_map = {
        "🍜 美食餐厅": "food",
        "🛍️ 购物百货": "shop",
        "📦 快递包裹": "express",
        "🛠 实用工具": "tools",
        "🎮 休闲娱乐": "game",
    }
    if text in category_map:
        cat = category_map[text]
        msg = await update.message.reply_text(
            f"{CAT_TITLE[cat]}，点击查看详情👇",
            reply_markup=merchant_keyboard(cat, 0)
        )
        if is_group_chat(update.effective_chat):
            schedule_delete(context, msg.chat_id, msg.message_id)
    elif text == "💬 群组交流":
        msg = await update.message.reply_text("👉 亚美尼亚华人交流群：@Armenia202688")
        if is_group_chat(update.effective_chat):
            schedule_delete(context, msg.chat_id, msg.message_id)
    elif text == "📢 免费商家入驻":
        msg = await update.message.reply_text("👉 联系管理员：@Rich3988")
        if is_group_chat(update.effective_chat):
            schedule_delete(context, msg.chat_id, msg.message_id)

# ── Inline 按钮回调 ────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat = query.message.chat

    try:
        if data == "main":
            await query.answer()
            await safe_edit(query, "📢 请选择分类👇", reply_markup=main_menu_keyboard())
            if is_group_chat(chat):
                schedule_delete(context, chat.id, query.message.message_id)
            return

        if data == "group":
            await query.answer()
            await safe_edit(query, "👉 亚美尼亚华人交流群：@Armenia202688",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 主菜单", callback_data="main")
                ]]))
            if is_group_chat(chat):
                schedule_delete(context, chat.id, query.message.message_id)
            return

        if data == "join":
            await query.answer()
            await safe_edit(query, "👉 联系管理员：@Rich3988",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 主菜单", callback_data="main")
                ]]))
            if is_group_chat(chat):
                schedule_delete(context, chat.id, query.message.message_id)
            return

        parts = data.split(":", 2)

        if parts[0] == "C" and len(parts) == 3:
            _, category, page_str = parts
            page = int(page_str)
            items = merchants.get(category, [])
            title = CAT_TITLE.get(category, category)
            await query.answer()
            if not items:
                await safe_edit(query, f"{title}\n\n暂无内容，敬请期待！",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 返回", callback_data="main")
                    ]]))
            else:
                await safe_edit(query, f"{title}，点击查看详情👇",
                    reply_markup=merchant_keyboard(category, page))
            if is_group_chat(chat):
                schedule_delete(context, chat.id, query.message.message_id)
            return

        if parts[0] == "M" and len(parts) == 3:
            _, category, idx_str = parts
            idx = int(idx_str)
            items = merchants.get(category, [])
            if idx >= len(items):
                await query.answer("该信息不存在", show_alert=True)
                return
            merchant = items[idx]
            page = idx // PAGE_SIZE
            title = CAT_TITLE.get(category, category)
            await query.answer()
            await safe_edit(
                query,
                f"📋 {merchant['name']}\n\n"
                f"🔎 详情：\n{merchant['contact']}\n\n"
                f"来自 {title}",
                reply_markup=detail_keyboard(category, page)
            )
            if is_group_chat(chat):
                schedule_delete(context, chat.id, query.message.message_id)
            return

        await query.answer("未知操作", show_alert=True)

    except Exception as e:
        print(f"[ERROR] {traceback.format_exc()}")
        try:
            await query.answer(f"出错: {e}", show_alert=True)
        except Exception:
            pass

# ── 启动 ───────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ 机器人启动成功")
    app.run_polling()

if __name__ == "__main__":
    main()
