import math
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
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
DELETE_AFTER = 300

merchants = {
    "food": [
        {"name": "🍜 张记面馆", "contact": "微信: zhangji001\n电话: 13800000001"},
        {"name": "🍱 李家快餐", "contact": "微信: lijia002\n电话: 13800000002"},
        {"name": "🍣 老王寿司", "contact": "微信: laowang003\n电话: 13800000003"},
        {"name": "🥘 陈记火锅", "contact": "微信: chenji004\n电话: 13800000004"},
        {"name": "🍕 小意餐厅", "contact": "微信: xiaoyi005\n电话: 13800000005"},
        {"name": "🥗 绿色沙拉", "contact": "微信: green006\n电话: 13800000006"},
        {"name": "🍔 汉堡工厂", "contact": "微信: burger007\n电话: 13800000007"},
        {"name": "🥟 饺子王",   "contact": "微信: jiaozi008\n电话: 13800000008"},
    ],
    "express": [
        {"name": "📦 顺丰代收", "contact": "微信: sf001"},
        {"name": "📫 韵达站点", "contact": "微信: yd002"},
        {"name": "🚚 极兔驿站", "contact": "微信: jitu003"},
    ],
    "tools": [
        {"name": "🗺 地图导航",  "contact": "👉 maps.google.com"},
        {"name": "💱 汇率换算",  "contact": "👉 xe.com"},
        {"name": "🌤 天气查询",  "contact": "👉 weather.com"},
        {"name": "📝 在线翻译",  "contact": "👉 translate.google.com"},
    ],
    "game": [
        {"name": "🎰 娱乐城A", "contact": "联系: @gameA"},
        {"name": "🎮 游戏厅B", "contact": "联系: @gameB"},
        {"name": "🎲 棋牌室C", "contact": "联系: @gameC"},
        {"name": "🃏 扑克群D",  "contact": "联系: @gameD"},
    ],
}

CAT_TITLE = {
    "food":    "🍔 美食大全",
    "express": "📦 快递包裹",
    "tools":   "🛠 实用工具",
    "game":    "🎮 休闲娱乐",
}

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

def is_group(update: Update) -> bool:
    return update.effective_chat.type in ("group", "supergroup")

def reply_menu():
    return ReplyKeyboardMarkup([
        ["🍔 美食大全", "💬 群组交流"],
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
    for i in range(0, len(page_items), 2):
        row = []
        for j, item in enumerate(page_items[i:i + 2]):
            global_idx = start + i + j
            cb = f"M|{category}|{global_idx}"
            print(f"[BUILD] button: {item['name']} -> callback_data={cb}")
            row.append(InlineKeyboardButton(item["name"], callback_data=cb))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            f"🔄 换一批 ({page + 1}/{total_pages})",
            callback_data=f"C|{category}|{page + 1}"
        ),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ])
    return InlineKeyboardMarkup(keyboard)

def detail_keyboard(category: str, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 返回列表", callback_data=f"C|{category}|{page}"),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[START] triggered")
    msg = await update.message.reply_text("📢 功能导航，请选择👇", reply_markup=reply_menu())
    if is_group(update):
        schedule_delete(context, msg.chat_id, msg.message_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"[MSG] received: {text}")

    category_map = {
        "🍔 美食大全": "food",
        "📦 快递包裹": "express",
        "🛠 实用工具": "tools",
        "🎮 休闲娱乐": "game",
    }

    if text in category_map:
        cat = category_map[text]
        title = CAT_TITLE[cat]
        msg = await update.message.reply_text(
            f"{title}，点击查看联系方式👇",
            reply_markup=merchant_keyboard(cat, 0)
        )
        if is_group(update):
            schedule_delete(context, msg.chat_id, msg.message_id)

    elif text == "💬 群组交流":
        msg = await update.message.reply_text("👉 群组入口：@yourgroup")
        if is_group(update):
            schedule_delete(context, msg.chat_id, msg.message_id)

    elif text == "📢 免费商家入驻":
        msg = await update.message.reply_text("👉 联系管理员：@admin")
        if is_group(update):
            schedule_delete(context, msg.chat_id, msg.message_id)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(f"[CALLBACK] raw data: '{query.data}'")

    try:
        await query.answer()
    except Exception as e:
        print(f"[CALLBACK] answer() error: {e}")

    data = query.data

    if data == "main":
        print("[CALLBACK] -> main menu")
        await query.edit_message_text(
            "📢 请选择分类👇",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🍔 美食大全", callback_data="C|food|0"),
                    InlineKeyboardButton("📦 快递包裹", callback_data="C|express|0"),
                ],
                [
                    InlineKeyboardButton("🛠 实用工具", callback_data="C|tools|0"),
                    InlineKeyboardButton("🎮 休闲娱乐", callback_data="C|game|0"),
                ],
            ])
        )
        return

    if data.startswith("C|"):
        parts = data.split("|")
        print(f"[CALLBACK] -> category list, parts={parts}")
        _, category, page_str = parts
        page = int(page_str)
        title = CAT_TITLE.get(category, category)
        items = merchants.get(category, [])
        if not items:
            await query.edit_message_text(f"{title}\n\n暂无内容！")
            return
        await query.edit_message_text(
            f"{title}，点击查看联系方式👇",
            reply_markup=merchant_keyboard(category, page)
        )
        return

    if data.startswith("M|"):
        parts = data.split("|")
        print(f"[CALLBACK] -> merchant detail, parts={parts}")
        _, category, idx_str = parts
        idx = int(idx_str)
        items = merchants.get(category, [])
        print(f"[CALLBACK] category={category}, idx={idx}, total={len(items)}")

        if idx >= len(items):
            print(f"[CALLBACK] ERROR: idx out of range")
            await query.answer("该商家信息不存在", show_alert=True)
            return

        merchant = items[idx]
        page = idx // PAGE_SIZE
        title = CAT_TITLE.get(category, category)
        print(f"[CALLBACK] showing merchant: {merchant['name']}")

        try:
            await query.edit_message_text(
                f"📋 {merchant['name']}\n\n"
                f"📞 联系方式：\n{merchant['contact']}\n\n"
                f"来自 {title}",
                reply_markup=detail_keyboard(category, page)
            )
            print(f"[CALLBACK] edit_message_text SUCCESS")
        except Exception as e:
            print(f"[CALLBACK] edit_message_text FAILED: {e}")
        return

    print(f"[CALLBACK] UNHANDLED data: {data}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ 机器人启动成功")
    app.run_polling()

if __name__ == "__main__":
    main()
