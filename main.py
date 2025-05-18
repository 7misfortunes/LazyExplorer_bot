from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import requests
import re
from datetime import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

IATA_TO_YANDEX = {
    "LED": "c2",
    "MOW": "c213"
    # добавляй по мере надобности
}

def parse_aviasales_url(url):
    if "avs.io" in url:
        try:
            r = requests.get(url, allow_redirects=False)
            url = r.headers["Location"]
        except:
            return "❌ Не удалось распаковать ссылку"

    match = re.search(r"([A-Z]{3})(\d{2})(\d{2})([A-Z]{3})(\d{2})?(\d{2})?", url)
    if not match:
        return "❌ Неверная ссылка"

    from_iata, day, month, to_iata, return_day, return_month = match.groups()
    from_id = IATA_TO_YANDEX.get(from_iata)
    to_id = IATA_TO_YANDEX.get(to_iata)
    if not from_id or not to_id:
        return "❌ Неизвестный город"

    year = datetime.now().year
    depart_date = f"{year}-{month}-{day}"
    base = f"https://travel.yandex.ru/avia/search/result/?fromId={from_id}&toId={to_id}&when={depart_date}&adult_seats=1&children_seats=0&infant_seats=0&klass=economy"

    if return_day and return_month:
        return_date = f"{year}-{return_month}-{return_day}"
        base += f"&return_date={return_date}&oneway=2"
    else:
        base += f"&oneway=1"

    return f"📍{to_iata} — {day}.{month}\n{base}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    result = parse_aviasales_url(url)
    await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
