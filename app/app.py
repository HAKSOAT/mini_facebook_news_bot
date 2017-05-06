#!/usr/bin/python

import requests
import random
from flask import Flask, request
from datetime import datetime
from bs4 import BeautifulSoup
pageAccessToken = "GET A PAGE TOKEN FROM FACEBOOK AND SAVE AS A STRING"
fb_token = "CREATE A FACEBOOK PAGE AND GENERATE A TOKEN"
app = Flask(__name__)

@app.route("/", methods = ["GET"])
def handle_verification():
    print "Handling Verification"
    if request.args.get("hub.verify_token", "") == fb_token:
        print "Verification Successful"
        return request.args.get("hub.challenge", "")
    else:
        print "Verification Failed"
        return "Error, wrong validation token"

@app.route('/', methods = ['POST'])
def handle_messages():
    global sender
    data = request.json
    print data
    try:
        sender = data["entry"][0]["messaging"][0]["sender"]["id"]
        message = data["entry"][0]["messaging"][0]["message"]["text"].lower()
        reply_messages(sender, reply_text(message))
    except KeyError:
        print "Not text sent"

    return "ok"

class NewsClass():
    def create_soccer(self):#Foreign football news
        global SoccerTable
        SoccerTable = {}
        webObject = requests.get("http://www.dailymail.co.uk/sport/football/index.html")
        webContent = webObject.content
        htmlContent = BeautifulSoup(webContent, "html.parser")
        excerpts = htmlContent.find_all("div", {"class":["articletext","articletext-holder"]})
        links = htmlContent.find_all("a", {"itemprop" : "url"})
        User_id = 1
        for each, stitch in zip(links, excerpts):
            title = each.text.replace("'","")
            link = "http://www.dailymail.co.uk" + each["href"].replace("'","")          
            excerpt = stitch.find("p").text.replace("'","")
            User_id += 1  
            #print title           
            SoccerTable.update({User_id:[User_id,title,link,excerpt]})
            if User_id == 21:
                break
        SoccerTable = SoccerTable.values()

    def create_npoli(self):#Nigerian politics news
            global PoliticsTable
            PoliticsTable = {}
            webObject = requests.get("http://www.vanguardngr.com/category/politics/")
            webContent = webObject.content
            htmlContent = BeautifulSoup(webContent, "html.parser")
            all_content = htmlContent.find_all("article", id = True)
            User_id = 1
            for each in all_content:
                title = each.find("h2", {"class":"entry-title"}).find("a", href = True).text
                link = (each.find("h2", {"class":"entry-title"}).find("a", href = True))["href"]         
                excerpt = each.find("p").text
                User_id += 1  
                #print title           
                PoliticsTable.update({User_id:[User_id,title,link,excerpt]})
                if User_id == 22:
                    break
            PoliticsTable = PoliticsTable.values()

    def truncate(self, tableType):
        del tableType

def reply_messages(user_id, message):
    data = {
        "recipient":{"id": user_id},
        "message":{"text": message}
    }
    response = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + pageAccessToken, json=data)
    print response.content



def reply_text(message):
    if message == "menu":
        reply = "Here are my news keyword:\nType FFOOT for foreign football news.\nNPOLI for Nigerian political news"
        return reply
    elif message == "ffoot":
        num = 0
        send = ""
        for each in SoccerTable:
            send += str(each[0]) + ">>>" + each[1] + "\n\n"
            num += 1
            if num % 3 == 0:
                reply_messages(sender, send) 
                send = ""

    
        return "\n\nTo get more from the list, type FFOOT.number; e.g FFOOT.1 to get first news on list"
    elif "ffoot" in message:
        try:
            number = int(message[6:])
            latest = SoccerTable[number - 2][3] + "....Full details here ....\n" + SoccerTable[number - 2][2]
            reply_messages(sender, latest)
        except:
            return "Keyword doesn't exist. To get more from the list type FFOOT.number, e.g FFOOT.1 to get first news on list"
    elif message == "npoli":
        num = 0
        send = ""
        for each in PoliticsTable:
            send += str(each[0]) + ">>>" + each[1] + "\n\n"
            num += 1
            if num % 3 == 0:
                reply_messages(sender, send) 
                send = ""

        return "\n\nTo get more from the list, type NPOLI.number; e.g NPOLI.1 to get first news on list"
    elif "npoli" in message:        
        try:
            number = int(message[6:])
            latest = PoliticsTable[number - 2][3] + "....Full details here ....\n" + PoliticsTable[number - 2][2]
            reply_messages(sender, latest)
        except:
            return "Keyword doesn't exist. To get more from the list type FFOOT.number, e.g FFOOT.1 to get first news on list"
    elif message in greetIn:
        return random.choice(greetOut)
    else:
        return "Wrong Keyword, type MENU for my menu."

greetIn = ["hi","hello","hey","how far?","good day","hey there","newsify","hey there","how are you?","how are you","What's up","Wats up",
            "Whats up?","good morning","good afternoon","good evening"]
greetOut = ["Hi. I am a Newsify bot.\nType MENU to know more.","Hey there, I'm Newsify.\nType MENU to know more.",
            "You are welcome to Newsify.\nType MENU to know more.", "Hi there, Newsify brings foreign football and Nigerian political headlines for now.\nType MENU to know more.",
            "Hello, the Newsify bot welcomes you.\nType MENU to know more.","I welcome you to the Newsify bot page.\nType MENU to know more.",
            "Newsify at your service!\nType MENU to know more."]

tables = NewsClass()
tables.create_soccer()
tables.create_npoli()


if str(datetime.now().hour) + str(datetime.now().minute) == 0001:
    tables.truncate(SoccerTable)
    tables.create_soccer()
    tables.truncate(PoliticsTable)
    tables.create_npoli()

random.seed(datetime.now())

if __name__ == '__main__':
    app.run()