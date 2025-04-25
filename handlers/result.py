from aiogram import Router, types
from utils.scoring import get_result
from keyboards.inline import get_result_buttons

router = Router()


async def show_result(msg: types.Message, scores: dict):
    result = get_result(scores)
    try:
        photo = types.FSInputFile(f"images/{result}.jpg")
    except:
        photo = None
    text = f"Ты — {result.capitalize()}! 🎉\nЭто удивительное существо из Московского зоопарка!"
    if photo:
        await msg.answer_photo(photo, caption=text, reply_markup=get_result_buttons())
    else:
        await msg.answer(text, reply_markup=get_result_buttons())
