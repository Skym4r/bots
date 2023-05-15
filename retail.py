import retailcrm 
import telebot
import requests
import json

client = retailcrm.v5('https://astraflo.retailcrm.ru','nzZBf9ItHjkSL5KWRPb4AwlCXH0AxGAN') 


def curier(numb):
    couriers = client.couriers().get_response()
    for courier in couriers['couriers']:
        #print(courier['phone']['number'])
        if courier['phone']['number'] == numb:
            id_cur=courier['id']
            return id_cur

def ordersretail(id,dateorders):
    result = client.orders(filters={'extendedStatus': 'send-to-delivery','createdAtFrom':dateorders,'createdAtTo':dateorders, 'deliveryTypes':'courier','couriers': [id]}, limit=100)
    orders=result.get_response()['orders']
    number=[]
    order_id=[]
    if len(orders):
        for order in orders:
            order_id.append(order['id'])
            number.append(order['number']) 
        markup = telebot.types.InlineKeyboardMarkup() 
        butt1=[telebot.types.InlineKeyboardButton(text=str(x), callback_data="order:"+str(z) )for x,z in zip(number,order_id)]
        return markup.add(*butt1)

def retailcustomfild(id):
    order = client.order(id, uid_type='id').get_response()['order']
    #order = answer.get_response()['order']
    url=order["customFields"]['ssylka_iandeks']
    return url


def order_one(id):
    order = client.order(id, uid_type='id').get_response()['order']
    #order = answer.get_response()['order']
    items = assign_order(id)
    name=""
    if 'lastName' in order.keys():
        name += order['lastName'] + " "
    if 'firstName' in order.keys():
        name += " " + order['firstName'] + " "
    if 'patronymic' in order.keys():
        name += " " + order['patronymic'] + " "
    if 'date' in order['delivery'].keys(): 
        adress = "Дата доставки: " + str(order['delivery']['date'])
    else: 
        adress = "Дата доставки не указана"
    if 'time' in order['delivery'].keys():
        vremia = " от %s до %s" % (order['delivery']['time']['from'], order['delivery']['time']['to'])
    else: 
        vremia = " Время доставки не указано"  
    if 'text' in order['delivery']['address'].keys():                   
        dom = order['delivery']['address']['text'] 
    else: 
        dom = " Адрес не указан"
    if 'phone' in order.keys():
        phone = order['phone']
    else:
        phone =" отсутствует"         
    if 'managerComment' in order.keys():
        managerComment = order['managerComment'] 
    else:
        managerComment = "отсутствует" 
    text="Информация о заказе" +"\nНомер заказа: " + str(order['number']) + "\nФИО: " + str(name)+ "\nАдрес: " +  str(adress) + str(vremia) +str(dom) + "\nТелефон заказчика: " + str(phone)+"\nТовар: " + str(items) + "\nКомментарий к доставке: " + str(managerComment)
    return text
    
def assign_order(order_id):
    answer = client.order(uid=order_id, uid_type='id')
    order = answer.get_response()['order']
    order['status'] = 'delivery'
    client.order_edit(order, uid_type='id', site=order['site'])
    string = ""
    for it in order['items']:
        string += "%s : %s\n" % (it['offer']['displayName'], it['quantity'])
    return string

def cancelorder(id):
    order = client.order(uid=id, uid_type='id').get_response()['order']
    #order=result.get_response()['order']
    site=order['site']
    orderedit={
        'status':'poluchatelia-net-na-meste',
        'id':id
            }
    result = client.order_edit(orderedit,'id',site).get_response()
    return result


def commentorder(id,mes):
    order = client.order(uid=id, uid_type='id').get_response()['order']
    #order=result.get_response()['order']
    site=order['site']
    orderedit={
        'customFields':{'kommentarii_operatora':mes},
        'id':id
            }
    result = client.order_edit(orderedit,'id',site).get_response()
    return result



def deliveredorder(id):
    order = client.order(uid=id, uid_type='id').get_response()['order']
    #order=result.get_response()['order']
    site=order['site']
    orderedit={
        'status':'delivered',
        'id':id
            }
    result = client.order_edit(orderedit,'id',site).get_response()
    return result
    

def load_photo(order_id, file):
    #answer = client.files_upload(file_path, order['site'])

    url = '%s/api/v5/files/upload?apiKey=%s' % ('https://astraflo.retailcrm.ru', 'nzZBf9ItHjkSL5KWRPb4AwlCXH0AxGAN')

    response = requests.post(
        url=url,
        data=file
    )
    data = response.json()
    file = data['file']

    #file = answer.get_response()['file']
    answer = client.file(file['id'])
    file = answer.get_response()['file']
    file['filename'] = 'Отчет курьера'
    file['attachment'] = [
        {'order': {'id': order_id}}
    ]

    files_edit=client.files_edit(file)
    return files_edit