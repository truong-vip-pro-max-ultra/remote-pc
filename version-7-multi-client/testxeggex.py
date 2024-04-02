import requests
import time
import pytz
from datetime import datetime
import streamlit as st
import threading

def get_time_now():
  tz_Vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
  now_Vietnam = datetime.now(tz_Vietnam)
  return now_Vietnam.strftime('%d-%m-%Y %H:%M:%S')


def cut_string(string, start, end):
  try:
    return string.split(start)[1].split(end)[0]
  except:
    return ''


def send_message(message):
  TOKEN = "6540669594:AAECx9DSh1apAXYz7KudYIoygEvzwm-Gapo"
  ID = "-4123868070"
  url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage?chat_id=" + ID + "&text=" + "<code>" + message + "</code>" + "&parse_mode=HTML"
  p = requests.post(url)


def get_price():
  price_save = 0
  while True:
    session = requests.session()
    url = 'https://xeggex.com/market/ZEPH_USDT'
    headers = {
        'user-agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
    }
    p = session.get(url)
    price = cut_string(p.text, 'class="marketlastprice">', '<')
    try:
      float(price)
      price_usdt = float(price)
      if price_save != price_usdt:
        # print(price)
        if price_save < price_usdt:
          notify = 'Tăng'
        else:
          notify = 'Giảm'
        price_save = price_usdt
        message = notify + ' | ' + str(price_usdt) + ' | ' + get_time_now()
        send_message(message)
    except Exception as e:
      print(e)
    time.sleep(5)

t1 = threading.Thread(target=get_price)
t1.start()
st.set_page_config(
             page_title="Spam Số Điện Thoại By Thầy Trường",
             page_icon=":shark:"
        )
st.title("Spam Số Điện Thoại By Thầy Trường")