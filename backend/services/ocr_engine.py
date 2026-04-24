import asyncio
import ollama
from core.config import settings

OCR_MODEL = settings.OCR_MODEL
PROMPT = '''Тебе должно прийти изображение с рецептом лекарств. Ты должен образовать список формата JSON, элементы которого представляют из себя следующее:
{
    "name": <название препарата (например "Ибупрофен")>,
    "dosage": <Здесь дозировка (например "100мг"), если не указано то "">,
    "instructions": <Здесь дополнительные инструкции, может быть null>,
    "start_time": <дата и время начала приема в формате ISO 8601 (например "2026-04-23T08:00:00Z"), если не указана - используй текущую>,
    "end_time": <дата и время окончания приема в формате ISO 8601 (например "2026-05-23T08:00:00Z"), может быть null>,
    "nday": <здесь количество дней пропусков между днями приема (например 0, если лекарство нужно принимать каждый день, 1 если через день и так далее)>,
    "times": <список дат и времен приема для первого дня в формате ISO 8601 (например ["2026-04-23T08:00:00Z", "2026-04-23T20:00:00Z"]). Если не можешь определить время, ставь предположительное>
}

Имей ввиду:
    1. р/д значит "раз в день". Например "5 р/д" будет означать, что лекарство принимается 5 раз в день.
    2. внимательно следи за тем, указаны ли даты начала и окончания приема для одного лекарства или для всех.
'''
ANS_TIMEOUT = 40.

client = ollama.AsyncClient(host=settings.OLLAMA_HOST)

async def process_image(image: bytes) -> str | None:
    msgs = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": "Вот рецепт лекарств. Если ты не можешь здесь ничего распознать, напиши просто 'Нет'", "images": [image]}
    ]
    try:
        chat = await asyncio.wait_for(client.chat(model = OCR_MODEL, messages=msgs), timeout=ANS_TIMEOUT)
        cont = chat.message.content
        if cont == 'Нет':
            return None
        if cont is not None:
            cont = cont.replace("```json", "").replace("```", "")
        return cont
    except asyncio.TimeoutError:
        return None
