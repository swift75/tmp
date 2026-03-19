from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Лексика"), KeyboardButton(text="📝 Практика")],
        [KeyboardButton(text="🏮 История Китая")],
    ],
    resize_keyboard=True,
)

lexic_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📖 Словарь HSK (работает медленно)"),
            KeyboardButton(text="🔑 Ключи (работает медленно)"),
        ],
        [
            KeyboardButton(text="📚 Теория"),
            KeyboardButton(text="🃏 Карточки"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ],
    resize_keyboard=True,
)

practice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📕 Игра со словами")],
        [KeyboardButton(text="📖 Игра с предложениями")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True,
)
