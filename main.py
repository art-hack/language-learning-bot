from telegram.ext import Updater, CommandHandler
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()

# Set the logging function to print the error message whenever it happens
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def send_word(update, context):
  
  # Read the dataset and pick a random word
  df = pd.read_csv('dictionary.csv')
  word = df.sample()
  word, korean, pronunciation, meaning = (word.iloc[0]["word"], word.iloc[0]["korean"], word.iloc[0]["pronunciation"], word.iloc[0]["meaning"])
  message = "*" + word.capitalize() + "*" + "\n" + meaning + "\n\n" + "`Korean`\n" + korean + "\nPronunced as _" + pronunciation + "_"
  message = message.replace("-","")
  message = message.replace("(","")
  message = message.replace(".","")
  message = message.replace(")","")
  print("Handled Request with",word)

  # Get the user chat_id for sending back the message
  chat_id = update.message.chat_id
  
  # Send the word and the audio
  context.bot.send_message(chat_id=chat_id, text=message,  parse_mode='MarkdownV2')
  context.bot.send_voice(chat_id=chat_id, voice=open('audio/{}.mp3'.format(korean), 'rb'))
  
def main():
  
  # Initiate the bot and add command handler  
  updater = Updater('1372620314:AAHxc2wdMdjn-5I8QAaKgQ_qyZc36j6mvcQ', use_context=True)
  updater.dispatcher.add_handler(CommandHandler('newword', send_word))
  
  # Run the bot
  updater.start_polling()
  updater.idle()
  
if __name__ == '__main__':
  main()