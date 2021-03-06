# -*- coding: utf-8 -*-
import telebot
from telebot import types
import config as cfg 
from peewee import *
import dhash
from wand.image import Image
import datetime
import distance
import os
from pymorphy2 import MorphAnalyzer

# https://habrahabr.ru/post/120562/


bot = telebot.TeleBot(cfg.token)
db = SqliteDatabase('bot.db')

uid = lambda m: m.from_user.id
from_chat = lambda m: m.forward_from.id
# from_user = lambda m: 
# forward_message = lambda m: m.


class BaseModel(Model):
	class Meta:
		database = db

class Photo(BaseModel):
	chat_id			= IntegerField()
	message_id		= IntegerField()
	photo_hash		= TextField()


class Message(BaseModel):
	message_id = IntegerField(primary_key = True)
	text 	   = TextField()
	timestamp  = DateTimeField(default = datetime.datetime.now)


class Repost(BaseModel):
	chat_id			= IntegerField()
	message_id 		= IntegerField()
	from_chat		= IntegerField()
	from_chat_type  = TextField()
	user_id			= IntegerField()
	timestamp 		= IntegerField()
	forward_text	= TextField()

	class Meta:
		primary_key = CompositeKey("from_chat", "user_id", "timestamp", "forward_text")



def check_pin(message):
	pin_user = [59863436] # Эмиль (@litleleprikon)
	if message.from_user.id in pin_user:
		bot.pin_chat_message(message.chat.id, message.message_id)


def save_photo(message): 
	fileID = message.photo[-1].file_id
	file_info = bot.get_file(fileID)
	downloaded_file = bot.download_file(file_info.file_path)
	photo_name = "{}_{}.jpg".format(message.chat.id, message.message_id)
	with open("./photo/{}".format(photo_name), 'wb') as new_file:
		new_file.write(downloaded_file)
		new_file.close()
	return photo_name



@bot.message_handler(commands = ['init'])
def init(m):
	Photo.create_table(fail_silently = True)
	Message.create_table(fail_silently = True)
	Repost.create_table(fail_silently = True)




@bot.message_handler(commands = ['ping'])
def ping(message):
	bot.send_message(message.chat.id, "I'm alive")


@bot.message_handler(content_types = ['new_chat_members'])
def new_member(m):
	sex = 'male'
	first_name = m.user.first_name
	morph = MorphAnalyzer(first_name)
	person = morph.parse(first_name)[0]
	if person.tag.gender == 'femn':
		sex = 'female'

	if sex == 'male':
		bot.send_message(m.chat.id, "Пошёл нахуй", reply_to_message_id = m.message_id)
	else:
		bot.send_message(m.chat.id, "Пошла нахуй", reply_to_message_id = m.message_id)



@bot.message_handler(content_types = ['text'])
def reply_to_text(m):
	n =1
	# check_pin(m)
	# print(m)




@bot.message_handler(content_types = ['photo'])
def reply_to_photo(m):
	# check_pin(m)
	# print(m)
	photo_name = save_photo(m)
	with Image(filename='./photo/{}'.format(photo_name)) as image:
	    row, col = dhash.dhash_row_col(image)
	photo_hash = dhash.format_hex(row, col)
	os.remove('./photo/{}'.format(photo_name))
	# print(photo_hash)
	exist = 0
	for row in Photo.select().where(Photo.chat_id == m.chat.id):
		hd = distance.hamming(photo_hash, row.photo_hash)
		# print(hd, photo_hash, row.photo_hash)
		if photo_hash == row.photo_hash:
			exist = 1
			bot.send_message(row.chat_id, "Уже было", reply_to_message_id=row.message_id)
			return True
	
	for row in Photo.select().where(Photo.chat_id == m.chat.id):
		hd = distance.hamming(photo_hash, row.photo_hash)			
		if hd < 6:
			bot.send_message(row.chat_id, "Похоже, что уже было", reply_to_message_id=row.message_id)
	Photo.create(chat_id = m.chat.id, message_id = m.message_id, photo_hash = photo_hash)	




	



if __name__ == '__main__':
	bot.polling(none_stop=True)

