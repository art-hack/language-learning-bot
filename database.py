from google.cloud import texttospeech
from bs4 import BeautifulSoup

import pandas as pd
from dotenv import load_dotenv
from googletrans import Translator
from PyDictionary import PyDictionary

dictionary=PyDictionary()
translator = Translator()
load_dotenv()

def get_hangeul():
  words = ["angle", "ant", "apple", "arch", "arm", "army", "baby", "bag", "ball", "band", "basin", "basket", "bath", "bed", "bee", "bell", "berry", "bird", "blade", "board", "boat", "bone", "book", "boot", "bottle", "box", "boy", "brain", "brake", "branch", "brick", "bridge", "brush", "bucket", "bulb", "button", "cake", "camera", "card", "cart", "carriage", "cat", "chain", "cheese", "chest", "chin", "church", "circle", "clock", "cloud", "coat", "collar", "comb", "cord", "cow", "cup", "curtain", "cushion", "dog", "door", "drain", "drawer", "dress", "drop", "ear", "egg", "engine", "eye", "face", "farm", "feather", "finger", "fish", "flag", "floor", "fly", "foot", "fork", "fowl", "frame", "garden", "girl", "glove", "goat", "gun", "hair", "hammer", "hand", "hat", "head", "heart", "hook", "horn", "horse", "hospital", "house", "island", "jewel", "kettle", "key", "knee", "knife", "knot", "leaf", "leg", "library", "line", "lip", "lock", "map", "match", "monkey", "moon", "mouth", "muscle", "nail", "neck", "needle", "nerve", "net", "nose", "nut", "office", "orange", "oven", "parcel", "pen", "pencil", "picture", "pig", "pin", "pipe", "plane", "plate", "plow", "pocket", "pot", "potato", "prison", "pump", "rail", "rat", "receipt", "ring", "rod", "roof", "root", "sail", "school", "scissors", "screw", "seed", "sheep", "shelf", "ship", "shirt", "shoe", "skin", "skirt", "snake", "sock", "spade", "sponge", "spoon", "spring", "square", "stamp", "star", "station", "stem", "stick", "stocking", "stomach", "store", "street", "sun", "table", "tail", "thread", "throat", "thumb", "ticket", "toe", "tongue", "tooth", "town", "train", "tray", "tree", "trousers", "umbrella", "wall", "watch", "wheel", "whip", "whistle", "window", "wing", "wire", "worm"]

  result = []
  i = 1
  for word in words:
    x = translator.translate(word, dest='ko')
    result.append((word, x.text,x.pronunciation,dictionary.meaning(word)["Noun"][0]))
    create_audio(x.text)
    print("Completed:",i,"/",len(words),end='\r')
    i+=1

  return result

def create_audio(text, language='ko-KR'):

  # Instantiates a client
  client = texttospeech.TextToSpeechClient()

  # Set the text input to be synthesized
  synthesis_input = texttospeech.SynthesisInput(text=text)

  # Build the voice request, select the language code ("ko-KR") and the ssml
  # voice gender ("neutral")
  voice = texttospeech.VoiceSelectionParams(
    language_code=language,
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

  # Select the type of audio file you want returned
  audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3)

  # Perform the text-to-speech request on the text input with the selected
  # voice parameters and audio file type
  response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

  # The response's audio_content is binary.
  with open('audio/{}.mp3'.format(text), 'wb') as out:
    # Write the response to the output file.
    out.write(response.audio_content)

if __name__ == "__main__":

  # Get list of korean words and get the audio for each word
  words = get_hangeul()

  # Create the dataframe of words and save it as .csv file
  dictionary = pd.DataFrame(words, columns=['word','korean','pronunciation','meaning'])
  dictionary.to_csv('dictionary.csv', index=False)
