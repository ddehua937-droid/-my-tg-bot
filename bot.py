import json
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ── 配置 ──────────────────────────────────────────
BOT_TOKEN = "你的BOT_TOKEN"
PAGE_SIZE = 6  # 每页显示几个商家

# ── 商家数据（可以改成读取数据库）────────────────
merchants = {
    "food": [
        {"name": "🍜 张记面馆", "contact": "微信: zhangji001\n电话: 138-0000-0001\n地址: 幸福路1号"},
        {"name": "🍱 李家快餐", "contact": "微信: lijia002\n电话: 138-0000-0002\n地址: 解放路88号"},
        {"name": "🍣 老王寿司", "contact": "微信: laowang003\n电话: 138-0000-0003\n地址: 中山路5号"},
        {"name": "🥘 陈记火锅", "contact": "微信: chenji004\n电话: 138-0000-0004\n地址: 人民路22号"},
        {"name": "🍕 小意餐厅", "contact": "微信: xiaoyi005\n电话: 138-0000-0005\n地址: 新华路10号"},
        {"name": "🥗 绿色沙拉", "contact": "微信: green006\n电话: 138-0000-0006\n地址: 花园路3号"},
        {"name": "🍔 汉堡工厂", "contact": "微信: burger007\n电话: 138-0000-0007\n地址: 北京路15号"},
        {"name": "🥟 饺子王", "contact": "微信: jiaozi008\n电话: 138-0000-0008\n地址: 上海路8号"},
    ],
    "express": [
        {"name": "📦 顺丰代收", "contact": "微信: sf001\n电话: 139-0000-0001\n地址: 快递中心A区"},
        {"name": "📫 韵达站点", "contact": "微信: yd002\n电话: 139-0000-0002\n地址: 快递中心B区"},
        {"name": "🚚 极兔驿站", "contact": "微信: jitu003\n电话: 139-0000-0003\n地址: 快递中心C区"},
    ],
    "news": [
        {"name": "📰 本地快讯", "contact": "频道: @localnews\n更新: 每日8次"},
        {"name": "📡 科技日报", "contact": "频道: @techdaily\n更新: 每日5次"},
    ],
}

# ── 主菜单 ────────────────────────────────────────
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🍔 美食大全", callback_data="cat:food:0"),
            InlineKeyboardButton("💬 群组交流", callback_data="cat:group:0"),
        ],
        [
            InlineKeyboardButton("📦 快递包裹", callback_data="cat:express:0"),
            InlineKeyboardButton("🎮 休闲娱乐", callback_data="cat:game:0"),
        ],
        [
            InlineKeyboardButton("📰 新闻事件", callback_data="cat:news:0"),
            InlineKeyboardButton("📢 免费商家入驻", callback_data="join"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ── 商家列表键盘（分页）────────────────────────────
def merchant_list_keyboard(category: str, page: int):
    items = merchants.get(category, [])
    total_pages = max(1, math.ceil(len(items) / PAGE_SIZE))
    page = page % total_pages  # 循环翻页

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = items[start:end]

    keyboard = []
    # 商家按钮，每行2个
    for i in range(0, len(page_items), 2):
        row = []
        for item in page_items[i:i+2]:
            idx = start + page_items.index(item)
            row.append(InlineKeyboardButton(
                item["name"],
                callback_data=f"merchant:{category}:{idx}"
            ))
        keyboard.append(row)

    # 底部导航
    nav_row = []
    if total_pages > 1:
        next_page = (page + 1) % total_pages
        nav_row.append(InlineKeyboardButton(
            f"🔄 换一批 ({page+1}/{total_pages})",
            callback_data=f"cat:{category}:{next_page}"
        ))
    nav_row.append(InlineKeyboardButton("🔙 返回主菜单", callback_data="main"))
    keyboard.append(nav_row)

    return InlineKeyboardMarkup(keyboard)

# ── 商家详情键盘 ──────────────────────────────────
def merchant_detail_keyboard(category: str, page: int):
    keyboard = [[
        InlineKeyboardButton("🔙 返回列表", callback_data=f"cat:{category}:{page}"),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ]]
    return InlineKeyboardMarkup(keyboard)

# ── 分类名称映射 ──────────────────────────────────
CAT_NAMES = {
    "food": "🍔 美食大全",
    "express": "📦 快递包裹",
    "news": "📰 新闻事件",
    "group": "💬 群组交流",
    "game": "🎮 休闲娱乐",
}

# ── 命令处理 ──────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 欢迎使用本地生活服务Bot！\n请选择你感兴趣的分类：",
        reply_markup=main_menu_keyboard()
    )

# ── 按钮回调处理 ──────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 返回主菜单
    if data == "main":
        await query.edit_message_text(
            "👋 欢迎使用本地生活服务Bot！\n请选择你感兴趣的分类：",
            reply_markup=main_menu_keyboard()
        )

    # 商家入驻
    elif data == "join":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main")
        ]])
        await query.edit_message_text(
            "📢 *免费商家入驻*\n\n"
            "欢迎入驻本平台！\n"
            "请联系管理员：@admin\n"
            "或发送邮件至：admin@example.com",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    # 分类列表页
    elif data.startswith("cat:"):
        _, category, page_str = data.split(":")
        page = int(page_str)
        items = merchants.get(category, [])
        cat_name = CAT_NAMES.get(category, category)

        if not items:
            await query.edit_message_text(
                f"{cat_name}\n\n暂无商家信息，敬请期待！",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 返回主菜单", callback_data="main")
                ]])
            )
            return

        total = len(items)
        await query.edit_message_text(
            f"{cat_name}\n共 {total} 家商户，点击查看联系方式：",
            reply_markup=merchant_list_keyboard(category, page)
        )

    # 商家详情
    elif data.startswith("merchant:"):
        _, category, idx_str = data.split(":")
        idx = int(idx_str)
        page = idx // PAGE_SIZE
        items = merchants.get(category, [])

        if idx >= len(items):
            await query.answer("商家信息不存在", show_alert=True)
            return

        merchant = items[idx]
        cat_name = CAT_NAMES.get(category, category)

        await query.edit_message_text(
            f"📋 *{merchant['name']}*\n\n"
            f"📞 联系方式：\n{merchant['contact']}\n\n"
            f"_来自 {cat_name}_",
            parse_mode="Markdown",
            reply_markup=merchant_detail_keyboard(category, page)
        )

# ── 启动 ──────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot 启动中...")
    app.run_polling()

if __name__ == "__main__":
    main()
