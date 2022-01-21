from transitions.extensions import GraphMachine

#from asyncio.windows_events import NULL
import os
import sys
from itertools import count
from transitions.extensions import GraphMachine
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotApi, WebhookParser
import datetime
from dateutil import rrule
import schedule
import time
from apscheduler.schedulers.background import BlockingScheduler,BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import requests
from bs4 import BeautifulSoup
from random import randrange

from utils import send_showAll, send_text_message,send_showAll,job_that_executes_once
user_id = "U227736503c290a9f5fbe50b3423d5df2"
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

expireyear = []
expiremonth = []
expireday = []
oneday = []
null=["NULL"]
class TocMachine(GraphMachine):
    
    date = []
    foodtype = []
    num = []
    count = 0
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
    def my_job():
        line_bot_api = LineBotApi(channel_access_token)
        line_bot_api.push_message(user_id, TextSendMessage(text=TocMachine.foodtype[count]+'到期了！'))
        print('到期了')
        
    #輸入食材流程
    def is_going_to_enterFood(self, event):
        text = event.message.text
        return text.lower() == "開始記錄"

    def is_going_to_enterDate(self, event):
        text = event.message.text
        return True
    
    def is_going_to_enternum(self, event):
        text = event.message.text
        return True

    def is_going_to_comfirm(self, event):
        text = event.message.text
        return True

    #other
    def is_going_to_showAll(self, event):
        text = event.message.text
        return text.lower() == "查看冰箱"
    #推薦食譜
    def is_going_to_recommand(self, event):
        text = event.message.text
        return text.lower() == "推薦食譜"
 
    #輸入食材流程
    def on_enter_enterFood(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入菜名我們將會儲存至資料庫")
        
    
    #輸入日期
    def on_enter_enterDate(self, event):
        print("I'm entering state1")
        TocMachine.foodtype.append(event.message.text)
        reply_token = event.reply_token
        send_text_message(reply_token, "已收到菜名，請輸入保存期限，屆時會提醒你 "+TocMachine.foodtype[TocMachine.count])

    #輸入數量
    def on_enter_enternum(self, event):
        print("I'm entering state1")
        TocMachine.date.append(event.message.text)
        reply_token = event.reply_token
        send_text_message(reply_token, "已收到菜名，請輸入數量，屆時會提醒你 "+TocMachine.foodtype[TocMachine.count])
        
    
    #確認
    def on_enter_comfirm(self, event):
        print("I'm entering state1")
        TocMachine.num.append(int(event.message.text))
        #expire = event.message.text
        length = len(TocMachine.date)
        expire = TocMachine.date[length - 1]
        
         
        expireyear.append(expire.split()[0])
        expiremonth.append(expire.split()[1])
        expireday.append(expire.split()[2])
        today = datetime.date.today() 
        print(expire.split()[0])
        print(expire.split()[1])
        print(expire.split()[2])
        reply_token = event.reply_token
        #oneday.append(datetime.date(int(expire.split()[0]),int(expire.split()[1]),int(expire.split()[2])))
         
        #days = rrule.rrule(rrule.DAILY, dtstart=today, until=oneday).count()
        #schedule.every(days).day.at("8:30").do(job_that_executes_once("你的"+TocMachine.foodtype[TocMachine.count])+"已到期")
        send_text_message(reply_token, "已收到日期，跟你確認一下機制:\n"+TocMachine.foodtype[TocMachine.count]+"\n"+TocMachine.date[TocMachine.count] + "\n" + str(TocMachine.num[TocMachine.count]))
        scheduler = BackgroundScheduler()
        intervalTrigger=DateTrigger(run_date=expire.split()[0]+'-'+expire.split()[1]+'-'+expire.split()[2]+ 'T08:00:00+08:00')
        scheduler.add_job(TocMachine.my_job, intervalTrigger, id='my_job_id'+str(TocMachine.count))
        scheduler.start()
        
        
        TocMachine.count+=1
        self.go_back()
     


  
    def on_enter_showAll(self, event):
        print("I'm entering state2")
        
        reply_token = event.reply_token
        text = "目前冰箱已有食材：\n"
        for i in range (0,TocMachine.count):
            if TocMachine.foodtype[i]!=null[0]:
                text = text + TocMachine.foodtype[i]+"\t"+TocMachine.date[i]+"\t" + "數量："+str(TocMachine.num[i]) + "\n"
        send_showAll(reply_token,text)
        self.go_back()

    def on_exit_showAll(self):
        print("Leaving state2")
#推薦食譜
    def on_enter_recommand(self, event):
        print("I'm entering state2")
       
        reply_token = event.reply_token
        
        if TocMachine.count >1:
            cnt = TocMachine.count-1
            key=TocMachine.foodtype[randrange(cnt)]
            key2=TocMachine.foodtype[randrange(cnt)]
            while( key=="NULL"):
                key = TocMachine.foodtype[randrange(cnt)]

            while( key2=="NULL"):
                key2 = TocMachine.foodtype[randrange(cnt)]

            r = requests.get('https://www.google.com/search?q='+key+'%20'+key2+'%20食譜')
            soup = BeautifulSoup(r.text, 'lxml')
            a_tag = soup.select_one('div.kCrYT a')
            href = a_tag['href']
            googleUrl = 'https://www.google.com'
            text = googleUrl + href
        else:
            text = "食材不足無法推薦食譜，至少要兩樣以上喔！"
        send_text_message(reply_token,text)
         
        self.go_back()

    def on_exit_recommand(self):
        print("Leaving state2")

    # delete
    def is_going_to＿deletedfood(self, event):
        text = event.message.text
        return text.lower() == "刪除食材"

    def on_enter_deletedfood(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入要刪除的菜名及數量")

    def is_going_to＿delete(self, event):
        text = event.message.text
        return True

    def on_enter_delete(self, event):
        print("I'm entering state1")
        #TocMachine.foodtype.append(event.message.text)
        foodtype = event.message.text.split()[0] 
        foodsnum = event.message.text.split()[1]
        length = len(TocMachine.foodtype)
        flag = 0
        for i in range(0,length):
            if foodtype == TocMachine.foodtype[i] and int(foodsnum) == TocMachine.num[i]:
                TocMachine.foodtype.pop(i)
                TocMachine.date.pop(i)
                TocMachine.num.pop(i)
                TocMachine.count = TocMachine.count-1
                flag = 1
                #TocMachine.foodtype[i] = "NULL"
                #TocMachine.date[i] = "NULL" 
                #TocMachine.num[i] = ""
                break
            elif foodtype == TocMachine.foodtype[i] and int(foodsnum) < TocMachine.num[i]:
                TocMachine.num[i] = TocMachine.num[i] - int(foodsnum)
                flag = 1
            else:
                flag = 0
        
        if flag == 0:
            text = "刪除失敗，冰箱沒有欲刪除的食材"
        else:
            text = "刪除成功！"
        reply_token = event.reply_token 
        send_text_message(reply_token, text)
        self.go_back()

    def on_exit_delete(self): 
        print("Leaving state2")


