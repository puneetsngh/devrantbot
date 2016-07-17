# -*- coding: utf-8 -*-

import sys
import cgi
from datetime import datetime, timedelta
from datetime import *
from time import *
import time
import os
import telebot # use pip install pyTelegramBotAPI to install telebot
from telebot import types
import re
import json
import requests
import string
from uuid import uuid4
import unittest 
import traceback
import pretty

reload(sys)
sys.setdefaultencoding('utf8')



API_TOKEN = 'TYPE YOUR TELEGRAM BOT TOKEN' # telegram bot token you got from @botfather
bot = telebot.TeleBot(API_TOKEN)
print bot		
		
profile_regex = r'\/[a-zA-Z0-9\S]+'
		
		
# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):

    bot.send_message(message.chat.id,"""Hi, I am the devRant bot. One of the ranters among you created me.

I work inline. Just see some examples /learn to get an idea about me.

<b>Bot from</b> @techworxs
<b>Credits for api access</b> devRant creators @dfoxinator and @tim_rogus
""",parse_mode="HTML") 
    bot.send_document(message.chat.id,open('media/devrant.mp4','r'))
    user_joined(message)

def user_joined(message):
    try:
        in_file = open('devrantuserlist.json','r')
        new_dict = json.load(in_file)
        text = new_dict
        flag=1
        for user in new_dict:
            print user['id']
            if str(message.from_user.id) in user['id']:
                flag = 0
                break
        if flag==1:
            print "I am here"
            my_dict={'id':str(message.from_user.id), 'Name':str(message.from_user.first_name)+' '+str(message.from_user.last_name),'username':str(message.from_user.username)}
            new_dict.append(my_dict)
            out_file = open('devrantuserlist.json','w')
            json.dump(new_dict,out_file,indent=4)
            out_file.close()
            print "Nope you are already there"
            in_file.close()

    except Exception:
        pass

        
        
@bot.chosen_inline_handler(func=lambda m: True)
def inline_chosen(m):
    print m.query
    try:
        in_file = open('devrantinlineuserlist.json','r')
        new_dict = json.load(in_file)
        text = new_dict
        flag=1
        for user in new_dict:
            print user['id']
            if str(m.from_user.id) in user['id']:
                flag = 0
                break
        if flag==1:
            my_dict={'id':str(m.from_user.id), 'Name':str(m.from_user.first_name)+' '+str(m.from_user.last_name),'username':str(m.from_user.username)}
            new_dict.append(my_dict)
            out_file = open('devrantinlineuserlist.json','w')
            json.dump(new_dict,out_file,indent=4)
            out_file.close()
            in_file.close()   

    except:
        pass        

@bot.message_handler(commands=['extras'])
def send_extras(message):
    bot.send_message(message.chat.id,"""
Hi, I have more bots created for daily use.

1. @smswaybot - *Sends free sms anywhere in India.*

2. @siftbot - *Search web, news, pics, youtube, gifs, wiki, weather, restaurants, live cricket scores, urban dictionary.*

3. @emojirobot - *It can transform your text into emoji. Use it inline.*

4. @watchcomicbot - *You can watch more than 4000 cartoons,animated movies, english dubbed anime.*
""",parse_mode='Markdown')        


# to learn bot commands  
@bot.message_handler(commands=['learn'])
def send_welcome(message):
    bot.send_message(message.chat.id,"""
*devRant bot inline commands* :-

*1. Rants* : @devrantbot

*2. Top Rants* : @devrantbot top

*3. Recent Rants* : @devrantbot recent

*4. Search Rants* : @devrantbot search <term>

*5. Surprise Rants* : @devrantbot surprise

*6. Ranter's Profile* : @devrantbot /<username>
""",parse_mode="Markdown")



@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,"""
    You can contact the creator of the bot @puneetsingh.
    
For queries about bot hosting you can contact @bothostingbot""")



@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(message.chat.id,"""
Hi, I can search for rants from devRant.io.

If you are also a devRant app user, you can use me or if not then and if not then look what developers do other than work.

You can also join out @devrant community on telegram.

We created this bot because we love devRant and want to grow devRant ecosystem. 🙂""")



@bot.message_handler(func=lambda message:True)
def process_message(message):
    try:
        text = message.text
        msg = "You should use me inline. Just see my inline commands /learn"
        bot.send_message(message.chat.id,msg)
    except Exception:
        pass



@bot.inline_handler(func=lambda m:True)
def query_text(m):
    print m
    text = str(m.query)
    try:    
        if text[:6]=='search':

            offset = int(m.offset or 0)
            limit = offset + 5
            search_feeds,search_offset = search(text[7:],limit,offset)
            
            isearch_list = []
            for results in range(len(search_feeds)):
                inline_search_markup = types.InlineKeyboardMarkup()
                search_comments = types.InlineKeyboardButton('comments',url='https://www.devrant.io/rants/'+str(search_feeds[results]['id']))
                inline_search_markup.row(search_comments)	
            
                tags = str('#'+',\t#'.join(search_feeds[results]['tags'])).replace(" ","")

                search_inline =types.InlineQueryResultArticle(str(uuid4()),"@"+str(search_feeds[results]['name'])+' ['+str(search_feeds[results]['user_score'])+']',types.InputTextMessageContent('@<b>'+str(cgi.escape(search_feeds[results]['name']))+' [+'+str(search_feeds[results]['user_score'])+']</b>\n<code>'+str(search_feeds[results]['time'])+'</code>\n\n'+str(cgi.escape(search_feeds[results]['text']))+'\n\n<code>score :'+str(search_feeds[results]['score'])+'\ncomments :'+str(search_feeds[results]['comments'])+'</code>''\n\n'+tags+' <a href="'+str(search_feeds[results]['image'])+'">.</a>',parse_mode="HTML"),url='https://www.devrant.io/rants/'+str(search_feeds[results]['id']),hide_url=True,description=str(cgi.escape(search_feeds[results]['text'])),reply_markup=inline_search_markup,thumb_url='http://getdummyimage.com/image?width=128&height=128&bgcolor=%2354556e&color=%23ffffff&text=%2B%2B%0A'+str(search_feeds[results]['score'])+'%0A--&bordercolor=')
                isearch_list.append(search_inline)
            bot.answer_inline_query(m.id,isearch_list,cache_time=1,next_offset=search_offset)
            
        elif text[:8]=='surprise':
            surprise_feeds= surprise()
            surprise_list = []
            inline_surprise_markup = types.InlineKeyboardMarkup()
            surprise_comments = types.InlineKeyboardButton('comments',url='https://www.devrant.io/rants/'+str(surprise_feeds['id']))
            inline_surprise_markup.row(surprise_comments)	
            
            tags = str('#'+',\t#'.join(surprise_feeds['tags'])).replace(" ","")

            surprise_inline =types.InlineQueryResultArticle(str(uuid4()),"@"+str(surprise_feeds['name'])+' ['+str(surprise_feeds['user_score'])+']',types.InputTextMessageContent('@<b>'+str(cgi.escape(surprise_feeds['name']))+' [+'+str(surprise_feeds['user_score'])+']</b>\n<code>'+str(surprise_feeds['time'])+'</code>\n\n'+str(cgi.escape(surprise_feeds['text']))+'\n\n<code>score :'+str(surprise_feeds['score'])+'\ncomments :'+str(surprise_feeds['comments'])+'</code>''\n\n'+tags+' <a href="'+str(surprise_feeds['image'])+'">.</a>',parse_mode="HTML"),url='https://www.devrant.io/rants/'+str(surprise_feeds['id']),hide_url=True,description=str(cgi.escape(surprise_feeds['text'])),reply_markup=inline_surprise_markup,thumb_url='http://getdummyimage.com/image?width=128&height=128&bgcolor=%2354556e&color=%23ffffff&text=%2B%2B%0A'+str(surprise_feeds['score'])+'%0A--&bordercolor=')
            surprise_list.append(surprise_inline)
            bot.answer_inline_query(m.id,surprise_list,cache_time=1)  
            
        elif re.match(profile_regex,text):

            profile_info = profile(text[1:])
            profile_list = []
            inline_profile_markup = types.InlineKeyboardMarkup()
            profile_page = types.InlineKeyboardButton('see my profile',url='https://www.devrant.io/users/'+str(profile_info['name']))
            inline_profile_markup.row(profile_page)	
            
            profile_inline =types.InlineQueryResultArticle(str(uuid4()),"@"+str(profile_info['name'])+' ['+str(profile_info['score'])+']',types.InputTextMessageContent('@*'+str(cgi.escape(profile_info['name']))+' [+'+str(profile_info['score'])+']*\n\n👤 '+str(cgi.escape(profile_info['about']))+'\n*</>* '+str(cgi.escape(profile_info['skill']))+'\n📫 '+str(profile_info['location'])+'\nJoined devRant on '+str(cgi.escape(profile_info['time']))+'\n\nRants : '+str(profile_info['rants'])+"\n+1's : "+str(profile_info['upvotes'])+'\nComments : '+str(profile_info['comments'])+'\nFavorites : '+str(profile_info['favorites']),parse_mode="Markdown"),description='Joined devRant on '+str(cgi.escape(profile_info['time'])),thumb_url='http://simpleicon.com/wp-content/uploads/user-5.png')
            profile_list.append(profile_inline)
            bot.answer_inline_query(m.id,profile_list,cache_time=1)  
            
        else:
            offset = int(m.offset or 0)
            limit = 5
            skip = offset
            rants_feeds,rantoffset = rants(text,limit,skip)
            rantoffset = rantoffset+5
            feed_list = []
            for results in range(len(rants_feeds)):
                inline_rant_markup = types.InlineKeyboardMarkup()
                rant_comments = types.InlineKeyboardButton('comments',url='https://www.devrant.io/rants/'+str(rants_feeds[results]['id']))
                inline_rant_markup.row(rant_comments)	
                
                tags = str('#'+',\t#'.join(rants_feeds[results]['tags'])).replace(" ","")

                rants_inline =types.InlineQueryResultArticle(str(uuid4()),"@"+str(rants_feeds[results]['name'])+' ['+str(rants_feeds[results]['user_score'])+']',types.InputTextMessageContent('@<b>'+str(cgi.escape(rants_feeds[results]['name']))+' [+'+str(rants_feeds[results]['user_score'])+']</b>\n<code>'+str(rants_feeds[results]['time'])+'</code>\n\n'+str(cgi.escape(rants_feeds[results]['text']))+'\n\n<code>score :'+str(rants_feeds[results]['score'])+'\ncomments :'+str(rants_feeds[results]['comments'])+'</code>''\n\n'+tags+' <a href="'+str(rants_feeds[results]['image'])+'">.</a>',parse_mode="HTML"),url='https://www.devrant.io/rants/'+str(rants_feeds[results]['id']),hide_url=True,description=str(cgi.escape(rants_feeds[results]['text'])),reply_markup=inline_rant_markup,thumb_url='http://getdummyimage.com/image?width=128&height=128&bgcolor=%2354556e&color=%23ffffff&text=%2B%2B%0A'+str(rants_feeds[results]['score'])+'%0A--&bordercolor=')
                feed_list.append(rants_inline)
            bot.answer_inline_query(m.id,feed_list,cache_time=1,next_offset=rantoffset,switch_pm_text="see more commands",switch_pm_parameter='learn')
            
    except Exception as e: 
        print "Exception"+str(e)
        print traceback.print_exc()
        pass
    
    
def rants(text,limit,skip):
    #'weekly':
    #    url = 'https://www.devrant.io/api/devrant/weekly-rants?app=3'

    url='https://www.devrant.io/api/devrant/rants?app=3&limit='+str(limit)+'&skip='+str(skip)+'&sort='+text
    response = requests.get(url)
    print response
    tags = []
    rant_list = []
    data = response.json()

    for rant in range(len(data['rants'])):
        rant_dic = {}
        rant_dic['name'] = data['rants'][rant]['user_username']
        rant_dic['img'] = data['rants'][rant]['attached_image'] or {"url":"#"}
        rant_dic['image'] = str(rant_dic['img']['url'] or '#')
        tags = data['rants'][rant]['tags']
        rant_dic['tags'] = tags
        rant_dic['comments'] = str(data['rants'][rant]['num_comments'] or 0)
        rant_dic['text'] = str(data['rants'][rant]['text'] or None)
        rant_dic['score'] = data['rants'][rant]['score']   
        rant_dic['time'] = pretty.date(data['rants'][rant]['created_time'])
        rant_dic['id'] = data['rants'][rant]['id']        
        rant_dic['user_id'] = data['rants'][rant]['user_id']
        rant_dic['user_score'] = data['rants'][rant]['user_score']
        rant_list.insert(rant,rant_dic)  
    return rant_list,skip

def search(text,limit,off):
    url='https://www.devrant.io/api/devrant/search?app=3&term='+str(text)+'&limit'+str(limit)
    response = requests.get(url)
    print response
    tags = []
    data = response.json()
    search_dic = {}
    search_list = []
    for rant in range(len(data['results']))[off:limit]:
        search_dic = {}
        search_dic['name'] = data['results'][rant]['user_username']
        search_dic['img'] = data['results'][rant]['attached_image'] or {"url":"#"}

        search_dic['image'] = str(search_dic['img']['url'] or '#')
        tags = data['results'][rant]['tags']
        search_dic['tags'] = tags
        search_dic['comments'] = str(data['results'][rant]['num_comments'] or 0)
        search_dic['text'] = str(data['results'][rant]['text'] or None)
        search_dic['score'] = data['results'][rant]['score']   
        search_dic['time'] = pretty.date(data['results'][rant]['created_time'])
        search_dic['id'] = data['results'][rant]['id']        
        search_dic['user_id'] = data['results'][rant]['user_id']
        search_dic['user_score'] = data['results'][rant]['user_score']
        search_list.insert(rant,search_dic)

    return search_list,limit

def surprise():  
    url='https://www.devrant.io/api/devrant/rants/surprise?app=3'
    response = requests.get(url)
    print response
    tags = []
    data = response.json()
    surprise_dic = {}
    surprise_dic['name'] = data['rant']['user_username']
    surprise_dic['img'] = data['rant']['attached_image'] or {"url":"#"}
    surprise_dic['image'] = str(surprise_dic['img']['url'] or '#')
    tags = data['rant']['tags']
    surprise_dic['tags'] = tags
    surprise_dic['comments'] = str(data['rant']['num_comments'] or 0)
    surprise_dic['text'] = str(data['rant']['text'] or None)
    surprise_dic['score'] = data['rant']['score']   
    surprise_dic['time'] = pretty.date(data['rant']['created_time'])
    surprise_dic['id'] = data['rant']['id']        
    surprise_dic['user_id'] = data['rant']['user_id']
    surprise_dic['user_score'] = data['rant']['user_score']
    return surprise_dic
  
def profile(text):
    url1 = 'https://www.devrant.io/api/get-user-id?username='+text+'&app=3'
    response1 = requests.get(url1)
    print response1
    data1 = response1.json()
    url2 = 'https://www.devrant.io/api/users/'+str(data1['user_id'])+'?app=3'
    response2 = requests.get(url2)
    print response2
    data = response2.json()
    profile_dic = {}
    profile_dic['name'] = data['profile']['username']
    profile_dic['score'] = data['profile']['score'] 
    profile_dic['about'] = data['profile']['about'] 
    profile_dic['location'] = data['profile']['location'] 
    create_time = time.localtime(int(data['profile']['created_time']))
    profile_dic['time'] = time.strftime("%d/%m/%Y", create_time)
    profile_dic['github'] = data['profile']['github'] 
    profile_dic['skill'] = data['profile']['skills'] 
    profile_dic['rants'] = data['profile']['content']['counts']['rants']  
    profile_dic['comments'] = data['profile']['content']['counts']['comments']  
    profile_dic['upvotes'] = data['profile']['content']['counts']['upvoted']  
    profile_dic['favorites'] = data['profile']['content']['counts']['favorites']     

    return profile_dic


###############################
#                             #               
#     Bot Polling Starts      #
#                             #
###############################


my_id = '10000100' #use your telegram id to get messages whenever exception occur
  
try:
    bot.polling(none_stop=True) 
except Exception as e:
    print "Exception Occur : "+str(e)+"\n"+str(traceback.print_exc())
    bot.send_message(my_id,'Exception Occur : '+str(e))
    pass
