# -*- coding: utf-8 -*-
import telebot
from telebot import types
import config as cfg 


bot = telebot.TeleBot(cfg.token)

pin_user = [59863436]


@bot.message_handler(commands = ['ping'])
def ping(message):
	bot.send_message(message.chat.id, "I'm alive")


@bot.message_handler(content_types = ['text'])
def reply(message):
	if message.from_user.id in pin_user:
		bot.pin_chat_message(message.chat.id, message.message_id)

if __name__ == '__main__':
	bot.polling(none_stop=True)

