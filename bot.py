import math
import os
import traceback
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InputMediaPhoto
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
DELETE_AFTER = 300

merchants = {
    "food": [
        {"name": "🍽️ Mao",              "image": "https://your-image-url.com/bali.jpg",       "contact": "类别: 亚洲融合料理（中餐、寿司、点心、泰餐）\n⭐ 评分极高，环境精致\n🕐 营业时间: 12:00–00:00\n📍地址: 28 Isahakyan St, Yerevan\n📞电话: +374 55 001001\n📱Instagram: @maoyerevan"},
        {"name": "🌴 Little Bali",       "image": "https://your-image-url.com/bali.jpg",      "contact": "类别: 正宗印尼/巴厘岛料理\n⭐ 印尼厨师主理，口味地道\n🕐 营业时间: 12:00–22:00\n📍地址: Tamanyan St 1, Yerevan\n📞电话: +374 330 08009\n📱Instagram: @littlebali.am"},
        {"name": "🍖 Katsin Restaurant", "image": "https://your-image-url.com/katsin.jpg",    "contact": "类别: 海鲜、肉类料理（现代风格）\n⭐ 跳舞侍者+现场表演，气氛热烈\n🕐 营业时间: 12:00–01:00（表演从20:00开始）\n📍地址: 4/6 Amiryan St, Yerevan\n📞电话: +374 77 881001\n📱Instagram: @katsinyerevan"},
        {"name": "🍜 Ramen-Ten",         "image": "https://your-image-url.com/ramen.jpg",     "contact": "类别: 正宗日式拉面\n⭐ 埃里温最受好评的拉面专门店\n🕐 营业时间: 待确认\n📍地址: 2/5 Abovyan St, Yerevan\n📞电话: +374 95 223311\n📱Facebook: Ramen Ten Yerevan"},
        {"name": "🍵 Phobo",             "image": "https://your-image-url.com/phobo.jpg",     "contact": "类别: 正宗越南料理（河粉、春卷、米粉）\n⭐ 埃里温首家越南餐厅，越南厨师主理\n🕐 营业时间: 周一至周四/周日 11:00–22:00，周五至周六 11:00–23:00\n📍地址: 71 Hanrapetutyan St, Yerevan\n📞电话: +374 77 085599\n📱Instagram: @phobo.am"},
        {"name": "🏮 老北京中餐厅",      "image": "https://your-image-url.com/laobj.jpg",     "contact": "类别: 🍜 中餐（川菜、粤菜，200+菜品）\n⭐ 埃里温最知名中餐厅，2009年创立\n🕐 营业时间: 12:00–00:00\n📍地址: 9 Tumanyan St, Yerevan\n📞电话: +374 91 527822"},
        {"name": "🐉 Dragon Garden",     "image": "https://your-image-url.com/dragon.jpg",    "contact": "类别: 🍜 中餐、日料、泰餐\n⭐ 埃里温最热闹的亚洲餐厅之一\n📍地址: 76 Arami St, Yerevan\n📞联系: @dragongarden_yerevan"},
        {"name": "🥡 Made in China",     "image": "https://your-image-url.com/mic.jpg",       "contact": "类别: 🍜 中式快餐（炒饭、炒面、炒锅）\n⭐ 埃里温第一家中式快餐店，价格实惠\n📍地址: 19/37 Tumanyan St, Yerevan\n📞联系: @madeinchina_am"},
        {"name": "🍱 Beijing Restaurant","image": "https://your-image-url.com/beijing.jpg",   "contact": "类别: 🍜 中餐（川菜为主）\n⭐ 提供外卖，份量大价格实惠\n📍地址: 5 Nalbandyan St, Yerevan"},
        {"name": "🍣 Suteki Sushi & Wok","image": "https://your-image-url.com/suteki.jpg",    "contact": "类别: 🍱 寿司、中式炒锅\n⭐ Glovo评分100%\n📍地址: 15 Abovyan St, Yerevan"},
        {"name": "🎋 IKIGAI",            "image": "https://your-image-url.com/ikigai.jpg",    "contact": "类别: 🍱 日料、中餐、亚洲融合菜\n⭐ Glovo评分99%，环境优雅\n📍地址: 10 Sayat-Nova Ave, Yerevan"},
        {"name": "🍙 Murakami City",     "image": "https://your-image-url.com/murakami.jpg",  "contact": "类别: 🍱 日式料理、寿司、拉面\n📍地址: 7 Mashtots Ave, Yerevan"},
        {"name": "🥢 Ako Sushi",         "image": "https://your-image-url.com/ako.jpg",       "contact": "类别: 🍱 寿司、中式面条\n📍地址: 6 Martiros Saryan St, Yerevan"},
        {"name": "🌿 Wine Republic",     "image": "https://your-image-url.com/wine.jpg",      "contact": "类别: 🍜 泰餐、中餐、印度菜 + 亚美尼亚葡萄酒\n📍地址: 12 Saryan St, Yerevan"},
        {"name": "🍤 Wok Story",         "image": "https://your-image-url.com/wok.jpg",       "contact": "类别: 🍜 中式炒锅、亚洲街头美食\n📍地址: 3 Pushkin St, Yerevan"},
        {"name": "🍗 Panda Kitchen",     "image": "https://your-image-url.com/panda.jpg",     "contact": "类别: 🍜 中式家常菜、煲汤\n📍地址: 22 Aram St, Yerevan"},
        {"name": "🥟 Dumpling House",    "image": "https://your-image-url.com/dumpling.jpg",  "contact": "类别: 🥟 饺子、包子、馄饨\n📍地址: 8 Paronyan St, Yerevan"},
        {"name": "🍲 Sichuan House",     "image": "https://your-image-url.com/sichuan.jpg",   "contact": "类别: 🌶 正宗川菜、麻辣火锅\n📍地址: 14 Tigran Mets Ave, Yerevan"},
        {"name": "🫕 Hot Pot Garden",    "image": "https://your-image-url.com/hotpot.jpg",    "contact": "类别: 🍲 中式火锅（清汤/麻辣）\n📍地址: 18 Northern Ave, Yerevan"},
        {"name": "🌏 Asia Fusion",       "image": "https://your-image-url.com/asia.jpg",      "contact": "类别: 🍱 亚洲融合菜（中/日/泰）\n📍地址: 25 Baghramyan Ave, Yerevan"},
    ],
    "shop": [
        {"name": "🛍️ 购物中心City",    "image": "", "contact": "类别: 综合超市，食品、日用品、家居\n📍地址: 14 Abovyan St, Yerevan"},
        {"name": "🛍️ SAS连锁超市",     "image": "", "contact": "类别: 🥩 生鲜、乳制品、日用品\n📍地址: 19 Amiryan St, Yerevan"},
        {"name": "🛍️ 家乐福大型超市",  "image": "", "contact": "类别: 🍖 生鲜、酒水、日用品\n📍地址: 48/2 Northern Ave, Yerevan"},
        {"name": "🛍️ 诺尔连锁超市",    "image": "", "contact": "类别: 🥩 生鲜、面包、零食\n📍地址: 7 Nalbandyan St, Yerevan"},
        {"name": "🛍️ Bravo小型超市",   "image": "", "contact": "类别: 🥖 面包、牛奶、基础食品\n📍地址: 55 Abovyan St, Yerevan"},
        {"name": "🛍️ Megamall购物",    "image": "", "contact": "类别: 👕 服装、鞋店、配饰\n📍地址: 26/1 Mashtots Ave, Yerevan"},
        {"name": "🪑 IKEA家具城",       "image": "", "contact": "类别: 💺 家具、家居用品\n📍地址: Tigran Mets Ave 43, Yerevan"},
        {"name": "🪑 Viva家具城",       "image": "", "contact": "类别: 📺 电视音响、大家电\n📍地址: 20 Tumanyan St, Yerevan"},
        {"name": "💻 ZOOD电子商品",     "image": "", "contact": "类别: 📱 手机平板、笔记本\n📍地址: 2 Sayat-Nova Ave, Yerevan"},
        {"name": "🏬 Dalma商场",        "image": "", "contact": "类别: 大型购物中心+娱乐综合体\n📍地址: Tsitsernakaberd Highway 3, Yerevan"},
        {"name": "👔 Mall商场",         "image": "", "contact": "类别: 👕 服装、美妆，100+品牌\n📍地址: 48/2 Northern Ave, Yerevan"},
        {"name": "📺 Market家具市场",   "image": "", "contact": "类别: 家具批发，价格便宜可议价\n📍地址: Tigran Mets Ave, Yerevan"},
        {"name": "📺 诺尔诺克家具",     "image": "", "contact": "类别: 木质家具，可从制造商拿货\n📍地址: Nor Nork 区，Erebuni Rd 附近"},
        {"name": "📺 塞巴斯蒂亚家具城", "image": "", "contact": "类别: 办公家具、沙发、床垫\n📍地址: Malatia-Sebastia 区, Yerevan"},
    ],
    "express": [
        {"name": "📦 顺丰代收", "image": "", "contact": "微信: sf001"},
        {"name": "📫 韵达站点", "image": "", "contact": "微信: yd002"},
        {"name": "🚚 极兔驿站", "image": "", "contact": "微信: jitu003"},
    ],
    "tools": [
        {"name": "🗺 地图导航", "image": "", "contact": "👉 maps.google.com"},
        {"name": "💱 汇率换算", "image": "", "contact": "👉 xe.com"},
        {"name": "🌤 天气查询", "image": "", "contact": "👉 weather.com"},
        {"name": "📝 在线翻译", "image": "", "contact": "👉 translate.google.com"},
    ],
    "game": [
        {"name": "🍺 Dargett精酿啤酒", "image": "", "contact": "类别: 精酿啤酒吧，20+种自酿啤酒\n⭐ 埃里温第一家精酿啤酒厂\n🕐 营业时间: 12:00–01:00\n📍地址: 70/1 Aram St, Yerevan\n📞电话: +374 10 544400"},
        {"name": "🍸 Epicure鸡尾酒吧", "image": "", "contact": "类别: 创意鸡尾酒吧，有户外露台\n⭐ 埃里温最受欢迎鸡尾酒吧之一\n🕐 营业时间: 11:00–02:00\n📍地址: Pushkin St, Yerevan"},
        {"name": "🎵 Calumet民族酒吧", "image": "", "contact": "类别: 民族风情酒吧，世界音乐+现场乐队\n⭐ 旅行者最爱，氛围独特\n🕐 营业时间: 18:00–02:00\n📍地址: 56a Pushkin St, Yerevan\n📞电话: +374 99 881173"},
        {"name": "📚 Hemingway's酒吧", "image": "", "contact": "类别: 文艺复古酒吧（书籍+黑胶+鸡尾酒）\n⭐ 标语"Alcohol & Books"，文艺范儿\n🕐 营业时间: 12:00–02:00\n📍地址: 1a Tamanyan St, Yerevan\n📞电话: +374 98 349882"},
        {"name": "🎶 Club 12爵士吧",   "image": "", "contact": "类别: 高档爵士俱乐部，海鲜+肉类料理\n⭐ 氛围优雅，法式乡村风格装修\n🕐 营业时间: 20:00–03:00\n📍地址: 28 Isahakyan St, Yerevan\n📞电话: +374 10 524211"},
        {"name": "🌃 El Sky Bar屋顶吧", "image": "", "contact": "类别: 顶楼酒吧，俯瞰埃里温全景\n⭐ DJ表演+特色鸡尾酒，奢华体验\n🕐 营业时间: 18:00–03:00\n📍地址: 市中心高层建筑顶楼, Yerevan"},
        {"name": "🎸 Simona酒吧",      "image": "", "contact": "类别: 复古潜水吧，70-80年代音乐\n⭐ 最佳鸡尾酒之一，深夜继续派对首选\n🕐 营业时间: 20:00–04:00\n📍地址: 市中心, Yerevan"},
        {"name": "🎤 Kami Club夜店",    "image": "", "contact": "类别: 高端夜店，国际DJ+现场演出\n⭐ 埃里温最顶级夜店体验\n🕐 营业时间: 22:00–05:00\n📍地址: 市中心, Yerevan"},
        {"name": "🍷 1320社区酒吧",     "image": "", "contact": "类别: 复古社区酒吧，自制烈酒+特色鸡尾酒\n⭐ 旅行者必打卡，地道亚美尼亚体验\n🕐 营业时间: 17:00–01:00\n📍地址: 市中心历史建筑内, Yerevan"},
        {"name": "🎹 Minas鸡尾酒室",   "image": "", "contact": "类别: 精品鸡尾酒吧，艺术家氛围\n⭐ 以亚美尼亚画家Minas命名，艺术装饰\n🕐 营业时间: 12:00–02:00\n📍地址: Pushkin St附近, Yerevan"},
    ],
}

CAT_TITLE = {
    "food":    "🍜 美食餐厅",
    "shop":    "🛍️ 购物百货",
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

def is_group_chat(chat) -> bool:
    return chat.type in ("group", "supergroup")

def has_real_image(merchant):
    img = merchant.get("image", "")
    return img and not img.startswith("https://your-image-url")

def reply_menu():
    return ReplyKeyboardMarkup([
        ["🍜 美食餐厅", "🛍️ 购物百货"],
        ["📦 快递包裹", "🛠 实用工具"],
        ["🎮 休闲娱乐", "💬 群组交流"],
        ["📢 免费商家入驻"],
    ], resize_keyboard=True)

def merchant_keyboard(category, page):
    items = merchants.get(category, [])
    total_pages = max(1, math.ceil(len(items) / PAGE_SIZE))
    page = page % total_pages
    start = page * PAGE_SIZE
    page_items = items[start:start + PAGE_SIZE]
    keyboard = []
    for i in range(0, len(page_items), 2):
        row = []
        for j in range(i, min(i + 2, len(page_items))):
            row.append(InlineKeyboardButton(
                page_items[j]["name"],
                callback_data=f"M:{category}:{start + j}"
            ))
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton(f"🔄 换一批 ({page+1}/{total_pages})", callback_data=f"C:{category}:{page+1}"),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ])
    return InlineKeyboardMarkup(keyboard)

def detail_keyboard(category, page):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 返回列表", callback_data=f"C:{category}:{page}"),
        InlineKeyboardButton("🏠 主菜单", callback_data="main"),
    ]])

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍜 美食餐厅", callback_data="C:food:0"),
         InlineKeyboardButton("🛍️ 购物百货", callback_data="C:shop:0")],
        [InlineKeyboardButton("📦 快递包裹", callback_data="C:express:0"),
         InlineKeyboardButton("🛠 实用工具", callback_data="C:tools:0")],
        [InlineKeyboardButton("🎮 休闲娱乐", callback_data="C:game:0"),
         InlineKeyboardButton("💬 群组交流", callback_data="group")],
        [InlineKeyboardButton("📢 免费商家入驻", callback_data="join")],
    ])

async def send_or_edit(context, query, text, keyboard, image_url=None):
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    has_photo = bool(query.message.photo)

    if image_url:
        if has_photo:
            try:
                msg = await context.bot.edit_message_media(
                    chat_id=chat_id, message_id=message_id,
                    media=InputMediaPhoto(media=image_url, caption=text),
                    reply_markup=keyboard
                )
                return msg
            except Exception:
                pass
        try:
            await query.message.delete()
        except Exception:
            pass
        msg = await context.bot.send_photo(
            chat_id=chat_id, photo=image_url, caption=text, reply_markup=keyboard
        )
        return msg
    else:
        if has_photo:
            try:
                await query.message.delete()
            except Exception:
                pass
            msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
            return msg
        else:
            try:
                msg = await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard
                )
                return msg
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    return query.message
                raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("📢 功能导航，请选择👇", reply_markup=reply_menu())
    if is_group_chat(update.effective_chat):
        schedule_delete(context, msg.chat_id, msg.message_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    category_map = {
        "🍜 美食餐厅": "food", "🛍️ 购物百货": "shop",
        "📦 快递包裹": "express", "🛠 实用工具": "tools", "🎮 休闲娱乐": "game",
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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat = query.message.chat

    try:
        await query.answer()

        if data == "main":
            msg = await send_or_edit(context, query, "📢 请选择分类👇", main_menu_keyboard())
            if is_group_chat(chat):
                schedule_delete(context, chat.id, msg.message_id)
            return

        if data == "group":
            msg = await send_or_edit(context, query, "👉 亚美尼亚华人交流群：@Armenia202688",
                InlineKeyboardMarkup([[InlineKeyboardButton("🏠 主菜单", callback_data="main")]]))
            if is_group_chat(chat):
                schedule_delete(context, chat.id, msg.message_id)
            return

        if data == "join":
            msg = await send_or_edit(context, query, "👉 联系管理员：@Rich3988",
                InlineKeyboardMarkup([[InlineKeyboardButton("🏠 主菜单", callback_data="main")]]))
            if is_group_chat(chat):
                schedule_delete(context, chat.id, msg.message_id)
            return

        parts = data.split(":", 2)

        if parts[0] == "C" and len(parts) == 3:
            _, category, page_str = parts
            page = int(page_str)
            items = merchants.get(category, [])
            title = CAT_TITLE.get(category, category)
            if not items:
                msg = await send_or_edit(context, query, f"{title}\n\n暂无内容，敬请期待！",
                    InlineKeyboardMarkup([[InlineKeyboardButton("🔙 返回", callback_data="main")]]))
            else:
                msg = await send_or_edit(context, query, f"{title}，点击查看详情👇",
                    merchant_keyboard(category, page))
            if is_group_chat(chat):
                schedule_delete(context, chat.id, msg.message_id)
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
            text = f"📋 {merchant['name']}\n\n🔎 详情：\n{merchant['contact']}\n\n来自 {title}"
            image_url = merchant["image"] if has_real_image(merchant) else None
            msg = await send_or_edit(context, query, text, detail_keyboard(category, page), image_url)
            if is_group_chat(chat):
                schedule_delete(context, chat.id, msg.message_id)
            return

        await query.answer("未知操作", show_alert=True)

    except Exception as e:
        print(f"[ERROR] {traceback.format_exc()}")
        try:
            await query.answer(f"出错: {e}", show_alert=True)
        except Exception:
            pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ 机器人启动成功")
    app.run_polling()

if __name__ == "__main__":
    main()
