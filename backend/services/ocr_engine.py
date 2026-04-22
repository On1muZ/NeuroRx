import asyncio
import ollama

OCR_MODEL = 'qwen2.5vl:7b'
PROMPT = '''Тебе должно прийти изображение с рецептом лекарств. Ты должен образовать список формата JSON, элементы которого представляют из себя следующее:
{
    "medication_name": <название препарата (например "Ибупрофен")>,
    "dosage": <Здесь дозировка (например 100мг), если не указано то null>,
    "instructions": <Здесь дополнительные инструкции, может быть null>,
    "start_date": <дата начала приема (например 2026-04-22)>,
    "end_date": <дата окончания приема (например 2026-05-22)>,
    "nday": <здесь количество дней пропусков между днями приема (например 0, если лекарство нужно принимать каждый день, 1 если лекарство нужно принимать через день и так далее)>,
    "amount": <количество приемов в день>,
    "times": <список времен, во сколько нужно принимать лекарства. Самое главное, чтобы длина этого списка была равна amount>
}

Имей ввиду:
    1. р/д значит "раз в день". Например "5 р/д" будет означать, что лекарство принимается 5 раз в день.
    2. внимательно следи за тем, указаны ли даты начала и окончания приема для одного лекарства или для всех.
    3. Времена в "times" могу находятся в пределах от 8 до 24 часов
'''
ANS_TIMEOUT = 40.

client = ollama.AsyncClient()

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
