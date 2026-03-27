import json
import math
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

# ── 配置 ─────────────────────────
BOT_TOKEN = "8702263955:AAHp4awcmEeNtnE7119ujPrPlvFv4oWMTEo"
PAGE_SIZE = 6

# ── 数据 ─────────────────────────
merchants = {
    "food": [
        {"name": "🍜 张记面馆", "contact": "微信: zhangji001\n电话: 13800000001"},
        {"name": "🍱 李家快餐", "contact": "微信: lijia002\n电话: 13800000002"},
        {"name": "🍣 老王寿司", "contact": "微信: laowang003\n电话: 13800000003"},
        {"name": "🥘 陈记火锅", "contact": "微信: chenji004\n电话: 13800000004"},
        {"name": "🍕 小意餐厅", "contact": "微信: xiaoyi005\n电话: 13800000005"},
        {"name": "🥗 绿色沙拉", "contact": "微信: green006\n电话: 13800000006"},
        {"name": "🍔 汉堡工厂", "contact": "微信: burger007\n电话: 13800000007"},
        {"name": "🥟 饺子王", "contact": "微信: jiaozi008\n电话: 13800000008"},
    ],
    "express": [
        {"name": "📦 顺丰代收", "contact": "微信: sf001"},
        {"name": "📫 韵达站点", "contact": "微信: yd002"},
        {"name": "🚚 极兔驿站", "contact": "微信: jitu003"},
    ]
}

# ── 底部菜单（重点）────────────────
def reply_menu():
    keyboard = [
        ["🍔 美食大全", "💬 群组交流"],
        ["📦 快递包裹", "🛠 实用工具"],
        ["🎮 休闲娱乐"],
        ["📢 免费商家入驻"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ── 商家列表按钮 ─────────────────
def merchant_keyboard(category, page):
    items = merchants.get(category, [])
    total_pages = max(1, math.ceil(len(items) / PAGE_SIZE))
    page = page % total_pages

    start = page * PAGE_SIZE
    page_items = items[start:start + PAGE_SIZE]

    keyboard = []

    for i in range(0, len(page_items), 2):
        row = []
        for j, item in enumerate(page_items[i:i+2]):
            idx = start + i + j
            row.append(
                InlineKeyboardButton(
                    item["name"],
                    callback_data=f"merchant:{category}:{idx}"
                )
            )
        keyboard.append(row)

    # 换一批 + 返回
    keyboard.append([
        InlineKeyboardButton("🔄 换一批", callback_data=f"cat:{category}:{page+1}"),
        InlineKeyboardButton("🏠 主菜单", callback_data="main")
    ])

    return InlineKeyboardMarkup(keyboard)

# ── 商家详情按钮 ─────────────────
def detail_keyboard(category, page):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 返回", callback_data=f"cat:{category}:{page}"),
            InlineKeyboardButton("🏠 主菜单", callback_data="main")
        ]
    ])

# ── start ───────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 功能导航，请选择👇",
        reply_markup=reply_menu()
    )

# ── 处理底部按钮 ─────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🍔 美食大全":
        await update.message.reply_text(
            "🍔 美食推荐👇",
            reply_markup=merchant_keyboard("food", 0)
        )

    elif text == "📦 快递包裹":
        await update.message.reply_text(
            "📦 快递服务👇",
            reply_markup=merchant_keyboard("express", 0)
        )

    elif text == "💬 群组交流":
        await update.message.reply_text("👉 群组入口：@yourgroup")

    elif text == "🛠 实用工具":
        await update.message.reply_text("👉 工具合集：xxx.com")

    elif text == "🎮 休闲娱乐":
        await update.message.reply_text("👉 娱乐频道：@xxx")

    elif text == "📢 免费商家入驻":
        await update.message.reply_text("👉 联系管理员：@admin")

# ── 按钮处理 ────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main":
        await query.message.reply_text(
            "📢 功能导航👇",
            reply_markup=reply_menu()
        )
        return

    if data.startswith("cat:"):
        _, category, page = data.split(":")
        page = int(page)

        await query.edit_message_text(
            "👇 点击商家查看",
            reply_markup=merchant_keyboard(category, page)
        )

    elif data.startswith("merchant:"):
        _, category, idx = data.split(":")
        idx = int(idx)
        items = merchants.get(category, [])

        if idx >= len(items):
            return

        page = idx // PAGE_SIZE
        m = items[idx]

        await query.edit_message_text(
            f"📋 {m['name']}\n\n{m['contact']}",
            reply_markup=detail_keyboard(category, page)
        )

# ── 启动 ───────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("机器人启动成功")
    app.run_polling()

if __name__ == "__main__":
    main()
