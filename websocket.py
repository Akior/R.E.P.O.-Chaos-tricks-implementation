import asyncio
import websockets
import json
import random
import threading
import tkinter as tk
from tkinter import ttk

# -------------------------------
# Группа "all_..." (глобальные эффекты для всех игроков)
all_buff_heal_prob            = 10    # Восстановление части здоровья у всех игроков
all_buff_full_restore_prob    = 4     # Полное восстановление здоровья и других показателей
all_debuff_hurt_prob          = 8     # Нанесение урона всем игрокам
all_debuff_hp_shuffle_prob    = 7     # Перетасовка здоровья между игроками
all_buff_hp_average_prob      = 6     # Усреднение здоровья всех игроков
all_goal_dec_prob             = 2     # Уменьшение цели/счёта
all_goal_inc_prob             = 2     # Увеличение цели/счёта
all_teleport_shuffle_prob     = 6     # Перемещение игроков по случайным позициям
all_teleport_start_prob       = 3     # Телепортация всех на стартовую позицию
all_teleport_rand_prob        = 3     # Случайная телепортация
all_cart_spread_prob          = 5     # Разбрасывание тележек по карте
all_stun_enemies_prob         = 4     # Оглушение противников
all_buff_resurrect_rand_prob  = 3     # Воскрешение случайного мёртвого игрока
all_buff_resurrect_all_prob   = 1     # Воскрешение всех мёртвых игроков
all_debuff_kill_rand_prob     = 1     # Случайное мгновенное убийство одного игрока

# Группа "item_..." (предметы, дающие бонусы или эффекты)
item_health_small_prob        = 5     # Небольшое восстановление здоровья
item_health_med_prob          = 3     # Среднее восстановление здоровья
item_health_big_prob          = 2     # Значительное восстановление здоровья
item_crystal_prob             = 1     # Получение редкого кристалла
item_nade_stun_prob           = 3     # Граната, оглушающая противников
item_nade_shock_prob          = 3     # Граната с электрическим эффектом
item_nade_expl_prob           = 2     # Взрывная граната
item_nade_f1_prob             = 5     # Специальная граната F1
item_nade_duck_f1_prob        = 5     # Граната с "утиной" тематикой
item_mine_stun_prob           = 5     # Мина, оглушающая противников
item_mine_shock_prob          = 5     # Мина с электрическим разрядом
item_mine_expl_prob           = 3     # Взрывная мина
item_rubber_duck_prob         = 3     # Резиновая утка как отвлекающий манёвр
item_book_roll_prob           = 2     # Книга для улучшения манёвренности
item_book_speed_prob          = 2     # Книга увеличения скорости
item_book_energy_prob         = 2     # Книга восстановления энергии
item_book_health_prob         = 2     # Книга увеличения или восстановления здоровья
item_book_range_prob          = 2     # Книга расширения дальности действия
item_book_strength_prob       = 2     # Книга повышения силы
item_book_jump_prob           = 2     # Книга улучшения прыжковых характеристик
item_drone_roll_prob          = 2     # Дрон для улучшения мобильности
item_drone_gravity_prob       = 2     # Дрон для изменения гравитации
item_drone_feather_prob       = 2     # Дрон для ослабления силы тяжести
item_drone_energy_prob        = 2     # Дрон, восстанавливающий энергию
item_drone_shield_prob        = 2     # Дрон-щит для защиты
item_sphere_gravity_prob      = 2     # Сферический генератор гравитации
item_frying_pan_prob          = 2     # Сковорода как оружие ближнего боя
item_inflatable_hammer_prob   = 2     # Надувной молот
item_sword_prob               = 3     # Меч для ближнего боя
item_baseball_bat_prob        = 3     # Бейсбольная бита
item_sledge_hammer_prob       = 3     # Кувалда с мощным уроном
item_valuable_tracker_prob    = 2     # Трекер для поиска ценных предметов
item_extraction_tracker_prob  = 2     # Трекер для поиска точек эвакуации
item_cart_small_prob          = 3     # Маленькая тележка
item_cart_medium_prob         = 3     # Средняя тележка
item_tranq_prob               = 4     # Транквилизатор для обездвиживания противников
item_handgun_prob             = 4     # Пистолет для атаки на средней дистанции
item_shotgun_prob             = 4     # Дробовик для коротких дистанций

# Группа "spawn_..." (появление врагов или NPC)
spawn_duck_prob             = 50    # Спавн утки (отвлекающий манёвр)
spawn_spewer_prob           = 8     # Спавн существа, извергающего вещества
spawn_upscream_prob         = 5     # Спавн существа с пронзительным воплем
spawn_alien_prob            = 3     # Спавн пришельца с уникальными эффектами
spawn_baby_prob             = 5     # Спавн младенца с хаотичным эффектом
spawn_thinman_prob          = 5     # Спавн худого персонажа (быстрый и неуловимый)
spawn_hidden_prob           = 5     # Спавн скрытого врага, внезапно атаковавшего
spawn_frog_prob             = 5     # Спавн лягушки, быстрая перемещающаяся единица
spawn_bowtie_prob           = 3     # Спавн персонажа в галстуке-бабочке (особые способности)
spawn_huntsman_prob         = 8     # Спавн охотника с прицельными атаками
spawn_trudge_prob           = 8     # Спавн медленного, но опасного персонажа
spawn_clown_prob            = 5     # Спавн клоуна, создающего хаос
spawn_robe_prob             = 5     # Спавн персонажа в мантии с магическими умениями
spawn_reaper_prob           = 4     # Спавн Жнеца, вызывающего мгновенную угрозу

# Специальное событие "empty_event" (ничего не делает)
empty_event_prob            = 100

# -------------------------------
# Словарь соответствия EventID и вероятности
probabilities = {
    "all_buff_heal":            all_buff_heal_prob,
    "all_buff_full_restore":    all_buff_full_restore_prob,
    "all_debuff_hurt":          all_debuff_hurt_prob,
    "all_debuff_hp_shuffle":    all_debuff_hp_shuffle_prob,
    "all_buff_hp_average":      all_buff_hp_average_prob,
    "all_goal_dec":             all_goal_dec_prob,
    "all_goal_inc":             all_goal_inc_prob,
    "all_teleport_shuffle":     all_teleport_shuffle_prob,
    "all_teleport_start":       all_teleport_start_prob,
    "all_teleport_rand":        all_teleport_rand_prob,
    "all_cart_spread":          all_cart_spread_prob,
    "all_stun_enemies":         all_stun_enemies_prob,
    "all_buff_resurrect_rand":  all_buff_resurrect_rand_prob,
    "all_buff_resurrect_all":   all_buff_resurrect_all_prob,
    "all_debuff_kill_rand":     all_debuff_kill_rand_prob,

    "item_health_small":        item_health_small_prob,
    "item_health_med":          item_health_med_prob,
    "item_health_big":          item_health_big_prob,
    "item_crystal":             item_crystal_prob,
    "item_nade_stun":           item_nade_stun_prob,
    "item_nade_shock":          item_nade_shock_prob,
    "item_nade_expl":           item_nade_expl_prob,
    "item_nade_f1":             item_nade_f1_prob,
    "item_nade_duck_f1":        item_nade_duck_f1_prob,
    "item_mine_stun":           item_mine_stun_prob,
    "item_mine_shock":          item_mine_shock_prob,
    "item_mine_expl":           item_mine_expl_prob,
    "item_rubber_duck":         item_rubber_duck_prob,
    "item_book_roll":           item_book_roll_prob,
    "item_book_speed":          item_book_speed_prob,
    "item_book_energy":         item_book_energy_prob,
    "item_book_health":         item_book_health_prob,
    "item_book_range":          item_book_range_prob,
    "item_book_strength":       item_book_strength_prob,
    "item_book_jump":           item_book_jump_prob,
    "item_drone_roll":          item_drone_roll_prob,
    "item_drone_gravity":       item_drone_gravity_prob,
    "item_drone_feather":       item_drone_feather_prob,
    "item_drone_energy":        item_drone_energy_prob,
    "item_drone_shield":        item_drone_shield_prob,
    "item_sphere_gravity":      item_sphere_gravity_prob,
    "item_frying_pan":          item_frying_pan_prob,
    "item_inflatable_hammer":   item_inflatable_hammer_prob,
    "item_sword":               item_sword_prob,
    "item_baseball_bat":        item_baseball_bat_prob,
    "item_sledge_hammer":       item_sledge_hammer_prob,
    "item_valuable_tracker":    item_valuable_tracker_prob,
    "item_extraction_tracker":  item_extraction_tracker_prob,
    "item_cart_small":          item_cart_small_prob,
    "item_cart_medium":         item_cart_medium_prob,
    "item_tranq":               item_tranq_prob,
    "item_handgun":             item_handgun_prob,
    "item_shotgun":             item_shotgun_prob,

    "spawn_duck":               spawn_duck_prob,
    "spawn_spewer":             spawn_spewer_prob,
    "spawn_upscream":           spawn_upscream_prob,
    "spawn_alien":              spawn_alien_prob,
    "spawn_baby":               spawn_baby_prob,
    "spawn_thinman":            spawn_thinman_prob,
    "spawn_hidden":             spawn_hidden_prob,
    "spawn_frog":               spawn_frog_prob,
    "spawn_bowtie":             spawn_bowtie_prob,
    "spawn_huntsman":           spawn_huntsman_prob,
    "spawn_trudge":             spawn_trudge_prob,
    "spawn_clown":              spawn_clown_prob,
    "spawn_robe":               spawn_robe_prob,
    "spawn_reaper":             spawn_reaper_prob,

    "empty_event":              empty_event_prob
}

# -------------------------------
# Список команд для случайного триггера (каждая команда представлена словарём)
commands = [
    {"EventID": "all_buff_heal"},
    {"EventID": "all_buff_full_restore"},
    {"EventID": "all_debuff_hurt"},
    {"EventID": "all_debuff_hp_shuffle"},
    {"EventID": "all_buff_hp_average"},
    {"EventID": "all_goal_dec"},
    {"EventID": "all_goal_inc"},
    {"EventID": "all_teleport_shuffle"},
    {"EventID": "all_teleport_start"},
    {"EventID": "all_teleport_rand"},
    {"EventID": "all_cart_spread"},
    {"EventID": "all_stun_enemies"},
    {"EventID": "all_buff_resurrect_rand"},
    {"EventID": "all_buff_resurrect_all"},
    {"EventID": "all_debuff_kill_rand"},
    {"EventID": "item_health_small"},
    {"EventID": "item_health_med"},
    {"EventID": "item_health_big"},
    {"EventID": "item_crystal"},
    {"EventID": "item_nade_stun"},
    {"EventID": "item_nade_shock"},
    {"EventID": "item_nade_expl"},
    {"EventID": "item_nade_f1"},
    {"EventID": "item_nade_duck_f1"},
    {"EventID": "item_mine_stun"},
    {"EventID": "item_mine_shock"},
    {"EventID": "item_mine_expl"},
    {"EventID": "item_rubber_duck"},
    {"EventID": "item_book_roll"},
    {"EventID": "item_book_speed"},
    {"EventID": "item_book_energy"},
    {"EventID": "item_book_health"},
    {"EventID": "item_book_range"},
    {"EventID": "item_book_strength"},
    {"EventID": "item_book_jump"},
    {"EventID": "item_drone_roll"},
    {"EventID": "item_drone_gravity"},
    {"EventID": "item_drone_feather"},
    {"EventID": "item_drone_energy"},
    {"EventID": "item_drone_shield"},
    {"EventID": "item_sphere_gravity"},
    {"EventID": "item_frying_pan"},
    {"EventID": "item_inflatable_hammer"},
    {"EventID": "item_sword"},
    {"EventID": "item_baseball_bat"},
    {"EventID": "item_sledge_hammer"},
    {"EventID": "item_valuable_tracker"},
    {"EventID": "item_extraction_tracker"},
    {"EventID": "item_cart_small"},
    {"EventID": "item_cart_medium"},
    {"EventID": "item_tranq"},
    {"EventID": "item_handgun"},
    {"EventID": "item_shotgun"},
    {"EventID": "spawn_duck", "Args": []},
    {"EventID": "spawn_spewer", "Args": []},
    {"EventID": "spawn_upscream", "Args": []},
    {"EventID": "spawn_alien", "Args": []},
    {"EventID": "spawn_baby", "Args": []},
    {"EventID": "spawn_thinman", "Args": []},
    {"EventID": "spawn_hidden", "Args": []},
    {"EventID": "spawn_frog", "Args": []},
    {"EventID": "spawn_bowtie", "Args": []},
    {"EventID": "spawn_huntsman", "Args": []},
    {"EventID": "spawn_trudge", "Args": []},
    {"EventID": "spawn_clown", "Args": []},
    {"EventID": "spawn_robe", "Args": []},
    {"EventID": "spawn_reaper", "Args": []},
    {"EventID": "empty_event"}
]

# -------------------------------
# Хранение активных WebSocket соединений
active_connections = set()

# Глобальные переменные для настроек рандом эвентов
random_events_enabled_var = None  # BooleanVar для переключателя
random_event_delay_var = None     # StringVar для задержки
# Словарь для переменных настроек вероятностей, ключ – EventID
probability_vars = {}

async def handle_connection(websocket):
    print("Client connected.")
    active_connections.add(websocket)
    config = {
        "type": "config",
        "data": json.dumps({"isAllPlayers": True})
    }
    await websocket.send(json.dumps(config))
    try:
        async for message in websocket:
            print(f"Received: {message}")
    finally:
        active_connections.remove(websocket)

async def broadcast(message):
    if not active_connections:
        print("No active connections to broadcast to.")
        return
    for websocket in list(active_connections):
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed while broadcasting.")
            active_connections.remove(websocket)

def get_username_by_event(event_id: str) -> str:
    if event_id.startswith("spawn_"):
        return "спавн моба"
    elif event_id.startswith("item_"):
        return "спавн предмета"
    elif event_id.startswith("all_buff_"):
        return "позитивное событие"
    elif event_id.startswith("all_debuff_"):
        return "негативное событие"
    elif event_id in ("all_goal_dec", "all_goal_inc", "all_teleport_shuffle",
                      "all_teleport_start", "all_teleport_rand", "all_cart_spread", "empty_event"):
        return "нейтральное событие"
    else:
        return "нейтральное событие"

async def trigger_random_event():
    while True:
        # Проверяем, включены ли случайные эвенты. Если нет, ожидаем 1 секунду и повторяем проверку.
        if random_events_enabled_var.get():
            try:
                delay = int(random_event_delay_var.get())
            except ValueError:
                delay = 120
            await asyncio.sleep(delay)
            # Получаем актуальные веса из переменных настроек
            weights = []
            for cmd in commands:
                eid = cmd["EventID"]
                try:
                    weight = int(probability_vars[eid].get()) if eid in probability_vars else probabilities.get(eid, 0)
                except ValueError:
                    weight = probabilities.get(eid, 0)
                weights.append(weight)
            command = random.choices(commands, weights=weights, k=1)[0]
            event_id = command["EventID"]

            if event_id == "empty_event":
                print("Triggering empty event: никакого действия не выполнено.")
                continue

            username = get_username_by_event(event_id)
            payload = {
                "type": "event",
                "data": f"UserName={username}&Cost=0&EventID={event_id}&Lang=RU&ExtraInfo=",
            }
            print(f"Triggering random event: {event_id} с UserName={username}")
            await broadcast(json.dumps(payload))
        else:
            await asyncio.sleep(1)

async def trigger_event_by_id(event_id: str):
    if event_id == "empty_event":
        print("Triggering empty event: никакого действия не выполнено.")
        return
    username = get_username_by_event(event_id)
    payload = {
        "type": "event",
        "data": f"UserName={username}&Cost=0&EventID={event_id}&Lang=RU&ExtraInfo=",
    }
    print(f"Triggering event: {event_id} с UserName={username}")
    await broadcast(json.dumps(payload))

# -------------------------------
# Сопоставление EventID с понятными русскими названиями для кнопок
button_texts = {
    "all_buff_heal":           "Частичное исцеление здоровья",
    "all_buff_full_restore":   "Полное исцеление",
    "all_debuff_hurt":         "Пощёчина",
    "all_debuff_hp_shuffle":   "Перетасовка здоровья",
    "all_buff_hp_average":     "Усреднение здоровья",
    "all_goal_dec":            "Уменьшить цель",
    "all_goal_inc":            "Увеличить цель",
    "all_teleport_shuffle":    "Случайное перемещение",
    "all_teleport_start":      "Телепортация на старт",
    "all_teleport_rand":       "Случайная телепортация",
    "all_cart_spread":         "Разброс тележек",
    "all_stun_enemies":        "Оглушить противников",
    "all_buff_resurrect_rand": "Воскрешение случайного игрока",
    "all_buff_resurrect_all":  "Воскрешение всех игроков",
    "all_debuff_kill_rand":    "Убить случайного игрока",

    "item_health_small":       "Малое исцеление",
    "item_health_med":         "Среднее исцеление",
    "item_health_big":         "Большое исцеление",
    "item_crystal":            "Кристалл",
    "item_nade_stun":          "Граната оглушающая",
    "item_nade_shock":         "Граната электрическая",
    "item_nade_expl":          "Граната взрывная",
    "item_nade_f1":            "Граната F1",
    "item_nade_duck_f1":       "Связка гранат",
    "item_mine_stun":          "Мина оглушающая",
    "item_mine_shock":         "Мина электрическая",
    "item_mine_expl":          "Мина Взрывная",
    "item_rubber_duck":        "Утка",
    "item_book_roll":          "Улучшение кувырка",
    "item_book_speed":         "Улучшение скорости",
    "item_book_energy":        "Улучшение энергии",
    "item_book_health":        "Улучшение здоровья",
    "item_book_range":         "Улучшение дальности",
    "item_book_strength":      "Улучшение силы",
    "item_book_jump":          "Улучшение прыжка",
    "item_drone_roll":         "Дрон кручения",
    "item_drone_gravity":      "Дрон гравитации",
    "item_drone_feather":      "Дрон легкости",
    "item_drone_energy":       "Дрон энергии",
    "item_drone_shield":       "Дрон щит",
    "item_sphere_gravity":     "Сфера гравитации",
    "item_frying_pan":         "Сковорода",
    "item_inflatable_hammer":  "Надувной молот",
    "item_sword":              "Меч",
    "item_baseball_bat":       "Бита",
    "item_sledge_hammer":      "Кувалда",
    "item_valuable_tracker":   "Искатель ценностей",
    "item_extraction_tracker": "Искатель эвакуации",
    "item_cart_small":         "Маленькая тележка",
    "item_cart_medium":        "Средняя тележка",
    "item_tranq":              "Транквилизатор",
    "item_handgun":            "Пистолет",
    "item_shotgun":            "Дробовик",

    "spawn_duck":              "Спавн утки",
    "spawn_spewer":            "Спавн извергающего",
    "spawn_upscream":          "Спавн с воплем",
    "spawn_alien":             "Спавн пришельца",
    "spawn_baby":              "Спавн младенца",
    "spawn_thinman":           "Спавн худого",
    "spawn_hidden":            "Спавн скрытого",
    "spawn_frog":              "Спавн лягушки",
    "spawn_bowtie":            "Спавн в галстуке",
    "spawn_huntsman":          "Спавн охотника",
    "spawn_trudge":            "Спавн медленного",
    "spawn_clown":             "Спавн клоуна",
    "spawn_robe":              "Спавн в мантии",
    "spawn_reaper":            "Спавн Жнеца",

    "empty_event":             "Пустое событие (нет действия)"
}

# Группировка кнопок по категориям
categories = {
    "Глобальные эффекты": [eid for eid in button_texts if eid.startswith("all_")],
    "Предметы": [eid for eid in button_texts if eid.startswith("item_")],
    "Спавн мобов": [eid for eid in button_texts if eid.startswith("spawn_")],
    "Прочее": [eid for eid in button_texts if eid == "empty_event"]
}

def start_tk_interface():
    global asyncio_loop, random_events_enabled_var, random_event_delay_var, probability_vars
    # Создаем окно
    root = tk.Tk()
    root.title("Интерфейс вызова событий")
    
    # Создаем главный фрейм с отступом
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    
    # Верхняя панель с настройками рандом эвентов (растянута по ширине)
    top_frame = ttk.Frame(main_frame)
    top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    
    # Переключатель включения/выключения рандом эвентов
    random_events_enabled_var = tk.BooleanVar(value=True)
    toggle = ttk.Checkbutton(top_frame, text="Включить рандом эвенты", variable=random_events_enabled_var)
    toggle.grid(row=0, column=0, padx=3, pady=3)
    
    # Поле ввода задержки (в секундах) для рандом эвентов
    random_event_delay_var = tk.StringVar(value="120")
    delay_label = ttk.Label(top_frame, text="Задержка (сек):")
    delay_label.grid(row=0, column=1, padx=3, pady=3)
    delay_entry = ttk.Entry(top_frame, width=5, textvariable=random_event_delay_var)
    delay_entry.grid(row=0, column=2, padx=3, pady=3)
    
    # Нижняя часть: левая панель – кнопки вызова событий, правая панель – настройки вероятностей
    # Левая панель с кнопками вызова событий
    left_frame = ttk.Frame(main_frame)
    left_frame.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
    
    row_index = 0
    for cat_name, event_ids in categories.items():
        frame = ttk.LabelFrame(left_frame, text=cat_name, padding="10")
        frame.grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        # Кнопки расположены в 4 столбца
        for idx, eid in enumerate(event_ids):
            r = idx // 4
            c = idx % 4
            btn = ttk.Button(frame, text=button_texts[eid],
                             command=lambda event_id=eid: button_callback(event_id))
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
        row_index += 1
    
    # Правая панель – настройки вероятностей
    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=1, column=1, sticky="ne", padx=5, pady=5)
    
    prob_title = ttk.Label(right_frame, text="Настройки вероятностей:")
    prob_title.grid(row=0, column=0, padx=3, pady=3, sticky="w")
    
    prob_row = 1
    # Для каждой категории создаём отдельный LabelFrame с вероятностями, располагая элементы в 4 столбца
    for cat_name, event_ids in categories.items():
        pf = ttk.LabelFrame(right_frame, text=cat_name, padding="10")
        pf.grid(row=prob_row, column=0, padx=5, pady=5, sticky="w")
        for idx, eid in enumerate(event_ids):
            # Определяем позицию: 4 элемента в строке
            row = idx // 6
            col = idx % 6
            # В каждой ячейке создаем свой контейнер для метки и поля ввода
            cell = ttk.Frame(pf)
            cell.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            lbl = ttk.Label(cell, text=button_texts[eid])
            lbl.pack()
            if eid not in probability_vars:
                probability_vars[eid] = tk.StringVar(value=str(probabilities.get(eid, 0)))
            entry = ttk.Entry(cell, width=5, textvariable=probability_vars[eid])
            entry.pack()
        prob_row += 1

    root.mainloop()

def button_callback(event_id: str):
    print(f"Кнопка нажата: {event_id}")
    if asyncio_loop is not None:
        asyncio.run_coroutine_threadsafe(trigger_event_by_id(event_id), asyncio_loop)
    else:
        print("Asyncio loop не запущен!")

async def start_server():
    global asyncio_loop
    asyncio_loop = asyncio.get_running_loop()
    # Запускаем Tkinter-интерфейс в отдельном потоке
    tk_thread = threading.Thread(target=start_tk_interface, daemon=True)
    tk_thread.start()
    
    async with websockets.serve(handle_connection, "127.0.0.1", 13715):
        print("WebSocket server running on ws://127.0.0.1:13715")
        await asyncio.gather(trigger_random_event())

if __name__ == "__main__":
    asyncio.run(start_server())
