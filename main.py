
from datetime import date
import telebot
import datetime
from datetime import datetime
import messages 
import telegramcalendar
from retail import *
from telebot.types import CallbackQuery, Message, KeyboardButton, ReplyKeyboardMarkup
from db import DB

bot = telebot.TeleBot('5876007095:AAFH0NQZajgiG2lHSEby45JviTPm7hVdjho')
db = DB()

@bot.message_handler(commands=['start'])
def starter(message):
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = KeyboardButton(text="Отправить телефон",request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id,'Здравствуйте. Отправьте свой телефон через меню в верхнем правом углу экрана или нажав на кнопку ниже.', reply_markup=keyboard)
    
@bot.message_handler(content_types=['contact'])
def phone_saver(message: Message):
    phone = message.contact.phone_number
    poisk=curier(phone)
    user=db.get_by_id(message.chat.id,phone,poisk) 
    #добавить тут в базу данных
    markup = telebot.types.InlineKeyboardMarkup() 
    button1=telebot.types.InlineKeyboardButton(text='Cегодня', callback_data="today:")
    button2=telebot.types.InlineKeyboardButton(text='Календарь', callback_data="calendar:")
    markup.add(button1, button2)
    bot.send_message(chat_id=message.chat.id, text='Выберите', reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == "today")
def today(call: CallbackQuery):
    #id_cur = call.data.split(":")[1]
    id_cur=db.proverk_id(call.message.chat.id)
    #Считать айди через базу данных
    list_orders=ordersretail(id_cur,dateorders = date.today())
    if list_orders is not None:
        markup = telebot.types.InlineKeyboardMarkup() 
        markup.add(list_orders)
        bot.send_message(call.message.chat.id,'Выберите заказ',reply_markup=list_orders)
    if list_orders is None:
        bot.send_message(call.message.chat.id,'Заказы на данную дату отсутствуют')

@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == "calendar")
def calendar(call: CallbackQuery):
    now = datetime.now()
    chat_id = call.message.chat.id
    date = (now.year,now.month)
    current_shown_dates = {}
    current_shown_dates[chat_id] = date 
    text=messages.calendar_message
    markup = telegramcalendar.create_calendar(now.year,now.month).to_json()
    bot.send_message(call.message.chat.id, text, reply_markup=markup) 


#@bot.callback_query_handler(func=lambda call: call.data.split(';')[1] == "DAY")
@bot.callback_query_handler(func=lambda call: len(call.data.split(';')) >= 2 and call.data.split(';')[1] == "DAY")
def day(call: CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    calendar_data=datetime.strptime(call.data.partition('CALENDAR;DAY;')[2], '%Y;%m;%d').strftime('%Y-%m-%d')
    #id из базы данных
    id_cur=db.proverk_id(call.message.chat.id)
    list_orders=ordersretail(id_cur,dateorders = calendar_data)
    if list_orders is not None:
        markup = telebot.types.InlineKeyboardMarkup() 
        markup.add(list_orders.to_json())
        bot.send_message(call.message.chat.id,'Выберите заказ',reply_markup=list_orders)
    if list_orders is None:
        markup = telebot.types.InlineKeyboardMarkup()
        button1=telebot.types.InlineKeyboardButton(text='Календарь', callback_data="calendar:")
        markup.add(button1)
        bot.send_message(call.message.chat.id,'Заказы на данную дату отсутствуют',reply_markup=list_orders)
    
    
@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == "order")
def order(call: CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    order_id=call.data.split(':')[1]# айди заказа, без бд
    order_osn=order_one(order_id)
    url_yandex=retailcustomfild(order_id)
    markup = telebot.types.InlineKeyboardMarkup()
    button1=telebot.types.InlineKeyboardButton(text='Нет на месте', callback_data="Client_not_present:"+str(order_id))
    button2=telebot.types.InlineKeyboardButton(text='Фото', callback_data="photo:"+str(order_id))
    button3=telebot.types.InlineKeyboardButton(text='Комментарий', callback_data="comment:"+str(order_id))
    button4=telebot.types.InlineKeyboardButton(text='Карта', url=url_yandex)
    markup.add(button1, button2, button3, button4)
    bot.send_message(call.message.chat.id, order_osn, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == "Client_not_present")
def notpresent(call: CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    id_order = call.data.split(':')[1]
    cancelled=cancelorder(id_order)
    markup = telebot.types.InlineKeyboardMarkup()
    button1=telebot.types.InlineKeyboardButton(text='Календарь', callback_data="calendar:")
    markup.add(button1)
    if cancelled is not None:
        bot.send_message(call.message.chat.id, 'Заказ отменен', reply_markup=markup)
        
@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == "comment")
def comm(call: CallbackQuery):
    id_order = call.data.split(':')[1]
    bot.send_message(call.message.chat.id, 'Введите коментарий')
    @bot.message_handler(content_types=['text'])
    def after_text(message):
        cancelled=commentorder(id_order,message.text)
        if cancelled is not None:
            bot.send_message(call.message.chat.id, 'Комменатрий отправлен')

@bot.callback_query_handler(lambda query: query.data.split(":")[0] == 'photo')
def photo_catcher(call: CallbackQuery):
    user_id = call.from_user.id
    order_id=call.data.split(':')[1]
    bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text='Отправьте фотографию')
    bot.register_next_step_handler(call.message, proceed_photo, order_id, call.message.id)
    bot.answer_callback_query(call.id)

def proceed_photo(message, order_id, bots_msg):
    user_id = message.from_user.id
    bot.delete_message(chat_id=user_id, message_id=bots_msg)
    msg = bot.send_message(chat_id=user_id, text='⌛')  
    file_info = bot.get_file(message.photo[-1].file_id)
    file = bot.download_file(file_info.file_path)
    load_photo(order_id, file)
    if load_photo(order_id, file) is not None:
        markup = telebot.types.InlineKeyboardMarkup()
        button1=telebot.types.InlineKeyboardButton(text='Доставлен', callback_data="Delivered:"+str(order_id))
        markup.add(button1)
        bot.edit_message_text(chat_id=user_id, message_id=msg.id, text='Нажмите', reply_markup=markup)
 
@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == "Delivered")
def comm(call: CallbackQuery):
    id_order = call.data.split(':')[1]        
    Deliv=deliveredorder(id_order)
    if Deliv is not None:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            markup = telebot.types.InlineKeyboardMarkup()
            button1=telebot.types.InlineKeyboardButton(text='Календарь', callback_data="calendar:")
            markup.add(button1)
            bot.send_message(call.message.chat.id, 'Заказ доставлен', reply_markup=markup)
bot.polling(non_stop=True)