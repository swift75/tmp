from aiogram import Router
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from keyboards import main_keyboard, lexic_keyboard, practice_keyboard
from consts import CARDS
import db
from consts import WORDS
from consts import SENTENCES
import random

router = Router()

WELCOME_TEXT = (
    "Доброго времени суток!\n\n"
    "Этот бот поможет в изучении китайского языка на уровне HSK-1 "
    "(Hànyǔ Shuǐpíng Kǎoshì — тест на знание китайского языка), "
    "т.е. начального.\n\n"
    "Бот включает в себя множество материалов для самостоятельного "
    "достижения основополагающего уровня китайского языка.\n\n"
    "Все материалы взяты из открытых источников и литературы.\n\n"
    "<a href=\"https://t.me/chinese_hsk1_theory/6\">Полезные материалы</a>"
)


def render_card(index: int) -> str:
    card = CARDS[index]
    text = f"🃏 <b>{card['title']}</b>\n\n"

    for entry in card["entries"]:
        text += (
            f"{entry['num']}. <b>{entry['word']}</b> ({entry['pinyin']}) — {entry['translation']}\n"
            f"例: {entry['example']}\n"
            f"{entry['example_pinyin']}\n"
            f"{entry['example_ru']}\n\n"
        )

    text += f"Карточка {index + 1} / {len(CARDS)}"
    return text


def make_cards_inline_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Предыдущая карточка", callback_data="prev_card"),
            InlineKeyboardButton(text="➡️ Следующая карточка", callback_data="next_card"),
        ]
    ])
    return kb


def make_word_options_inline(options: list) -> InlineKeyboardMarkup:
    buttons = []
    for i, opt in enumerate(options):
        buttons.append([InlineKeyboardButton(text=opt, callback_data=f"word_answer:{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def make_continue_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дальше", callback_data="word_next")]
    ])


def choose_unseen_word_for_user(user_id: int):
    if not WORDS:
        return None
    seen = set(db.get_seen_word_ids(user_id))
    candidates = [w for w in WORDS if w["id"] not in seen]
    if not candidates:
        return None
    return random.choice(candidates)


def make_options_for_word(correct_word: dict, max_options: int = 4):
    correct = correct_word["word"]
    all_chars = [w["word"] for w in WORDS if w["word"] != correct]
    distractors = random.sample(all_chars, k=min(max(0, max_options - 1), len(all_chars)))
    options = distractors + [correct]
    random.shuffle(options)
    correct_index = options.index(correct)
    return options, correct_index


@router.message(lambda message: message.text == "/start")
async def start_handler(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard, parse_mode="HTML")


@router.message(lambda message: message.text == "📘 Лексика")
async def lexic_handler(message: Message):
    await message.answer(
        "<b>Раздел «Лексика»</b>\n\n"
        "Тут вы можете найти все материалы, которые необходимы "
        "для изучения теоретической части начального уровня "
        "китайского языка.",
        reply_markup=lexic_keyboard,
        parse_mode="HTML"
    )


@router.message(lambda message: message.text == "⬅️ Назад")
async def back_handler(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard, parse_mode="HTML")


@router.message(lambda message: message.text == "📖 Словарь HSK (работает медленно)")
async def hsk_dict_handler(message: Message):
    try:
        await message.answer_document(
            document=FSInputFile("HSK1.pdf"),
            caption=(
                "📖 <b>Словарь HSK-1</b>\n\n"
                "Файл содержит базовую лексику уровня HSK-1.\n"
                "Рекомендуется использовать для заучивания и повторения."
            ),
            reply_markup=lexic_keyboard,
            parse_mode="HTML",
        )
    except Exception:
        await message.answer("", reply_markup=lexic_keyboard)


@router.message(lambda message: message.text == "🔑 Ключи(работает медленно)")
async def keys_handler(message: Message):
    try:
        await message.answer_document(
            document=FSInputFile("keys.pdf"),
            caption=(
                "🔑 Здесь вы найдете таблицу ключей, которая поможет вам лучше понимать структуру китайских иероглифов. HSK-1\n\n"
                "Использование ключей - это один из способов быстрого и эффективного изучения китайского языка. "
            ),
            reply_markup=lexic_keyboard,
            parse_mode="HTML",
        )
    except Exception:
        await message.answer("", reply_markup=lexic_keyboard)


@router.message(lambda message: message.text == "🃏 Карточки")
async def cards_handler(message: Message):
    user_id = message.from_user.id
    idx = db.get_user_index(user_id)
    db.set_user_index(user_id, idx)
    await message.answer(
        render_card(idx),
        reply_markup=make_cards_inline_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "next_card")
async def next_card_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    idx = db.get_user_index(user_id)
    idx += 1
    if idx >= len(CARDS):
        idx = 0
    db.set_user_index(user_id, idx)

    try:
        if callback.message:
            await callback.message.edit_text(
                render_card(idx),
                reply_markup=make_cards_inline_keyboard(),
                parse_mode="HTML",
            )
    except Exception:
        if callback.message:
            await callback.message.answer(
                render_card(idx), reply_markup=make_cards_inline_keyboard(), parse_mode="HTML"
            )

    await callback.answer()


@router.callback_query(lambda c: c.data == "prev_card")
async def prev_card_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    idx = db.get_user_index(user_id)
    idx -= 1
    if idx < 0:
        idx = len(CARDS) - 1
    db.set_user_index(user_id, idx)

    try:
        if callback.message:
            await callback.message.edit_text(
                render_card(idx),
                reply_markup=make_cards_inline_keyboard(),
                parse_mode="HTML",
            )
    except Exception:
        if callback.message:
            await callback.message.answer(
                render_card(idx), reply_markup=make_cards_inline_keyboard(), parse_mode="HTML"
            )

    await callback.answer()


@router.message(lambda message: message.text == "📝 Практика")
async def practice_menu_handler(message: Message):
    await message.answer(
        "Выберите режим практики:",
        reply_markup=practice_keyboard
    )


@router.message(lambda message: message.text == "📕 Игра со словами")
async def word_game_handler(message: Message):
    user_id = message.from_user.id
    word = choose_unseen_word_for_user(user_id)
    if word is None:
        await message.answer(
            "Вы просмотрели все слова в этом словаре! Хотите начать заново?",
            reply_markup=practice_keyboard
        )
        return

    options, correct_index = make_options_for_word(word, max_options=4)
    db.set_game(user_id, word["id"], options, correct_index)

    text = f"Перевод: <b>{word['translation_ru']}</b>\n\n<b>Выберите иероглиф:</b>"
    await message.answer(
        text,
        reply_markup=make_word_options_inline(options),
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data.startswith("word_answer:"))
async def word_answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    game = db.get_game(user_id)
    if game is None:
        await callback.answer("Игра не запущена. Нажмите «Игра со словами».", show_alert=True)
        return

    try:
        _, chosen_str = callback.data.split(":", 1)
        chosen_idx = int(chosen_str)
    except Exception:
        await callback.answer("Неправильные данные.", show_alert=True)
        return

    options = game["options"]
    correct_idx = game["correct_index"]
    word_id = game["current_word_id"]

    word = next((w for w in WORDS if w["id"] == word_id), None)
    if word is None:
        await callback.answer("Ошибка: слово не найдено.", show_alert=True)
        db.clear_game(user_id)
        return

    db.add_seen_word(user_id, word_id)

    is_correct = (chosen_idx == correct_idx)
    header = "✅ Правильно!" if is_correct else "❌ Неправильно."

    result_text = (
        f"{header}\n\n"
        f"Слово: <b>{word['word']}</b>\n"
        f"Пиньинь: {word.get('pinyin', '')}\n"
        f"Перевод: {word.get('translation_ru', '')}\n\n"
    )
    db.clear_game(user_id)

    try:
        if callback.message:
            await callback.message.edit_text(
                result_text,
                reply_markup=make_continue_keyboard(),
                parse_mode="HTML"
            )
    except Exception:
        if callback.message:
            await callback.message.answer(
                result_text,
                reply_markup=make_continue_keyboard(),
                parse_mode="HTML"
            )

    await callback.answer()


@router.callback_query(lambda c: c.data == "word_next")
async def word_next_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    word = choose_unseen_word_for_user(user_id)
    if word is None:
        try:
            if callback.message:
                await callback.message.edit_text(
                    "Вы просмотрели все слова в этом словаре! Хотите начать заново?",
                    reply_markup=None
                )
        except Exception:
            if callback.message:
                await callback.message.answer("Вы просмотрели все слова в этом словаре! Хотите начать заново?")
        await callback.answer()
        return

    options, correct_index = make_options_for_word(word, max_options=4)
    db.set_game(user_id, word["id"], options, correct_index)

    text = f"Перевод: <b>{word['translation_ru']}</b>\n\nВыберите иероглиф:"
    try:
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=make_word_options_inline(options),
                parse_mode="HTML"
            )
    except Exception:
        if callback.message:
            await callback.message.answer(text, reply_markup=make_word_options_inline(options), parse_mode="HTML")

    await callback.answer()


def options_keyboard(options, prefix):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=o, callback_data=f"{prefix}:{i}")]
            for i, o in enumerate(options)
        ]
    )


def next_keyboard(prefix):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Дальше", callback_data=prefix)]
        ]
    )


def choose_sentence(user_id):
    seen = set(db.get_seen_sentence_ids(user_id))
    available = [s for s in SENTENCES if s["id"] not in seen]
    return random.choice(available) if available else None


async def send_sentence_question(message: Message, user_id: int):
    sentence = choose_sentence(user_id)

    if not sentence:
        await message.answer("Все предложения пройдены 🎉", reply_markup=practice_keyboard)
        return

    translations = [s["translation_ru"] for s in SENTENCES if s["id"] != sentence["id"]]
    wrong = random.sample(translations, k=min(3, len(translations)))
    options = wrong + [sentence["translation_ru"]]
    random.shuffle(options)

    correct_index = options.index(sentence["translation_ru"])

    db.set_sentence_game(user_id, sentence["id"], options, correct_index)

    await message.answer(
        f"Выберите перевод:\n\n<b>{sentence['sentence']}</b>\n{sentence['pinyin']}",
        reply_markup=options_keyboard(options, "sent_ans"),
        parse_mode="HTML",
    )


@router.message(lambda m: m.text == "📖 Игра с предложениями")
async def sentence_game_start(message: Message):
    await send_sentence_question(message, message.from_user.id)


@router.callback_query(lambda c: c.data and c.data.startswith("sent_ans"))
async def sentence_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    game = db.get_sentence_game(user_id)

    if not game:
        await callback.answer()
        return

    try:
        idx = int(callback.data.split(":")[1])
    except Exception:
        await callback.answer()
        return

    correct = game["correct_index"]
    sentence = next(s for s in SENTENCES if s["id"] == game["sentence_id"])

    is_correct = idx == correct

    db.add_seen_sentence(user_id, sentence["id"])
    db.clear_sentence_game(user_id)

    header = "✅ <b>Правильно!</b>\n\n" if is_correct else "❌ <b>Неправильно.</b>\n\n"

    result_text = (
            header +
            f"<b>{sentence['sentence']}</b>\n"
            f"{sentence['pinyin']}\n"
            f"{sentence['translation_ru']}"
    )

    try:
        if callback.message:
            await callback.message.edit_text(result_text, parse_mode="HTML")
        else:
            await callback.message.answer(result_text, parse_mode="HTML")
    except Exception:
        if callback.message:
            await callback.message.answer(result_text, parse_mode="HTML")

    await callback.answer()

    if callback.message:
        await send_sentence_question(callback.message, user_id)


@router.callback_query(lambda c: c.data == "sent_next")
async def sentence_next(callback: CallbackQuery):
    if callback.message:
        await send_sentence_question(callback.message, callback.from_user.id)
    await callback.answer()

@router.message(lambda message: message.text == "📚 Теория")
async def theory_handler(message: Message):
    await message.answer(
        (
            "📚 <b>Теоретические уроки HSK-1</b>\n\n"

            "<a href='https://t.me/chinese_hsk1_theory/9'>Урок 1. Общая характеристика</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/12'>Урок 2. Система пиньинь</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/15'>Урок 3. Тоновая система</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/17'>Урок 4. Черты иероглифов</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/19'>Урок 5. Порядок написания черт</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/20'>Урок 6. Простые иероглифы</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/21'>Урок 7. Личные местоимения</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/22'>Урок 8. Множественное число местоимений</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/23'>Урок 9. Глагол 是</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/24'>Урок 10. Отрицание 不</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/25'>Урок 11. Вопросительная частица 吗</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/27'>Урок 12. Порядок слов в предложении</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/28'>Урок 13. Глаголы действия</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/29'>Урок 14. Место действия</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/30'>Урок 15. Время действия</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/31'>Урок 16. Числа и счёт</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/32'>Урок 17. Счётное слово 个</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/33'>Урок 18. Вопросительные слова</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/34'>Урок 19. Частица 的</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/35'>Урок 20. Глагол 有</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/36'>Урок 21. Простые прилагательные</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/37'>Урок 22. Наречие 很</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/38'>Урок 23. Отрицание 没</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/39'>Урок 24. Модальный глагол 会</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/40'>Урок 25. Модальный глагол 能</a>\n"
            "<a href='https://t.me/chinese_hsk1_theory/41'>Урок 26. Простые вопросы без 吗</a>"
        ),
        reply_markup=lexic_keyboard,
        parse_mode="HTML",
    )


@router.message(lambda message: message.text == "🏮 История Китая")
async def china_history_handler(message: Message):
    await message.answer(
        (
            "🏮 <b>История Китая и китайского языка</b>\n\n"
            "Ниже приведены каналы со всей информацией об истории Китая и языка:\n\n"
            "👉 <a href='https://t.me/dnevnik_kitaista'>Канал 1</a>\n"
            "👉 <a href='https://t.me/chinahistoria'>Канал 2</a>"
        ),
        parse_mode="HTML"
    )
