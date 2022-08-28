import requests
import vk_api
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from users_db import *


class ChatBotVK:
    def __init__(self):
        print('Создан Бот')
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message):
        """отправка сообщений"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10**7), })

    def get_name(self, user_id):
        """имя пользователя"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_id': user_id,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_dict = response['response']
            for i in info_dict:
                for key, value in i.items():
                    first_name = i.get('first_name')
                    return first_name
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def get_sex(self, user_id):
        """Пол пользователя, замена на противоположный"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_id': user_id,
                  'fields': 'sex',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_list = response['response']
            for i in info_list:
                if i.get('sex') == 2:
                    get_sex = 1
                    return get_sex
                elif i.get('sex') == 1:
                    get_sex = 2
                    return get_sex
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def lowest_age(self, user_id):
        """Нижняя граница возраста"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_id': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_list = response['response']
            for i in info_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in info_list:
                self.write_msg(user_id, 'Введите нижний порог возраста (минимально - 18 лет): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def highest_age(self, user_id):
        """Верхняя граница возраста"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_list = response['response']
            for i in info_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in info_list:
                self.write_msg(user_id, 'Введите верхний порог возраста (максимально - 100): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def get_city(self, user_id, city_name):
        """Id города по названию"""
        url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': user_token,
                  'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_list = response['response']
            cities_list = info_list['items']
            for i in cities_list:
                get_city_name = i.get('title')
                if get_city_name == city_name:
                    get_city_id = i.get('id')
                    return int(get_city_id)
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def find_city_name(self, user_id):
        """Город пользователя"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'fields': 'city',
                  'user_ids': user_id,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            info_dict = response['response']
            for i in info_dict:
                if 'city' in i:
                    city = i.get('city')
                    vk_id = str(city.get('id'))
                    return vk_id
                elif 'city' not in i:
                    self.write_msg(user_id, 'Введите ваш город: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.cities(user_id, city_name)
                            if id_city != '' or id_city != None:
                                return str(id_city)
                            else:
                                break
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def find_pair(self, user_id):
        """Поиск человека, подходящего по параметрам"""
        url = f'https://api.vk.com/method/users.search'
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age_from': self.lowest_age(user_id),
                  'age_to': self.highest_age(user_id),
                  'city': self.find_city_name(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': '1' or '6',
                  'count': 500}
        repl = requests.get(url, params=params)
        response = repl.json()
        try:
            dict_1 = response['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def get_photos_id(self, user_id):
        """Id фотографии в обратном порядке"""
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'access_token': user_token,
                  'type': 'album',
                  'owner_id': user_id,
                  'extended': 1,
                  'count': 25,
                  'v': '5.131'}
        repl = requests.get(url, params=params)
        photos = dict()
        response = repl.json()
        try:
            dict_1 = response['response']
            list_1 = dict_1['items']
            for i in list_1:
                photo_id = str(i.get('id'))
                photos_likes = i.get('likes')
                if photos_likes.get('count'):
                    likes = photos_likes.get('count')
                    photos[likes] = photo_id
            list_of_ids = sorted(photos.items(), reverse=True)
            return list_of_ids
        except KeyError:
            self.write_msg(user_id, 'Ошибка, не хватает данных, введите токен в user_token')

    def get_photo_1(self, user_id):
        """Получение id фотографии_1"""
        photos_list = self.get_photos_id(user_id)
        count = 0
        for i in photos_list:
            count += 1
            if count == 1:
                return i[1]

    def get_photo_2(self, user_id):
        """Получение id фотографии_2"""
        photos_list = self.get_photos_id(user_id)
        count = 0
        for i in photos_list:
            count += 1
            if count == 2:
                return i[1]

    def get_photo_3(self, user_id):
        """Получение id фотографии_3"""
        photos_list = self.get_photos_id(user_id)
        count = 0
        for i in photos_list:
            count += 1
            if count == 3:
                return i[1]

    def send_photo_1(self, user_id, message, shift):
        """Отправка фотографии_1"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(shift)}_{self.get_photo_1(self.person_id(shift))}',
                                         'random_id': 0})

    def send_photo_2(self, user_id, message, shift):
        """Отправка фотографии_2"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(shift)}_{self.get_photo_2(self.person_id(shift))}',
                                         'random_id': 0})

    def send_photo_3(self, user_id, message, shift):
        """Отправка фотографии_3"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(shift)}_{self.get_photo_3(self.person_id(shift))}',
                                         'random_id': 0})

    def find_persons(self, user_id, shift):
        self.write_msg(user_id, self.found_person_info(shift))
        self.person_id(shift)
        insert_data_seen_users(self.person_id(shift), shift)  # shift
        self.get_photos_id(self.person_id(shift))
        self.send_photo_1(user_id, 'Фото номер 1', shift)
        if self.get_photo_2(self.person_id(shift)) != None:
            self.send_photo_2(user_id, 'Фото номер 2', shift)
            self.send_photo_3(user_id, 'Фото номер 3', shift)
        else:
            self.write_msg(user_id, f'Больше фото нет')

    def found_person_info(self, shift):
        """Информация о подобранном пользователе"""
        person_tuple = select(shift)
        person_list = []
        for i in person_tuple:
            person_list.append(i)
        return f'{person_list[0]} {person_list[1]}, ссылка - {person_list[3]}'

    def person_id(self, shift):
        """Id подобранного пользователя"""
        person_tuple = select(shift)
        person_list = []
        for i in person_tuple:
            person_list.append(i)
        return str(person_list[2])


bot = ChatBotVK()
