# from config import tokenAPI
import time
import telegram
from ..utils.parseJSON import readJson

tokenAPI = readJson('crypt.json')
bot = telegram.Bot(token=tokenAPI['tokenAPI'])

def publish(response):
	print('Sending {}'.format(response))
	# pass
	time.sleep(5)
	bot.send_message(chat_id="-1001353473714", text=response)
	print("Signal successfully sent !!")
	# print(status)