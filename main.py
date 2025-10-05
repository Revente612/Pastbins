import logging
import json
import os
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

# Путь к JSON файлу для хранения данных
DATA_FILE = 'data.json'

class JSONDatabase:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({"orders": []}, f, ensure_ascii=False, indent=2)
    
    def _read_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"orders": []}
    
    def _write_data(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_order(self, user_id, username, product, amount, screenshot):
        data = self._read_data()
        order_id = len(data['orders']) + 1
        order = {
            'id': order_id,
            'user_id': user_id,
            'username': username,
            'product': product,
            'amount': amount,
            'screenshot': screenshot,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        data['orders'].append(order)
        self._write_data(data)
        return order_id
    
    def get_pending_orders(self):
        data = self._read_data()
        return [order for order in data['orders'] if order['status'] == 'pending']
    
    def get_order(self, order_id):
        data = self._read_data()
        for order in data['orders']:
            if order['id'] == order_id:
                return order
        return None
    
    def update_order_status(self, order_id, status):
        data = self._read_data()
        for order in data['orders']:
            if order['id'] == order_id:
                order['status'] = status
                order['updated_at'] = datetime.now().isoformat()
                self._write_data(data)
                return True
        return False
    
    def get_stats(self):
        data = self._read_data()
        orders = data['orders']
        total = len(orders)
        pending = len([o for o in orders if o['status'] == 'pending'])
        confirmed = len([o for o in orders if o['status'] == 'confirmed'])
        rejected = len([o for o in orders if o['status'] == 'rejected'])
        
        return {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'rejected': rejected
        }

# Инициализация базы данных
db = JSONDatabase()

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
        
        pending_orders = db.get_pending_orders()
        
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
            order_text += f"🆔 Заказ #{order['id']}\n"
            order_text += f"👤 Пользователь: @{order['username'] or 'N/A'} (ID: {order['user_id']})\n"
            order_text += f"📦 Продукт: {order['product']}\n"
            order_text += f"💰 Сумма: {order['amount']}\n"
            order_text += f"📅 Дата: {order['created_at'][:19]}\n"
            order_text += f"🖼️ Скриншот: {'Есть' if order['screenshot'] else 'Нет'}\n\n"
        
        keyboard = []
        for order in pending_orders:
            keyboard.append([InlineKeyboardButton(f"Заказ #{order['id']}", callback_data=f'view_order_{order["id"]}')])
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
        order = db.get_order(order_id)
        
        if order:
            order_text = (
                f"📦 *Заказ #{order['id']}*\n\n"
                f"👤 Пользователь: @{order['username'] or 'N/A'} (ID: {order['user_id']})\n"
                f"📦 Продукт: {order['product']}\n"
                f"💰 Сумма: {order['amount']}\n"
                f"📅 Дата: {order['created_at'][:19]}\n"
                f"📊 Статус: {order['status']}"
            )
            
            try:
                with open('main.png', 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=order_text,
                        reply_markup=order_management_menu(order['id']),
                        parse_mode=ParseMode.MARKDOWN
                    )
                await query.message.delete()
            except FileNotFoundError:
                await query.edit_message_text(
                    order_text,
                    reply_markup=order_management_menu(order['id']),
                    parse_mode=ParseMode.MARKDOWN
                )
    
    # Подтверждение заказа
    elif data.startswith('confirm_'):
        if user.id != ADMIN_ID:
            return
        
        order_id = int(data.split('_')[1])
        order = db.get_order(order_id)
        
        if order and db.update_order_status(order_id, 'confirmed'):
            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=order['user_id'],
                    text=f"✅ *Ваш заказ подтвержден!*\n\nПродукт: {order['product']}\nСпасибо за покупку!",
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
        order = db.get_order(order_id)
        
        if order and db.update_order_status(order_id, 'rejected'):
            # Уведомляем пользователя
            try:
                await context.bot.send_message(
                    chat_id=order['user_id'],
                    text=f"❌ *Ваш заказ отклонен*\n\nПродукт: {order['product']}\nЕсли вы считаете это ошибкой, обратитесь в поддержку.",
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
        
        stats = db.get_stats()
        
        stats_text = (
            "📊 *Статистика заказов*\n\n"
            f"📦 Всего заказов: {stats['total']}\n"
            f"⏳ Ожидают: {stats['pending']}\n"
            f"✅ Подтверждены: {stats['confirmed']}\n"
            f"❌ Отклонены: {stats['rejected']}"
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
    photo = update.message.photo[-1]
    
    products = {
        'buy_1month': {'name': 'Fatality Client 1 месяц', 'price': '50₽/0.5$'},
        'buy_beta': {'name': 'Fatality Client Beta навсегда', 'price': '199₽/2$'},
        'buy_forever': {'name': 'Fatality Client Навсегда', 'price': '599₽/6$'}
    }
    
    product_data = products[context.user_data['awaiting_payment']]
    
    # Сохраняем заказ в JSON
    order_id = db.add_order(user.id, user.username, product_data['name'], product_data['price'], 'yes')
    
    # Уведомляем администратора
    admin_text = (
        f"🆕 *Новый заказ #{order_id}*\n\n"
        f"👤 Пользователь: @{user.username or 'N/A'} (ID: {user.id})\n"
        f"📦 Продукт: {product_data['name']}\n"
        f"💰 Сумма: {product_data['price']}\n"
        f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        admin_message = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
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
    print("Используется JSON база данных")
    application.run_polling()

if __name__ == '__main__':
    main()
