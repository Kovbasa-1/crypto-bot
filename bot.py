import telebot
import requests

TOKEN = '7516013242:AAH2_RXgCOFPb5Gc_ts-2zEgGJmnAehRsrA'
CHAT_ID = 634460073
bot = telebot.TeleBot(TOKEN)

price_targets = {
    'BTC': {'buy': 110000},
    'UNI': {'buy': 8.5, 'sell': [11.5, 13, 15]},
    'LINK': {'buy': 15, 'sell': 25},
    'ENA': {'buy': 0.3, 'sell': 0.55}
}

def get_price(symbol):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data.get(symbol, {}).get('usd', None)

def check_action(symbol, price):
    tg = price_targets.get(symbol.upper())
    if not tg:
        return ''
    action = ''
    if 'buy' in tg and price <= tg['buy']:
        action += 'Пора купувати'
    elif 'sell' in tg:
        if isinstance(tg['sell'], list):
            for s in tg['sell']:
                if price >= s:
                    action += f'Пора продавати ({s}$+)\n'
        elif price >= tg['sell']:
            action += 'Пора продавати'
    else:
        action = 'Тримати'
    return action.strip()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привіт! Я крипто-бот. Обери команду:', reply_markup=main_keyboard())

@bot.message_handler(commands=['ціна'])
def price_check(message):
    prices = {
        'bitcoin': 'BTC',
        'uniswap': 'UNI',
        'chainlink': 'LINK',
        'ethena': 'ENA'
    }
    msg = ''
    for key, symbol in prices.items():
        price = get_price(key)
        if price:
            msg += f'{symbol}: ${price:.3f} - {check_action(symbol, price)}\n'
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['підказка', 'help'])
def show_help(message):
    msg = (
        "Пояснення:\n"
        "/ціна - показати актуальні ціни та сигнали\n\n"
        "Коли купувати:\n"
        "- BTC < $110,000\n"
        "- UNI < $8.5\n"
        "- LINK < $15\n"
        "- ENA < $0.3\n\n"
        "Коли продавати:\n"
        "- UNI > $11.5, $13, $15+\n"
        "- LINK > $25\n"
        "- ENA > $0.55"
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/ціна', '/підказка')
    return markup

bot.polling(none_stop=True)