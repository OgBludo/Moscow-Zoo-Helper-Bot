from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_result_buttons(result: str):
    share_text = f" - Здесь я узнал свое тотемное животное ☘️\n\n Это - {result.capitalize()} 🏆❗️\n\n Узнай, кто ты: https://t.me/@msc_zoo_help_bot?start=result"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Узнать об опеке 🔎", url="https://moscowzoo.ru/about/guardianship")],
            [InlineKeyboardButton(text="Связаться с сотрудником 📲", callback_data="contact")],
            [InlineKeyboardButton(text="Попробовать ещё раз ❓", callback_data="restart")],
            [InlineKeyboardButton(
                text="🔗 Поделиться результатом",
                switch_inline_query=share_text
            )],
        ]
    )


def get_answer_buttons(question_index: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=str(i + 1), callback_data=f"answer:{question_index}:{i}")]
        for i in range(4)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="🐾 Начать викторину"),
             KeyboardButton(text="🌐 Перейти на сайт")],
            [KeyboardButton(text="ℹ️ Общая информация"),
             KeyboardButton(text="💬 Оставить отзыв")],
        ]
    )
