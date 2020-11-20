from telegram.ext import Updater, CommandHandler, PollAnswerHandler, MessageHandler, Filters
from telegram import ParseMode
import speech_recognition as sr
from googletrans import Translator
import pandas as pd
import logging
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Set the logging function to print the error message whenever it happens
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

userbase = {}
language_mapping = {"English":"english","Hindi":"hindi","Korean":"korean","Japanese":"japanese","French":"french"}

def encodemessage(message):
  message = message.replace("-","")
  message = message.replace("(","")
  message = message.replace(".","")
  message = message.replace(")","")
  return message


def encode_file():
  subprocess.call(['ffmpeg', '-y', '-i', 'voice.mp3', 'voice.wav'],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)

def get_language_code(uid):
  global userbase
  if userbase[uid]["lastcmd"] == "src":
    return userbase[uid]["dest"]
  return userbase[uid]["src"]

def translate_from_file(update, context,file_path,uid):
  r = sr.Recognizer()
  voice = sr.AudioFile(file_path)
  with voice as source:
    audio = r.record(source)

  text = r.recognize_google(audio)

  translator = Translator()
  translated = translator.translate(text,dest=get_language_code(uid))
  context.bot.send_message(chat_id=update.message.chat_id, text="`{}`".format(translated.text),  parse_mode='MarkdownV2')
  print(translated.text,get_language_code(uid))


def transcribe_from_file(update, context,file_path,uid):
  r = sr.Recognizer()
  voice = sr.AudioFile(file_path)
  with voice as source:
    audio = r.record(source)

  text = r.recognize_google(audio)
  context.bot.send_message(chat_id=update.message.chat_id, text="`{}`".format(text),  parse_mode='MarkdownV2')

def send_word(update, context):
  # Read the dataset and pick a random word
  df = pd.read_csv('dictionary.csv')
  word = df.sample()
  word, korean, pronunciation, meaning = (word.iloc[0]["word"], word.iloc[0]["korean"], word.iloc[0]["pronunciation"], word.iloc[0]["meaning"])
  message = "*" + word.capitalize() + "*" + "\n" + meaning + "\n\n" + "`Korean`\n" + korean + "\nPronunced as _" + pronunciation + "_"
  message = encodemessage(message)
  print("Handled Request with",word)

  # Get the user chat_id for sending back the message
  chat_id = update.message.chat_id
  
  # Send the word and the audio
  context.bot.send_message(chat_id=chat_id, text=message,  parse_mode='MarkdownV2')
  context.bot.send_voice(chat_id=chat_id, voice=open('audio/{}.mp3'.format(korean), 'rb'))


def poll(update, context, question, options):
    """Sends a predefined poll"""
    questions = options
    message = context.bot.send_poll(
        update.effective_chat.id,
        question,
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def receive_poll_answer(update, context):
    """Summarize a users poll vote"""
    global userbase, language_mapping
    answer = update.poll_answer
    userid = answer.user.id
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    lastcmd = userbase[userid]["lastcmd"]


    for question_id in selected_options:
        answer_string += questions[question_id]

    if lastcmd =="setsrc":
      lastcmd = "Source"
      userbase[userid]["src"] = language_mapping[answer_string]
    elif lastcmd == "setdest":
      lastcmd = "Destination"
      userbase[userid]["dest"] = language_mapping[answer_string]
    else:
      lastcmd = "Unknown"

    print(userbase[userid])
    if lastcmd == "Unknown":
      context.bot.send_message("Unknown poll Result Recieved")
    else:
      context.bot.send_message(
          context.bot_data[poll_id]["chat_id"],
          "{} Language has been set to {}!".format(lastcmd,answer_string),
          parse_mode=ParseMode.HTML,
      )


def set_source(update, context):
  global userbase
  userid = update.message.chat.id
  if userid not in userbase:
    userbase[userid] = {}
  userbase[userid]["lastcmd"] = "setsrc"
  poll(update,context,"Please Select the source language",["English","Hindi","Korean","Japanese","French"])


def set_dest(update, context):
  global userbase
  userid = update.message.chat.id
  if userid not in userbase:
    userbase[userid] = {}
  userbase[userid]["lastcmd"] = "setdest"
  poll(update,context,"Please Select the destination language",["English","Hindi","Korean","Japanese","French"])


def source(update, context):
  global userbase
  userid = update.message.chat.id
  if userid not in userbase:
    userbase[userid] = {}
  userbase[userid]["lastcmd"] = "src"
  context.bot.send_message(chat_id=update.message.chat_id, text="You can now send audio in `{}`".format(userbase[userid]["src"]),  parse_mode='MarkdownV2')

def transcribe(update, context):
  global userbase
  userid = update.message.chat.id
  if userid not in userbase:
    userbase[userid] = {}
  userbase[userid]["lastcmd"] = "transcribe"
  context.bot.send_message(chat_id=update.message.chat_id, text="You can now send audio for transcribing".format(userbase[userid]["src"]),  parse_mode='MarkdownV2')

def dest(update, context):
  global userbase
  userid = update.message.chat.id
  if userid not in userbase:
    userbase[userid] = {}
  userbase[userid]["lastcmd"] = "dest"
  context.bot.send_message(chat_id=update.message.chat_id, text="You can now send audio in `{}`".format(userbase[userid]["dest"]),  parse_mode='MarkdownV2')


def voice_handler(update, context):
    global userbase
    bot = context.bot
    id = update.message.chat.id
    file = bot.getFile(update.message.voice.file_id)
    file.download('voice.mp3')
    print("Handling")
    encode_file()
    if userbase[id]["lastcmd"] == "transcribe":
      transcribe_from_file(update, context,"voice.wav",id)
    else:
      translate_from_file(update, context,"voice.wav",id)



def main():
  
  # Initiate the bot and add command handler  
  updater = Updater('1372620314:AAHxc2wdMdjn-5I8QAaKgQ_qyZc36j6mvcQ', use_context=True)
  updater.dispatcher.add_handler(CommandHandler('newword', send_word))

  updater.dispatcher.add_handler(CommandHandler('setsource', set_source))
  updater.dispatcher.add_handler(CommandHandler('setdestination', set_dest))

  updater.dispatcher.add_handler(CommandHandler('source', source))
  updater.dispatcher.add_handler(CommandHandler('dest', dest))
  updater.dispatcher.add_handler(CommandHandler('transcribe', transcribe))

  updater.dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
  updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))

  # Run the bot
  updater.start_polling()
  updater.idle()
  
if __name__ == '__main__':
  main()