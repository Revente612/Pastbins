import logging
import os
import psycopg2
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ID администратора
ADMIN_ID = 6422904023

# Токен бота
BOT_TOKEN = "8144499111:AAE-GWIYuutlUoeJPFVOs0En7HOh7S53dfM"

# Получение переменных окружения Railway
DATABASE_URL = os.environ.get('DATABASE_URL')

# Настройка базы данных
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            product TEXT,
            amount TEXT,
            screenshot TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Главное меню
def main_menu():
    keyboard = [
        [KeyboardButton("Купить"), KeyboardButton("Информация")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Меню покупки
def buy_menu():
    keyboard = [
        [InlineKeyboardButton("Fatality Client 1 месяц 50₽/0.5$", callback_data='buy_1month')],
        [InlineKeyboardButton("Fatality Client Beta навсегда - 199₽/2$", callback_data='buy_beta')],
        [InlineKeyboardButton("Fatality Client Навсегда 599₽/6$", callback_data='buy_forever')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Админ меню
def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📦 Управление заказами", callback_data='admin_orders')],
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Меню управления заказом
def order_management_menu(order_id):
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f'confirm_{order_id}'),
            InlineKeyboardButton("❌ Отклонить", callback_data=f'reject_{order_id}')
        ],
        [InlineKeyboardButton("⬅️ Назад", callback_data='admin_orders')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для отправки сообщения с фото и текстом
async def send_message_with_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode=None):
    try:
        with open('main.png', 'rb') as photo:
            if hasattr(update, 'message') and update.message:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            elif hasattr(update, 'callback_query') and update.callback_query:
                await context.bot.send_photo(
                    chat_id=update.callback_query.message.chat_id,
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
    except FileNotFoundError:
        logger.error("Файл main.png не найден!")
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        elif hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )

# Команда старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Здравствуйте 👋, вас приветствует Fatality Client 💞\n"
        "Хотите купить клиент? Нажмите кнопку ниже чтобы увидеть цены на подписку"
    )
    
    await send_message_with_photo(update, context, welcome_text, main_menu())

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Купить":
        buy_text = "Выберите тариф:"
        await send_message_with_photo(update, context, buy_text, buy_menu())
    
    elif text == "Информация":
        info_text = (
            "ℹ️ *Информация о Fatality Client*\n\n"
            "Fatality Client будет доступен 04.06.2026 ⚠️\n"
            "На данный момент идёт разработка ⏳"
        )
        await send_message_with_photo(update, context, info_text, main_menu(), ParseMode.MARKDOWN)
    
    else:
        # Для любых других сообщений отправляем основное меню с фото
        welcome_text = (
            "Здравствуйте 👋, вас приветствует Fatality Client 💞\n"
            "Хотите купить клиент? Нажмите кнопку ниже чтобы увидеть цены на подписку"
        )
        await send_message_with_photo(update, context, welcome_text, main_menu())

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user

    # Обработка кнопок покупки
    if data.startswith('buy_'):
        products = {
            'buy_1month': {'name': 'Fatality Client 1 месяц', 'price': '50₽/0.5$'},
            'buy_beta': {'name': 'Fatality Client Beta навсегда', 'price': '199₽/2$'},
            'buy_forever': {'name': 'Fatality Client Навсегда', 'price': '599₽/6$'}
        }
        
        product = products[data]
        instruction_text = (
            f"💳 *Оплата {product['name']}*\n\n"
            f"Стоимость: {product['price']}\n\n"
            f"📋 *Инструкция по оплате:*\n"
            f"1. Отправьте деньги пользователю @AttackSindrom\n"
            f"2. Пришлите скриншот с оплатой\n"
            f"3. Мы подтвердим вашу оплату в течение 24 часов\n\n"
            f"После оплаты отправьте скриншот в этот чат."
        )
        
        await send_message_with_photo(update, context, instruction_text, None, ParseMode.MARKDOWN)
        context.user_data['awaiting_payment'] = data
    
    # Админ панель
    elif data == 'admin_panel':
        if user.id != ADMIN_ID:
            await query.edit_message_text("⛔ У вас нет доступа к админ панели")
            return
        
        admin_text = "👨‍💼 *Админ панель*"
        try:
            with open('main.png', 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo,
                    caption=admin_text,
                    reply_markup=admin_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            await query.message.delete()
        except FileNotFoundError:
            await query.edit_message_text(
                admin_text,
                reply_markup=admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
    
    # Управление заказами
    elif data == 'admin_orders':
        if user.id != ADMIN_ID:
            return
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE status = %s ORDER BY created_at DESC', ('pending',))
        pending_orders = cursor.fetchall()
        conn.close()
        
        if not pending_orders:
            admin_text = "📦 *Ожидающие заказы*\n\nНет ожидающих заказов."
            try:
                with open('main.png', 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=admin_text,
                        reply_markup=admin_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                await query.message.delete()
            except FileNotFoundError:
                await query.edit_message_text(
                    admin_text,
                    reply_markup=admin_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            return
        
        order_text = "📦 *Ожидающие заказы:*\n\n"
        for order in pending_orders:
            order_id, user_id, username, product, amount, screenshot, status, created_at = order
            order_text += f"🆔 Заказ #{order_id}\n"
            order_text += f"👤 Пользователь: @{username or 'N/A'} (ID: {user_id})\n"
            order_text += f"📦 Продукт: {product}\n"
            order_text += f"💰 Сумма: {amount}\n"
            order_text += f"📅 Дата: {created_at}\n"
            order_text += f"🖼️ Скриншот: {'Есть' if screenshot else 'Нет'}\n\n"
        
        keyboard = []
        for order in pending_orders:
            keyboard.append([InlineKeyboardButton(f"Заказ #{order[0]}", callback_data=f'view_order_{order[0]}')])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='admin_panel')])
        
        try:
            with open('main.png', 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo,
                    caption=order_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.MARKDOWN
                )
            await query.message.delete()
        except FileNotFoundError:
            await query.edit_message_text(
                order_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
    
    # Просмотр конкретного заказа
    elif data.startswith('view_order_'):
        if user.id != ADMIN_ID:
            return
        
        order_id = int(data.split('_')[2])
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if order:
            order_id, user_id, username, product, amount, screenshot, status, created_at = order
            order_text = (
                f"📦 *Заказ #{order_id}*\n\n"
                f"👤 Пользователь: @{username or 'N/A'} (ID: {user_id})\n"
                f"📦 Продукт: {product}\n"
                f"💰 Сумма: {amount}\n"
                f"📅 Дата: {created_at}\n"
                f"📊 Статус: {status}"
            )
            
            try:
                with open('main.png', 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=order_text,
                        reply_markup=order_management_menu(order_id),
                        parse_mode=ParseMode.MARKDOWN
                    )
                await query.message.delete()
            except FileNotFoundError:
                await query.edit_message_text(
                    order_text,
                    reply_markup=order_management_menu(order_id),
                    parse_mode=ParseMode.MARKDOWN
                )
    
    # Подтверждение заказа
    elif data.startswith('confirm_'):
        if user.id != ADMIN_ID:
            return
        
        order_id = int(data.split('_')[1])
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Обновляем статус заказа
        cursor.execute('UPDATE orders SET status = %s WHERE id = %s', ('confirmed', order_id))
        
        # Получаем информацию о заказе
        cursor.execute('SELECT user_id, product FROM orders WHERE id = %s', (order_id,))
        order_info = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if order_info:
            user_id, product = order_info
            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ *Ваш заказ подтвержден!*\n\nПродукт: {product}\nСпасибо за покупку!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить пользователя: {e}")
        
        confirmation_text = "✅ Заказ подтвержден! Пользователь уведомлен."
        try:
            with open('main.png', 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo,
                    caption=confirmation_text,
                    reply_markup=admin_menu()
                )
            await query.message.delete()
        except FileNotFoundError:
            await query.edit_message_text(
                confirmation_text,
                reply_markup=admin_menu()
            )
    
    # Отклонение заказа
    elif data.startswith('reject_'):
        if user.id != ADMIN_ID:
            return
        
        order_id = int(data.split('_')[1])
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Обновляем статус заказа
        cursor.execute('UPDATE orders SET status = %s WHERE id = %s', ('rejected', order_id))
        
        # Получаем информацию о заказе
        cursor.execute('SELECT user_id, product FROM orders WHERE id = %s', (order_id,))
        order_info = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if order_info:
            user_id, product = order_info
            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ *Ваш заказ отклонен*\n\nПродукт: {product}\nЕсли вы считаете это ошибкой, обратитесь в поддержку.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить пользователя: {e}")
        
        rejection_text = "❌ Заказ отклонен! Пользователь уведомлен."
        try:
            with open('main.png', 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo,
                    caption=rejection_text,
                    reply_markup=admin_menu()
                )
            await query.message.delete()
        except FileNotFoundError:
            await query.edit_message_text(
                rejection_text,
                reply_markup=admin_menu()
            )
    
    # Статистика
    elif data == 'admin_stats':
        if user.id != ADMIN_ID:
            return
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Общее количество заказов
        cursor.execute('SELECT COUNT(*) FROM orders')
        total_orders = cursor.fetchone()[0]
        
        # Ожидающие заказы
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = %s', ('pending',))
        pending_orders = cursor.fetchone()[0]
        
        # Подтвержденные заказы
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = %s', ('confirmed',))
        confirmed_orders = cursor.fetchone()[0]
        
        # Отклоненные заказы
        cursor.execute('SELECT COUNT(*) FROM orders WHERE status = %s', ('rejected',))
        rejected_orders = cursor.fetchone()[0]
        
        conn.close()
        
        stats_text = (
            "📊 *Статистика заказов*\n\n"
            f"📦 Всего заказов: {total_orders}\n"
            f"⏳ Ожидают: {pending_orders}\n"
            f"✅ Подтверждены: {confirmed_orders}\n"
            f"❌ Отклонены: {rejected_orders}"
        )
        
        try:
            with open('main.png', 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo,
                    caption=stats_text,
                    reply_markup=admin_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            await query.message.delete()
        except FileNotFoundError:
            await query.edit_message_text(
                stats_text,
                reply_markup=admin_menu(),
                parse_mode=ParseMode.MARKDOWN
            )

# Обработка фотографий (скриншоты оплаты)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_payment'):
        error_text = "Пожалуйста, сначала выберите продукт для покупки через меню 'Купить'"
        await send_message_with_photo(update, context, error_text, main_menu())
        return
    
    user = update.message.from_user
    photo = update.message.photo[-1]  # Берем самую большую версию фото
    
    # Сохраняем информацию о заказе
    products = {
        'buy_1month': {'name': 'Fatality Client 1 месяц', 'price': '50₽/0.5$'},
        'buy_beta': {'name': 'Fatality Client Beta навсегда', 'price': '199₽/2$'},
        'buy_forever': {'name': 'Fatality Client Навсегда', 'price': '599₽/6$'}
    }
    
    product_data = products[context.user_data['awaiting_payment']]
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (user_id, username, product, amount, screenshot) VALUES (%s, %s, %s, %s, %s)',
        (user.id, user.username, product_data['name'], product_data['price'], 'yes')
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Уведомляем администратора
    admin_text = (
        f"🆕 *Новый заказ #{order_id}*\n\n"
        f"👤 Пользователь: @{user.username or 'N/A'} (ID: {user.id})\n"
        f"📦 Продукт: {product_data['name']}\n"
        f"💰 Сумма: {product_data['price']}\n"
        f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        # Отправляем текст администратору
        admin_message = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Пересылаем скриншот администратору
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=f"Скриншот оплаты для заказа #{order_id}",
            reply_to_message_id=admin_message.message_id
        )
        
    except Exception as e:
        logger.error(f"Не удалось уведомить администратора: {e}")
    
    confirmation_text = "✅ Скриншот оплаты получен! Мы проверим его в течение 24 часов и уведомим вас."
    await send_message_with_photo(update, context, confirmation_text, main_menu())
    context.user_data['awaiting_payment'] = None

# Команда админ панели
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде")
        return
    
    admin_text = "👨‍💼 *Админ панель*"
    await send_message_with_photo(update, context, admin_text, admin_menu(), ParseMode.MARKDOWN)

def main():
    # Инициализация базы данных
    init_db()
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Запуск бота
    print("Бот запущен...")
    print(f"Используется PostgreSQL")
    application.run_polling()

if __name__ == '__main__':
    main()
