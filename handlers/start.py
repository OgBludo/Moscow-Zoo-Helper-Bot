from aiogram import Router, types
from aiogram.filters import Command

from keyboards.inline import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def start_handler(msg: types.Message):
    photo = types.FSInputFile(f"images/preview.jpg")
    await msg.answer_photo(
        photo,
        caption="Привет, друг! 🐾\n\n"
                "Добро пожаловать в мир удивительных животных Московского зоопарка! 🌿\n\n"
                "Здесь ты можешь пройти викторину, узнать о программе опеки и заглянуть за кулисы зоопарка. ✨",
        reply_markup=get_main_keyboard()
    )
