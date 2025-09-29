import logging
import sqlite3
import random
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
BOT_TOKEN = "8400415519:AAETeEt-fAb9JQiXEwSihi1ZYMWaH6U1aUA"

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            money INTEGER DEFAULT 0,
            health INTEGER DEFAULT 100,
            happiness INTEGER DEFAULT 100,
            education_level INTEGER DEFAULT 0,
            job_level INTEGER DEFAULT 0,
            has_apartment INTEGER DEFAULT 0,
            has_laptop INTEGER DEFAULT 0,
            has_vpn INTEGER DEFAULT 0,
            food INTEGER DEFAULT 100,
            cigarettes INTEGER DEFAULT 0,
            vape_type TEXT DEFAULT NULL,
            vape_juice INTEGER DEFAULT 0,
            juice_flavor TEXT DEFAULT NULL,
            snus_packs INTEGER DEFAULT 0,
            snus_strength INTEGER DEFAULT 0,
            has_girlfriend INTEGER DEFAULT 0,
            girlfriend_happiness INTEGER DEFAULT 0,
            age INTEGER DEFAULT 0,
            has_id INTEGER DEFAULT 0,
            last_work_time TEXT,
            last_school_time TEXT,
            last_crime_time TEXT,
            last_date_time TEXT,
            last_smoke_time TEXT,
            last_fraud_time TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def upgrade_db():
    """Обновляет структуру базы данных если она устарела"""
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    new_columns = {
        'has_laptop': 'ALTER TABLE players ADD COLUMN has_laptop INTEGER DEFAULT 0',
        'has_vpn': 'ALTER TABLE players ADD COLUMN has_vpn INTEGER DEFAULT 0',
        'last_smoke_time': 'ALTER TABLE players ADD COLUMN last_smoke_time TEXT',
        'last_fraud_time': 'ALTER TABLE players ADD COLUMN last_fraud_time TEXT',
        'snus_packs': 'ALTER TABLE players ADD COLUMN snus_packs INTEGER DEFAULT 0',
        'snus_strength': 'ALTER TABLE players ADD COLUMN snus_strength INTEGER DEFAULT 0',
        'has_girlfriend': 'ALTER TABLE players ADD COLUMN has_girlfriend INTEGER DEFAULT 0',
        'girlfriend_happiness': 'ALTER TABLE players ADD COLUMN girlfriend_happiness INTEGER DEFAULT 0'
    }
    
    for column_name, alter_query in new_columns.items():
        if column_name not in columns:
            cursor.execute(alter_query)
    
    conn.commit()
    conn.close()
    print("База данных успешно обновлена")

def get_player(user_id):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    player = cursor.fetchone()
    conn.close()
    
    if player:
        # Безопасное создание словаря с проверкой длины кортежа
        player_dict = {
            'user_id': player[0],
            'username': player[1] if len(player) > 1 else None,
            'money': player[2] if len(player) > 2 else 0,
            'health': player[3] if len(player) > 3 else 100,
            'happiness': player[4] if len(player) > 4 else 100,
            'education_level': player[5] if len(player) > 5 else 0,
            'job_level': player[6] if len(player) > 6 else 0,
            'has_apartment': player[7] if len(player) > 7 else 0,
            'has_laptop': player[8] if len(player) > 8 else 0,
            'has_vpn': player[9] if len(player) > 9 else 0,
            'food': player[10] if len(player) > 10 else 100,
            'cigarettes': player[11] if len(player) > 11 else 0,
            'vape_type': player[12] if len(player) > 12 else None,
            'vape_juice': player[13] if len(player) > 13 else 0,
            'juice_flavor': player[14] if len(player) > 14 else None,
            'snus_packs': player[15] if len(player) > 15 else 0,
            'snus_strength': player[16] if len(player) > 16 else 0,
            'has_girlfriend': player[17] if len(player) > 17 else 0,
            'girlfriend_happiness': player[18] if len(player) > 18 else 0,
            'age': player[19] if len(player) > 19 else 16,
            'has_id': player[20] if len(player) > 20 else 0,
            'last_work_time': player[21] if len(player) > 21 else None,
            'last_school_time': player[22] if len(player) > 22 else None,
            'last_crime_time': player[23] if len(player) > 23 else None,
            'last_date_time': player[24] if len(player) > 24 else None,
            'last_smoke_time': player[25] if len(player) > 25 else None,
            'last_fraud_time': player[26] if len(player) > 26 else None,
            'created_at': player[27] if len(player) > 27 else datetime.now().isoformat()
        }
        return player_dict
    return None

def create_player(user_id, username):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO players (user_id, username, age, created_at) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, 16, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_player(user_id, **kwargs):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    
    cursor.execute(f'UPDATE players SET {set_clause} WHERE user_id = ?', values)
    conn.commit()
    conn.close()

def reset_player(user_id, username):
    conn = sqlite3.connect('life_simulator.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE players SET 
            money = 0,
            health = 100,
            happiness = 50,
            education_level = 0,
            job_level = 0,
            has_apartment = 0,
            has_laptop = 0,
            has_vpn = 0,
            food = 100,
            cigarettes = 0,
            vape_type = NULL,
            vape_juice = 0,
            juice_flavor = NULL,
            snus_packs = 0,
            snus_strength = 0,
            has_girlfriend = 0,
            girlfriend_happiness = 0,
            has_id = 0,
            last_work_time = NULL,
            last_school_time = NULL,
            last_crime_time = NULL,
            last_date_time = NULL,
            last_smoke_time = NULL,
            last_fraud_time = NULL
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    player = get_player(user_id)
    if not player:
        create_player(user_id, user.username)
        player = get_player(user_id)
    
    keyboard = [
        ["🏠 Статус", "💼 Работа"],
        ["🛒 Магазин", "🔫 Криминал"],
        ["🏫 Школа", "🚬 Курить/Вейпить/Снюс"],
        ["🏡 Купить квартиру", "💕 Девушка"],
        ["🎂 Отметить ДР", "📋 Получить паспорт"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
👋 Добро пожаловать в Симулятор Жизни, {user.first_name}!

🎯 Ваши цели:
• Заработать деньги 💰 (работа или криминал)
• Купить квартиру 🏡
• Найти девушку 💕
• Не умереть от голода 🍖

📝 Особенности:
- Работать можно с любого возраста
- Можно заниматься криминалом и мошенничеством
- В школе можно курить в туалете (осторожно!)
- Девушка увеличивает счастье
- Можно купить ноутбук для удаленной работы

⚠️ Внимание: курение, вейпинг и снюс в реальной жизни вредят здоровью!
Это всего лишь игра.

Нажмите "🏠 Статус" чтобы увидеть свое состояние!
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    food_decrease = random.randint(5, 15)
    new_food = max(0, player['food'] - food_decrease)
    
    if new_food <= 0:
        health_decrease = 10
        new_health = max(0, player['health'] - health_decrease)
        update_player(user_id, food=new_food, health=new_health)
    else:
        update_player(user_id, food=new_food)
    
    player = get_player(user_id)

    vape_info = ""
    if player['vape_type']:
        vape_info = f"\n🔋 Вейп: {player['vape_type']}"
    if player['vape_juice'] > 0 and player['juice_flavor']:
        vape_info += f"\n💧 Жижа: {player['juice_flavor']} ({player['vape_juice']}мл)"
    
    snus_info = ""
    if player['snus_packs'] > 0:
        snus_info = f"\n📦 Снюс: {player['snus_packs']} пачек ({player['snus_strength']} мг)"
    
    girlfriend_info = ""
    if player['has_girlfriend']:
        girlfriend_info = f"\n💕 Девушка: счастье {player['girlfriend_happiness']}/100"
    
    tech_info = ""
    if player['has_laptop']:
        tech_info += "\n💻 Ноутбук: ✅ Есть"
    if player['has_vpn']:
        tech_info += "\n🛡️ VPN: ✅ Есть"
    
    status_text = f"""
📊 ВАШ СТАТУС:

🎂 Возраст: {player['age']} лет
📋 Паспорт: {'✅ Есть' if player['has_id'] else '❌ Нет (нужно 18 лет)'}

💵 Деньги: {player['money']} руб.
❤️ Здоровье: {player['health']}/100
😊 Счастье: {player['happiness']}/100
🍖 Еда: {player['food']}/100

🎓 Образование: {get_education_level_name(player['education_level'])}
💼 Работа: {get_job_level_name(player['job_level'])}
🏡 Квартира: {'✅ Есть' if player['has_apartment'] else '❌ Нет'}
{tech_info}

🚬 Сигареты: {player['cigarettes']} шт.
{vape_info}
{snus_info}
{girlfriend_info}

{'⚠️ ВАЖНО: У вас закончилась еда! Здоровье уменьшается!' if player['food'] <= 0 else ''}
{'💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно поешьте!' if player['health'] <= 20 else ''}
    """
    
    await update.message.reply_text(status_text)

def get_education_level_name(level):
    levels = {
        0: "9 классов",
        1: "11 классов", 
        2: "Колледж",
        3: "Университет",
        4: "Аспирантура"
    }
    return levels.get(level, "Неизвестно")

def get_job_level_name(level):
    jobs = {
        0: "Безработный",
        1: "Разнорабочий (50 руб.)",
        2: "Продавец (100 руб.)",
        3: "Офисный работник (200 руб.)", 
        4: "Дальнобойщик (800 руб.)",
        5: "Менеджер (500 руб.)",
        6: "Директор (1000 руб.)",
        7: "Мошенник (600 руб.)"
    }
    return jobs.get(level, "Неизвестно")

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['job_level'] == 0:
        await update.message.reply_text("""
💼 Вам нужна работа!
Сначала получите работу в разделе "Магазин" -> "Устроиться на работу"
        """)
        return
    
    if player['job_level'] == 7 and not player['has_laptop']:
        await update.message.reply_text("""
❌ Для работы мошенником нужен ноутбук!
Купите ноутбук в магазине.
        """)
        return
    
    last_work = datetime.fromisoformat(player['last_work_time']) if player['last_work_time'] else None
    work_cooldown = timedelta(minutes=2) if player['job_level'] == 7 else timedelta(minutes=5)
    
    if last_work and (datetime.now() - last_work) < work_cooldown:
        time_left = work_cooldown - (datetime.now() - last_work)
        await update.message.reply_text(f"⏰ Вы устали! Отдохните {int(time_left.total_seconds() / 60)} минут перед следующей работой.")
        return
    
    earnings = [0, 50, 100, 200, 800, 500, 1000, 600][player['job_level']]
    new_money = player['money'] + earnings
    
    update_player(
        user_id, 
        money=new_money, 
        last_work_time=datetime.now().isoformat(),
        happiness=max(0, player['happiness'] - 5)
    )
    
    job_name = "💼 Поработали" if player['job_level'] != 7 else "🕵️‍♂️ Провели аферу"
    
    await update.message.reply_text(f"""
{job_name} и заработали {earnings} руб.!
💰 Теперь у вас: {new_money} руб.

😔 Счастье немного уменьшилось...
    """)

async def crime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Украсть кошелек", "🏪 Ограбить магазин"],
        ["🏠 Ограбить квартиру", "🚗 Угнать машину"],
        ["🕵️‍♂️ Мошенничество", "⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("""
🔫 КРИМИНАЛ:

💰 Украсть кошелек - мало риска, мало денег
🏪 Ограбить магазин - средний риск, средние деньги
🏠 Ограбить квартиру - высокий риск, много денег
🚗 Угнать машину - очень высокий риск, очень много денег
🕵️‍♂️ Мошенничество - интернет-аферы (нужен ноутбук)

⚠️ Внимание: Криминал опасен! Можете попасть в тюрьму (сброс прогресса)!
    """, reply_markup=reply_markup)

async def commit_crime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    crime_type = update.message.text
    success_chance = random.random()
    
    if crime_type == "💰 Украсть кошелек":
        money_min, money_max = 50, 200
        arrest_chance = 0.2
        crime_name = "кража кошелька"
        escape_chance = 0.7
    elif crime_type == "🏪 Ограбить магазин":
        money_min, money_max = 200, 500
        arrest_chance = 0.4
        crime_name = "ограбление магазина" 
        escape_chance = 0.5
    elif crime_type == "🏠 Ограбить квартиру":
        money_min, money_max = 500, 1000
        arrest_chance = 0.6
        crime_name = "ограбление квартиры"
        escape_chance = 0.3
    elif crime_type == "🚗 Угнать машину":
        money_min, money_max = 1000, 2000
        arrest_chance = 0.8
        crime_name = "угон машины"
        escape_chance = 0.2
    elif crime_type == "🕵️‍♂️ Мошенничество":
        if not player['has_laptop']:
            await update.message.reply_text("❌ Для мошенничества нужен ноутбук! Купите в магазине.")
            return
        
        money_min, money_max = 600, 1200
        arrest_chance = 0.3 if player['has_vpn'] else 0.6
        crime_name = "мошенничество"
        escape_chance = 0.8 if player['has_vpn'] else 0.4
    else:
        return
    
    if success_chance > arrest_chance:
        stolen_money = random.randint(money_min, money_max)
        new_money = player['money'] + stolen_money
        
        update_player(
            user_id,
            money=new_money,
            last_crime_time=datetime.now().isoformat(),
            happiness=min(100, player['happiness'] + 10)
        )
        
        crime_emoji = "💻" if crime_type == "🕵️‍♂️ Мошенничество" else "💰"
        
        await update.message.reply_text(f"""
✅ Преступление удалось!

{crime_emoji} Вы получили: {stolen_money} руб.
💰 Теперь у вас: {new_money} руб.
😊 Счастье: +10

{'🛡️ VPN помог остаться анонимным!' if crime_type == "🕵️‍♂️ Мошенничество" and player['has_vpn'] else '🏃‍♂️ Быстро скрывайтесь с места преступления!'}
        """)
    else:
        if random.random() < escape_chance:
            await update.message.reply_text(f"""
🏃‍♂️ ВАС ПОЧТИ ПОЙМАЛИ!

{'Полиция вышла на ваш след' if crime_type == "🕵️‍♂️ Мошенничество" else 'Полиция заметила вас'} при попытке {crime_name},
но вам удалось {'скрыть следы' if crime_type == "🕵️‍♂️ Мошенничество" else 'убежать'}!

💨 Вы {'использовали VPN для анонимности' if crime_type == "🕵️‍♂️ Мошенничество" and player['has_vpn'] else 'скрылись в темных переулках'}...
😰 Счастье: -15
            """)
            update_player(
                user_id,
                happiness=max(0, player['happiness'] - 15)
            )
        else:
            await update.message.reply_text(f"""
🚨🚨🚨 ВАС ПОЙМАЛИ! 🚨🚨🚨

{'Киберполиция' if crime_type == "🕵️‍♂️ Мошенничество" else 'Полиция'} поймала вас при попытке {crime_name}!
Вас посадили в тюрьму...

💀 Все достижения сброшены!
            """)
            reset_player(user_id, player['username'])

async def school_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📚 Учиться", "🚬 Сходить в туалет покурить"],
        ["⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("""
🏫 ШКОЛА:

📚 Учиться - повысить уровень образования
🚬 Сходить в туалет покурить - рискованно, но можно покурить

⚠️ Внимание: курение в школе может привести к проблемам!
    """, reply_markup=reply_markup)

async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['education_level'] >= 4:
        await update.message.reply_text("🎓 Вы уже достигли максимального уровня образования!")
        return
    
    last_study = datetime.fromisoformat(player['last_school_time']) if player['last_school_time'] else None
    if last_study and (datetime.now() - last_study) < timedelta(minutes=3):
        time_left = timedelta(minutes=3) - (datetime.now() - last_study)
        await update.message.reply_text(f"📚 Вы устали учиться! Отдохните {int(time_left.total_seconds() / 60)} минут.")
        return
    
    new_education_level = player['education_level'] + 1
    update_player(
        user_id,
        education_level=new_education_level,
        last_school_time=datetime.now().isoformat(),
        happiness=max(0, player['happiness'] - 3)
    )
    
    education_names = {
        1: "11 классов",
        2: "Колледж", 
        3: "Университет",
        4: "Аспирантура"
    }
    
    await update.message.reply_text(f"""
🎓 Поздравляем! Вы получили: {education_names[new_education_level]}

Теперь вы можете устроиться на работу уровня {new_education_level}!

😔 Счастье немного уменьшилось от учебы...
    """)

async def school_smoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    last_smoke = datetime.fromisoformat(player['last_smoke_time']) if player['last_smoke_time'] else None
    if last_smoke and (datetime.now() - last_smoke) < timedelta(minutes=10):
        time_left = timedelta(minutes=10) - (datetime.now() - last_smoke)
        await update.message.reply_text(f"🚬 Слишком рискованно! Подождите {int(time_left.total_seconds() / 60)} минут.")
        return
    
    teacher_catch_chance = 0.4
    
    if random.random() < teacher_catch_chance:
        await update.message.reply_text("""
🚨🚨🚨 ВАС ПОЙМАЛИ! 🚨🚨🚨

Учитель застал вас курящим в школьном туалете!
Родители вызваны в школу...
Вас отчислили! Игра начинается заново.

💀 Все достижения сброшены!
        """)
        reset_player(user_id, player['username'])
    else:
        keyboard = [
            ["🚬 Выкурить сигарету", "💨 Покурить вейп"],
            ["📦 Закинуть снюс", "⬅️ Выйти из туалета"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update_player(user_id, last_smoke_time=datetime.now().isoformat())
        
        await update.message.reply_text("""
🚬 Вы успешно пробрались в школьный туалет...

💨 Пахнет дымом и вейпом...
👀 Осторожно! Учитель может зайти в любой момент!

Выберите что хотите сделать:
        """, reply_markup=reply_markup)

async def smoke_vape_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    keyboard = [
        ["🚬 Выкурить сигарету", "💨 Покурить вейп"],
        ["📦 Закинуть снюс", "⬅️ Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("""
🚬 Выберите что хотите использовать:

🚬 Сигарета - больше вреда, но дешевле
💨 Вейп - меньше вреда, но нужен вейп и жидкость
📦 Снюс - очень крепкий, большой вред здоровью

⚠️ Помните: в реальной жизни и то и другое вредно для здоровья!
    """, reply_markup=reply_markup)

async def smoke_cigarette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['cigarettes'] <= 0:
        await update.message.reply_text("❌ У вас нет сигарет! Купите в магазине.")
        return
    
    new_cigarettes = player['cigarettes'] - 1
    new_health = max(0, player['health'] - 15)
    new_happiness = min(100, player['happiness'] + 20)
    
    update_player(
        user_id,
        cigarettes=new_cigarettes,
        health=new_health,
        happiness=new_happiness
    )
    
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно лечитесь!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"""
🚬 Вы выкурили сигарету...

❤️ Здоровье: -15 (теперь {new_health})
😊 Счастье: +20 (теперь {new_happiness})
📦 Сигарет осталось: {new_cigarettes}

{health_warning}
⚠️ Курение в реальной жизни вызывает рак и другие заболевания!
    """)

async def vape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['vape_type']:
        await update.message.reply_text("❌ У вас нет вейпа! Купите в магазине.")
        return
    
    if player['vape_juice'] <= 0:
        await update.message.reply_text("❌ В вейпе закончилась жидкость! Купите жидкость в магазине.")
        return
    
    new_juice = max(0, player['vape_juice'] - 5)
    new_health = max(0, player['health'] - 8)
    new_happiness = min(100, player['happiness'] + 25)
    
    update_player(
        user_id,
        vape_juice=new_juice,
        health=new_health,
        happiness=new_happiness
    )
    
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! Срочно лечитесь!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"""
💨 Вы покурили вейп ({player['vape_type']})...

❤️ Здоровье: -8 (теперь {new_health})
😊 Счастье: +25 (теперь {new_happiness})
💧 Жидкости осталось: {new_juice}мл
🎯 Вкус: {player['juice_flavor']}

{health_warning}
⚠️ Вейпинг в реальной жизни тоже вреден для здоровья!
    """)

async def use_snus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['snus_packs'] <= 0:
        await update.message.reply_text("❌ У вас нет снюса! Купите в магазине.")
        return
    
    new_snus = player['snus_packs'] - 1
    new_health = max(0, player['health'] - 25)
    new_happiness = min(100, player['happiness'] + 30)
    
    update_player(
        user_id,
        snus_packs=new_snus,
        health=new_health,
        happiness=new_happiness
    )
    
    health_warning = "💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! СРОЧНО ПРЕКРАТИТЕ И ЛЕЧИТЕСЬ!" if new_health <= 20 else ""
    
    await update.message.reply_text(f"""
📦 Вы закинули снюс {player['snus_strength']} мг...

❤️ Здоровье: -25 (теперь {new_health})
😊 Счастье: +30 (теперь {new_happiness})
📦 Пачек снюса осталось: {new_snus}

{health_warning}
⚠️ СНЮС ОЧЕНЬ ОПАСЕН! В реальной жизни вызывает рак ротовой полости!
    """)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍖 Еда (50 руб.)", callback_data="buy_food")],
        [InlineKeyboardButton("🚬 Сигареты (30 руб.)", callback_data="buy_cigarettes")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить сигареты (100 руб.)", callback_data="buy_cigarettes_adult")],
        [InlineKeyboardButton("💨 Вейпы и жижи", callback_data="vape_shop")],
        [InlineKeyboardButton("📦 Снюс 500 мг (150 руб.)", callback_data="buy_snus")],
        [InlineKeyboardButton("❤️ Лечение (100 руб.)", callback_data="buy_health")],
        [InlineKeyboardButton("😊 Развлечения (80 руб.)", callback_data="buy_happiness")],
        [InlineKeyboardButton("💼 Устроиться на работу (200 руб.)", callback_data="buy_job")],
        [InlineKeyboardButton("💻 Ноутбук (5000 руб.)", callback_data="buy_laptop")],
        [InlineKeyboardButton("🛡️ VPN (200 руб.)", callback_data="buy_vpn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("""
🛒 МАГАЗИН:

🍖 Еда (50 руб.) - +50 к еде
🚬 Сигареты (30 руб.) - пачка сигарет (только с 18 лет)
🔞 Попросить взрослых (100 руб.) - дороже, но без паспорта
💨 Вейпы и жижи - электронные сигареты и жидкости
📦 Снюс 500 мг (150 руб.) - крепкий снюс
❤️ Лечение (100 руб.) - +30 к здоровью
😊 Развлечения (80 руб.) - +40 к счастью
💼 Устроиться на работу (200 руб.) - получить работу
💻 Ноутбук (5000 руб.) - для удаленной работы и мошенничества
🛡️ VPN (200 руб.) - анонимность для мошенничества

Выберите что хотите купить:
    """, reply_markup=reply_markup)

async def vape_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔋 Вейп устройства", callback_data="vape_devices")],
        [InlineKeyboardButton("💧 Жидкости для вейпа", callback_data="vape_juices")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить вейп (300 руб.)", callback_data="buy_vape_adult")],
        [InlineKeyboardButton("🔞 Попросить взрослых купить жижу (250 руб.)", callback_data="buy_juice_adult")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
💨 МАГАЗИН ВЕЙПОВ И ЖИДКОСТЕЙ:

🔋 Вейп устройства - одноразовые и многоразовые
💧 Жидкости - разные вкусы
🔞 Попросить взрослых купить вейп - купить без паспорта
🔞 Попросить взрослых купить жижу - купить без паспорта

⚠️ Для покупки вейпов нужно быть 18+ или попросить взрослых
    """, reply_markup=reply_markup)

async def vape_devices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Pasito 2 (400 руб.)", callback_data="buy_pasito2")],
        [InlineKeyboardButton("Xros (350 руб.)", callback_data="buy_xros")],
        [InlineKeyboardButton("Boost 2 (450 руб.)", callback_data="buy_boost2")],
        [InlineKeyboardButton("Minican (300 руб.)", callback_data="buy_minican")],
        [InlineKeyboardButton("Knight (380 руб.)", callback_data="buy_knight")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="vape_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
🔋 ВЕЙП УСТРОЙСТВА:

Pasito 2 - 400 руб. (мощный, многоразовый)
Xros - 350 руб. (компактный)
Boost 2 - 450 руб. (профессиональный)
Minican - 300 руб. (одноразовый)
Knight - 380 руб. (стильный)

Выберите устройство:
    """, reply_markup=reply_markup)

async def vape_juices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🍉 Арбуз и мята (200 руб.)", callback_data="buy_juice_watermelon")],
        [InlineKeyboardButton("🌿 Лесные ягоды и мята (220 руб.)", callback_data="buy_juice_berries")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="vape_shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("""
💧 ЖИДКОСТИ ДЛЯ ВЕЙПА:

🍉 Арбуз и мята - 200 руб. (30мл)
🌿 Лесные ягоды и мята - 220 руб. (30мл)

Жидкости добавляют 30мл к вашему вейпу
    """, reply_markup=reply_markup)

async def handle_shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    player = get_player(user_id)
    
    if not player:
        await query.edit_message_text("Сначала запустите бота командой /start")
        return
    
    if query.data == "vape_shop":
        await vape_shop_menu(update, context)
        return
    elif query.data == "vape_devices":
        await vape_devices_menu(update, context)
        return
    elif query.data == "vape_juices":
        await vape_juices_menu(update, context)
        return
    elif query.data == "back_to_shop":
        await shop_callback(update, context)
        return
    
    item_data = {
        "buy_food": {"price": 50, "type": "food"},
        "buy_cigarettes": {"price": 30, "type": "cigarettes"},
        "buy_cigarettes_adult": {"price": 100, "type": "cigarettes_adult"},
        "buy_health": {"price": 100, "type": "health"},
        "buy_happiness": {"price": 80, "type": "happiness"},
        "buy_job": {"price": 200, "type": "job"},
        "buy_snus": {"price": 150, "type": "snus"},
        "buy_laptop": {"price": 5000, "type": "laptop"},
        "buy_vpn": {"price": 200, "type": "vpn"},
        "buy_pasito2": {"price": 400, "type": "vape_device", "name": "Pasito 2"},
        "buy_xros": {"price": 350, "type": "vape_device", "name": "Xros"},
        "buy_boost2": {"price": 450, "type": "vape_device", "name": "Boost 2"},
        "buy_minican": {"price": 300, "type": "vape_device", "name": "Minican"},
        "buy_knight": {"price": 380, "type": "vape_device", "name": "Knight"},
        "buy_juice_watermelon": {"price": 200, "type": "vape_juice", "flavor": "Арбуз и мята"},
        "buy_juice_berries": {"price": 220, "type": "vape_juice", "flavor": "Лесные ягоды и мята"},
        "buy_vape_adult": {"price": 300, "type": "vape_adult"},
        "buy_juice_adult": {"price": 250, "type": "juice_adult"}
    }
    
    item_info = item_data.get(query.data)
    if not item_info:
        return
    
    price = item_info["price"]
    item_type = item_info["type"]
    
    if item_type == "cigarettes" and (player['age'] < 18 or not player['has_id']):
        await query.edit_message_text("❌ Для покупки сигарет нужно быть 18+ и иметь паспорт!")
        return
    
    if item_type in ["vape_device", "vape_juice"] and (player['age'] < 18 or not player['has_id']):
        await query.edit_message_text("❌ Для покупки вейпов нужно быть 18+ и иметь паспорт!")
        return
    
    if player['money'] < price:
        await query.edit_message_text(f"❌ Недостаточно денег! Нужно {price} руб., а у вас {player['money']} руб.")
        return
    
    new_money = player['money'] - price
    message = f"✅ Покупка совершена за {price} руб.\n💰 Осталось: {new_money} руб.\n"
    
    if item_type == "food":
        update_player(user_id, money=new_money, food=min(100, player['food'] + 50))
        message += "🍖 +50 к еде"
    elif item_type == "cigarettes":
        update_player(user_id, money=new_money, cigarettes=player['cigarettes'] + 20)
        message += "🚬 +20 сигарет"
    elif item_type == "cigarettes_adult":
        update_player(user_id, money=new_money, cigarettes=player['cigarettes'] + 20)
        message += "🚬 +20 сигарет (через взрослых)"
    elif item_type == "health":
        update_player(user_id, money=new_money, health=min(100, player['health'] + 30))
        message += "❤️ +30 к здоровью"
    elif item_type == "happiness":
        update_player(user_id, money=new_money, happiness=min(100, player['happiness'] + 40))
        message += "😊 +40 к счастью"
    elif item_type == "job":
        if player['job_level'] < 7:
            new_job_level = player['job_level'] + 1
            update_player(user_id, money=new_money, job_level=new_job_level)
            message += f"💼 Теперь вы: {get_job_level_name(new_job_level)}"
        else:
            message += "💼 У вас уже максимальный уровень работы!"
    elif item_type == "snus":
        update_player(user_id, money=new_money, snus_packs=player['snus_packs'] + 1, snus_strength=500)
        message += "📦 +1 пачка снюса 500 мг"
    elif item_type == "laptop":
        update_player(user_id, money=new_money, has_laptop=1)
        message += "💻 Вы купили ноутбук! Теперь можете работать удаленно и заниматься мошенничеством"
    elif item_type == "vpn":
        update_player(user_id, money=new_money, has_vpn=1)
        message += "🛡️ Вы купили VPN! Теперь вы более анонимны в интернете"
    elif item_type == "vape_device":
        update_player(user_id, money=new_money, vape_type=item_info["name"])
        message += f"🔋 Приобретен вейп: {item_info['name']}"
    elif item_type == "vape_juice":
        update_player(user_id, money=new_money, vape_juice=player['vape_juice'] + 30, juice_flavor=item_info["flavor"])
        message += f"💧 +30мл жидкости: {item_info['flavor']}"
    elif item_type == "vape_adult":
        vapes = ["Pasito 2", "Xros", "Boost 2", "Minican", "Knight"]
        random_vape = random.choice(vapes)
        update_player(user_id, money=new_money, vape_type=random_vape)
        message += f"🔋 Взрослые купили вам вейп: {random_vape}"
    elif item_type == "juice_adult":
        juices = ["Арбуз и мята", "Лесные ягоды и мята"]
        random_juice = random.choice(juices)
        update_player(user_id, money=new_money, vape_juice=player['vape_juice'] + 30, juice_flavor=random_juice)
        message += f"💧 Взрослые купили вам жидкость: {random_juice} (30мл)"
    
    await query.edit_message_text(message)

async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await shop(update, context)

async def buy_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_apartment']:
        await update.message.reply_text("🏡 У вас уже есть квартира!")
        return
    
    apartment_price = 50000
    
    if player['money'] < apartment_price:
        await update.message.reply_text(f"""
❌ Недостаточно денег для покупки квартиры!
💰 Нужно: {apartment_price} руб.
💵 У вас: {player['money']} руб.

💼 Продолжайте работать и копите деньги!
        """)
        return
    
    new_money = player['money'] - apartment_price
    update_player(user_id, money=new_money, has_apartment=1, happiness=min(100, player['happiness'] + 50))
    
    await update.message.reply_text(f"""
🎉 ПОЗДРАВЛЯЕМ! Вы купили квартиру за {apartment_price} руб.!

🏡 Теперь у вас есть собственное жилье!
😊 Счастье значительно увеличилось!
💰 Осталось денег: {new_money} руб.

🎯 Основная цель достигнута! Вы победили в игре!
Но жизнь продолжается... 😊
    """)

async def celebrate_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    new_age = player['age'] + 1
    update_player(user_id, age=new_age, happiness=min(100, player['happiness'] + 10))
    
    message = f"🎂 С Днем Рождения! Вам теперь {new_age} лет!\n😊 +10 к счастью"
    
    if new_age == 18:
        message += "\n\n🎉 Вам 18 лет! Теперь вы можете:\n• Получить паспорт\n• Легально покупать сигареты\n• Легально покупать вейпы\n• Устроиться на работу дальнобойщиком"
    
    await update.message.reply_text(message)

async def get_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    if player['has_id']:
        await update.message.reply_text("📋 У вас уже есть паспорт!")
        return
    
    if player['age'] < 18:
        await update.message.reply_text(f"❌ Паспорт можно получить только с 18 лет! Вам сейчас {player['age']} лет.")
        return
    
    update_player(user_id, has_id=1)
    await update.message.reply_text("""
📋 Поздравляем! Вы получили паспорт!

Теперь вы можете:
• Легально покупать сигареты
• Легально покупать вейпы
• Устроиться на взрослую работу
• Жить полной жизнью!
    """)

async def girlfriend_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("Сначала запустите бота командой /start")
        return
    
    keyboard = []
    
    if not player['has_girlfriend']:
        keyboard.append(["💕 Найти девушку"])
    else:
        keyboard.append(["💑 Свидание", "🎁 Подарок девушке"])
        keyboard.append(["💔 Расстаться"])
    
    keyboard.append(["⬅️ Назад"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("""
💕 ДЕВУШКА:

У вас пока нет девушки. Хотите найти?
- Девушка увеличивает счастье
- Нужно ходить на свидания
- Можно дарить подарки

Нажмите "💕 Найти девушку" чтобы попробовать!
        """, reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"""
💕 ВАША ДЕВУШКА:

😊 Счастье девушки: {player['girlfriend_happiness']}/100

💑 Свидание - повышает счастье девушки
🎁 Подарок - дорого, но сильно повышает счастье
💔 Расстаться - если надоело

Чем счастливее девушка, тем больше бонус к вашему счастью!
        """, reply_markup=reply_markup)

async def find_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if player['has_girlfriend']:
        await update.message.reply_text("💕 У вас уже есть девушка!")
        return
    
    success_chance = 0.3 + (player['happiness'] / 200) + (min(player['money'], 1000) / 2000)
    
    if random.random() < success_chance:
        update_player(
            user_id,
            has_girlfriend=1,
            girlfriend_happiness=50,
            happiness=min(100, player['happiness'] + 20)
        )
        await update.message.reply_text("""
💕 ПОЗДРАВЛЯЕМ! Вы нашли девушку!

😊 Ваше счастье: +20
💑 Счастье девушки: 50/100

Теперь вы можете ходить на свидания и дарить подарки!
Чем счастливее девушка, тем больше бонус к вашему счастью!
        """)
    else:
        await update.message.reply_text("""
😔 Вам не удалось найти девушку...

Попробуйте еще раз когда будете счастливее и богаче!
Девушкам нравятся уверенные и успешные парни.
        """)

async def date_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    last_date = datetime.fromisoformat(player['last_date_time']) if player['last_date_time'] else None
    if last_date and (datetime.now() - last_date) < timedelta(minutes=15):
        time_left = timedelta(minutes=15) - (datetime.now() - last_date)
        await update.message.reply_text(f"💑 Девушка устала! Подождите {int(time_left.total_seconds() / 60)} минут до следующего свидания.")
        return
    
    happiness_increase = random.randint(10, 20)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    player_happiness_bonus = happiness_increase // 2
    
    update_player(
        user_id,
        girlfriend_happiness=new_girlfriend_happiness,
        happiness=min(100, player['happiness'] + player_happiness_bonus),
        last_date_time=datetime.now().isoformat()
    )
    
    await update.message.reply_text(f"""
💑 Вы сходили на свидание!

😊 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness}/100)
🎉 Ваше счастье: +{player_happiness_bonus}

Девушка очень довольна свиданием!
    """)

async def gift_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    gift_price = 500
    
    if player['money'] < gift_price:
        await update.message.reply_text(f"❌ Недостаточно денег для подарка! Нужно {gift_price} руб.")
        return
    
    happiness_increase = random.randint(25, 40)
    new_girlfriend_happiness = min(100, player['girlfriend_happiness'] + happiness_increase)
    new_money = player['money'] - gift_price
    
    update_player(
        user_id,
        girlfriend_happiness=new_girlfriend_happiness,
        money=new_money,
        happiness=min(100, player['happiness'] + 15)
    )
    
    await update.message.reply_text(f"""
🎁 Вы подарили девушке дорогой подарок!

😊 Счастье девушки: +{happiness_increase} (теперь {new_girlfriend_happiness}/100)
💵 Потрачено: {gift_price} руб.
💰 Осталось: {new_money} руб.
🎉 Ваше счастье: +15

Девушка в восторге от подарка!
    """)

async def break_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)
    
    if not player['has_girlfriend']:
        await update.message.reply_text("❌ У вас нет девушки!")
        return
    
    update_player(
        user_id,
        has_girlfriend=0,
        girlfriend_happiness=0,
        happiness=max(0, player['happiness'] - 30)
    )
    
    await update.message.reply_text("""
💔 Вы расстались с девушкой...

😔 Ваше счастье: -30
💔 Теперь вы снова одиноки

Можете найти новую девушку когда будете готовы!
    """)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🏠 Статус":
        await show_status(update, context)
    elif text == "💼 Работа":
        await work(update, context)
    elif text == "🔫 Криминал":
        await crime_menu(update, context)
    elif text in ["💰 Украсть кошелек", "🏪 Ограбить магазин", "🏠 Ограбить квартиру", "🚗 Угнать машину", "🕵️‍♂️ Мошенничество"]:
        await commit_crime(update, context)
    elif text == "🛒 Магазин":
        await shop(update, context)
    elif text == "🏫 Школа":
        await school_menu(update, context)
    elif text == "📚 Учиться":
        await study(update, context)
    elif text == "🚬 Сходить в туалет покурить":
        await school_smoke(update, context)
    elif text == "🏡 Купить квартиру":
        await buy_apartment(update, context)
    elif text == "🚬 Курить/Вейпить/Снюс":
        await smoke_vape_menu(update, context)
    elif text == "🚬 Выкурить сигарету":
        await smoke_cigarette(update, context)
    elif text == "💨 Покурить вейп":
        await vape(update, context)
    elif text == "📦 Закинуть снюс":
        await use_snus(update, context)
    elif text == "🎂 Отметить ДР":
        await celebrate_birthday(update, context)
    elif text == "📋 Получить паспорт":
        await get_passport(update, context)
    elif text == "💕 Девушка":
        await girlfriend_menu(update, context)
    elif text == "💕 Найти девушку":
        await find_girlfriend(update, context)
    elif text == "💑 Свидание":
        await date_girlfriend(update, context)
    elif text == "🎁 Подарок девушке":
        await gift_girlfriend(update, context)
    elif text == "💔 Расстаться":
        await break_up(update, context)
    elif text in ["⬅️ Назад", "⬅️ Выйти из туалета"]:
        await start(update, context)
    else:
        await update.message.reply_text("Используйте кнопки меню для управления игрой!")

def main():
    init_db()
    upgrade_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^vape_"))
    application.add_handler(CallbackQueryHandler(handle_shop_callback, pattern="^back_to_shop"))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()