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

# https://habrahabr.ru/post/120562/


bot = telebot.TeleBot(cfg.token)
db = SqliteDatabase('bot.db')

uid = lambda m: m.from_user.id


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




@bot.message_handler(commands = ['ping'])
def ping(message):
	bot.send_message(message.chat.id, "I'm alive")


@bot.message_handler(content_types = ['text'])
def reply_to_text(m):
	n = 1
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
	# print(photo_hash)
	exist = 0
	for row in Photo.select().where(Photo.chat_id == m.chat.id):
		hd = distance.hamming(photo_hash, row.photo_hash)
		# print(hd, photo_hash, row.photo_hash)
		if photo_hash == row.photo_hash:
			exist = 1
			bot.send_message(row.chat_id, "Уже было", reply_to_message_id=row.message_id)
		elif hd < 6:
			bot.send_message(row.chat_id, "Похоже, что уже было", reply_to_message_id=row.message_id)
	if exist == 0:
		Photo.create(chat_id = m.chat.id, message_id = m.message_id, photo_hash = photo_hash)
	os.remove('./photo/{}'.format(photo_name))




	



if __name__ == '__main__':
	bot.polling(none_stop=True)

