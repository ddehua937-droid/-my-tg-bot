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
        {"name": "💱 汇率换算", "contact": "👉 xe.com"},
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

# ── 安全 edit ──────────────────────────────────────
async def safe_edit(query, text, reply_markup=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

# ── 键盘构建 ───────────────────────────────────────
def reply_menu():
    return ReplyKeyboardMarkup([
        ["🛍️ 购物百货", "💬 群组交流"],
        ["📦 快递包裹", "🛠 实用工具"],
        ["🎮 休闲娱乐", "📢 免费商家入驻"],
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
            InlineKeyboardButton("🛍️ 购物百货", callback_data="C:shop:0"),
            InlineKeyboardButton("📦 快递包裹", callback_data="C:express:0"),
        ],
        [
            InlineKeyboardButton("🛠 实用工具", callback_data="C:tools:0"),
            InlineKeyboardButton("🎮 休闲娱乐", callback_data="C:game:0"),
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
            # 群组里重新注册删除（消息ID不变，刷新计时）
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
                await safe_edit(
                    query,
                    f"{title}\n\n暂无内容，敬请期待！",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 返回", callback_data="main")
                    ]])
                )
            else:
                await safe_edit(
                    query,
                    f"{title}，点击查看详情👇",
                    reply_markup=merchant_keyboard(category, page)
                )
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
