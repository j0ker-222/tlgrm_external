#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import socket
import telebot
import shutil
import netifaces
import subprocess
from telebot import types
from os.path import exists
from logging import basicConfig,INFO,info


# Default global variables
ALLOW_ID = ['']
BOT = telebot.TeleBot('')
IPTABLES_FILE = "/etc/network/iptables"

basicConfig(filename="bot.log", level=INFO)
info(":START SCRIPT at " + time.asctime())

# Filter access to chat BOT with improvisation of workflow
@BOT.message_handler(func=lambda message: str(message.chat.id) not in ALLOW_ID)
def some(message):
  info(":DROP id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  """ Send messages for new accounts """
  if message.text == "/start":
    BOT.send_message(message.chat.id, "Hi, welcome.\nIf you got questions print /help")
  elif message.text == "/help":
      BOT.send_message(message.from_user.id, "Temporary in testing mode.\nAll features is currently in development.")
  else:
      BOT.send_message(message.from_user.id, "Sorry, I don't understand you.\nPlease print /help.")

##
# COMMANDS
##

# First message at start BOT usage
@BOT.message_handler(commands=['start'])
def get_text_messages(message):
  BOT.send_message(message.from_user.id, "Greetings.\n\nStart to using - /go\nCall help pages - /help")

# Correct workflow for members of MLI
@BOT.message_handler(commands=['help'])
def get_text_messages(message):
  with open('/usr/local/bin/helper/help_message.lst', 'r') as help_msg:
    help_text = help_msg.read()
  BOT.send_message(message.from_user.id, help_text, parse_mode="markdown")

# Show IP address of server
@BOT.message_handler(commands=['ip'])
def get_text_messages(message):
  info(":ACCEPT(get ip) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  ip = netifaces.ifaddresses('ens3')[netifaces.AF_INET][0]['addr']
  BOT.send_message(message.from_user.id, ip)

# Add ip to iptables to allow access over SSH
# 1 step
@BOT.message_handler(commands=['ssh'])
def get_text_messages(message):
  info(":ACCEPT(get ip) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  msg = BOT.send_message(message.from_user.id, "Enter IP address to allow the access:")
  BOT.register_next_step_handler(msg, iptables_add_ssh_step)

# 2 step
def iptables_add_ssh_step(message):
  ip_addr_data = message.text.split(' ')[0]
  try:
    socket.inet_aton(ip_addr_data)
    subprocess.Popen(["iptables", "-I", "1_SSH", "-s", ip_addr_data + "/32", "-p", "tcp", "--dport", "22", "-j", "ACCEPT"])
    BOT.send_message(message.from_user.id, "IP address " + ip_addr_data + " will be added to chain SSH.\n_P.S.: Address will be removed after system reboot._", disable_notification=True, parse_mode="Markdown")
  except socket.error:
    BOT.send_message(message.from_user.id, "Sended message '" + ip_addr_data +"' are not match IP address.")

# Actions with iptables
# 1 step
@BOT.message_handler(commands=['iptables'])
def get_text_messages(message):
  info(":ACCEPT(get ip) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  keyboard = types.InlineKeyboardMarkup(row_width=2)
  iptables_save_button = types.InlineKeyboardButton("SAVE", callback_data="ipt_save_btn")
  iptables_restore_button = types.InlineKeyboardButton("RESTORE", callback_data="ipt_restore_btn")
  keyboard.add(iptables_save_button,iptables_restore_button)
  BOT.send_message(message.from_user.id, "Choose action with iptables:", reply_markup=keyboard)

# 2 step
# SAVE
@BOT.callback_query_handler(lambda query: query.data == "ipt_save_btn")
def callback_ping(call):
  try:
    exists(IPTABLES_FILE)
    shutil.copyfile(IPTABLES_FILE, IPTABLES_FILE + "." + str(round(time.time())) + ".BCK")
    subprocess.Popen(["iptables-save", "-f", IPTABLES_FILE])
    message_text = "Iptables file-conf updated."
  except:
    message_text = "File does not exist. Actions can't be done."
  info(":ACCEPT(iptables save) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  BOT.edit_message_text(message_text, chat_id=call.message.chat.id, message_id=call.message.message_id)

# 3 step
# RESTORE
@BOT.callback_query_handler(lambda query: query.data == "ipt_restore_btn")
def callback_ping(call):
  try:
    exists(IPTABLES_FILE)
    run_commands = []
    run_commands.append(["iptables-restore", IPTABLES_FILE])
# !!!!!!!!!! NEED TO CHANGE THIS because after restore wireguard rules are not applying
#    run_commands.append(["systemctl", "stop", "wg-quick@wg0.service"])
#    run_commands.append(["systemctl", "start", "wg-quick@wg0.service"])
    for command in run_commands:
      subprocess.Popen(command)
    message_text = "Iptables rules restored from file-conf."
  except:
    message_text = "File does not exist. Actions can't be done."
  info(":ACCEPT(iptables restore) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  BOT.edit_message_text(message_text, chat_id=call.message.chat.id, message_id=call.message.message_id)

## Menu for start the work with BOT
@BOT.message_handler(commands=['go'])
def get_text_messages(message):
  info(":ACCEPT(go action) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
#    info(":ACCEPT id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
#    keyboard = types.InlineKeyboardMarkup(row_width=3)
#    ping_button = types.InlineKeyboardButton("PING", callback_data="ping_btn")
#    nslookup_button = types.InlineKeyboardButton("NSLOOKUP", callback_data="nslookup_btn")
#    telnet_button = types.InlineKeyboardButton("TELNET", callback_data="telnet_btn")
#    phone_notify_button = types.InlineKeyboardButton("Вкл./Выкл. SMS оповещение", callback_data="phone_notify_btn")
#    myteam_notify_button = types.InlineKeyboardButton("Вкл./Выкл. MyTeam оповещение", callback_data="myteam_notify_btn")
#    telegram_notify_button = types.InlineKeyboardButton("Вкл./Выкл. Telegram оповещение", callback_data="telegram_notify_btn")
#    keyboard.add(ping_button, nslookup_button ,telnet_button)
#    keyboard.add(phone_notify_button)
#    keyboard.add(myteam_notify_button)
#    keyboard.add(telegram_notify_button)
#    BOT.send_message(message.chat.id, "Выберте действие:", reply_markup=keyboard)
  BOT.send_message(message.from_user.id, "Soon GO menu will be, until...\n\nStart to using - /go\nCall help pages - /help")

@BOT.message_handler(commands=['cancel'])
def get_text_messages(message):
  info(":ACCEPT(cancel action) id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  msg = BOT.send_message(message.from_user.id, "Cancelled.")

# Help message
@BOT.message_handler(content_types=['text'])
def first_menu_step(message):
  print(message)
  info(":UNKNOWN(" + message.text + ") id: " + str(message.chat.id) + ", username: " + str(message.chat.username) + ", name: " + str(message.chat.first_name) + " " + str(message.chat.last_name))
  BOT.send_message(message.from_user.id, "Unknown command.\nPlease use help-pages to get info if you need.\n\nStart to using - /go\nCall help pages - /help")

BOT.polling(none_stop=True, interval=0)

if __name__ == "__main__":
  main()
