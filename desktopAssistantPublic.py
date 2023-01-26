import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import wikipedia
import os
import operator
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from speech_recognition import Microphone, Recognizer, UnknownValueError
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
from gnews import GNews
from pepperVersionSara import *  # adapted from the pepper module


# method to take and recognize command
def takeCommand():
    r = sr.Recognizer()

    # use microphone module to listen for command
    with sr.Microphone() as source:
        print('Listening')

        # seconds of non-speaking audio before phrase is considered complete
        r.pause_threshold = 0.7
        audio = r.listen(source)

        # check if sound is recognized
        try:
            print("Recognizing")
            Query = r.recognize_google(audio, language='en-in')
            print("the command is printed=", Query)

        except Exception as e:
            print(e)
            print("Say that again, please")
            return "None"

    return Query


def speak(audio):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # set male/female voice
    engine.say(audio)  # make assistant speak
    engine.runAndWait()  # Blocks while processing all the currently queued commands


def tellDay():
    day = datetime.datetime.today().weekday() + 1
    Day_dict = {1: 'Monday', 2: 'Tuesday',
                3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday',
                7: 'Sunday'}

    if day in Day_dict.keys():
        day_of_the_week = Day_dict[day]
        print(day_of_the_week)
        speak("The day is " + day_of_the_week)


def tellTime():
    time = str(datetime.datetime.now())
    print(time)
    hour = time[11:13]
    min = time[14:16]
    speak("The time is" + hour + "Hours and" + min + "Minutes")


def setReminder(reminder):
    fout = open('reminders.txt', 'a')
    fout.write(reminder + '\n')
    fout.close()


class inventory(object):
    # this superclass will take the inventory of the items that are currently on the pantry

    def __init__(self, notepad):
        self.__notepad = notepad

    def query(self):
        # ask user for items to upload into the "pantry inventory" list
        fout = open(self.__notepad, "a")  # open new file to transcribe inventory
        
        speak("please tell me the items you want to add to the inventory")

        status = 0
        while status < 1:
            print("waiting for command")
            food = takeCommand()
            if food != None:  # to make sure that user gave program a command
                fout.write(food + "\n")
                status += 1
                fout.close()


class groceryList(inventory):

    def checkMissing(self):
        # this function will check for the basic items missing from the pantry and add them to the grocery list

        # turn txt file into lists >> grocery list
        grocery_List = open("grocery_List.txt", "r")  # opening the file in read mode
        data = grocery_List.read()  # reading the file
        groceryListList = data.split("\n")  # replacing end splitting the text when newline ('\n') is seen.
        grocery_List.close()

        # turn txt file into lists >> pantry inventory
        pantryInventory = open("pantryInventory.txt", "r")  # opening the file in read mode
        data = pantryInventory.read()  # reading the file
        pantryInventoryList = data.split("\n")  # replacing end splitting the text when newline ('\n') is seen.
        pantryInventory.close()

        fout = open("grocery_List.txt", "a")  # open grocery list to append missing items
        basics = ["bread", "milk", "eggs", "coffee", "chicken", "salmon", "lettuce", "carrots"]

        # read pantry inventory and see what basics are missing
        for item in basics:
            if (item not in groceryListList) and (item not in pantryInventoryList):
                fout.write(item + "\n")

        fout.close()


# deletes them from grocery list and adds them to pantry
def boughtGroceries():
    # turn txt files into a list >> grocery list
    groceryList = open("groceryList.txt", "r")  # open file in read mode
    data = groceryList.read()  # read file
    groceryListList = data.split("\n")  # split text

    fout = open("pantryInventory.txt", "a")  # append to pantry inventory items of grocery list
    fout2 = open("groceryList.txt", "w")  # erase items from shopping list

    for item in groceryListList:
        fout.write(item + "\n")  # append items to pantry inventory

    fout2.write("Grocery List")  # erase items from grocery list
    groceryList.close()


class searchRecipe(object):
    # scrapping the Bon Appétit website for recipe ideas

    def __init__(self, ingredient):
        self.__recipeLink = ""
        self.__ingredient = ingredient
        self.__dicti = {}  # for the names of the recipes
        self.__link = "http://bonappetit.com"
        self.__stepsDicti = {}  # for the steps
        self.__recipeTitle = ''

    def readTitles(self):
        html_txt = requests.get("https://www.bonappetit.com/search?q=" + self.__ingredient).text
        soup = BeautifulSoup(html_txt, "lxml")  # convert to beautiful soup format
        recipe = soup.find_all('article',
                               class_='recipe-content-card')  # find first card (contains all the info for one recipe)

        listt = []
        listLink = []
        for card in recipe:  # find all the recipe names in the first page of the website
            recipe_name = card.find('h4', class_='hed').text  # name/title of recipe
            recipe_link = card.find('a')
            listt += [recipe_name]
            listLink += [(recipe_link['href'])]

        speak("These are the recipes I found")
        count = 1
        # this will print out all the recipes and enumerate them so user can then choose which option to cook based
        # on the # assigned
        for name in listt:
            print(str(count) + '>> ' + str(name))
            count += 1

            # create a dictionary wth a number and the link of the recipe so that I can use it in the next function
            # to get the href
            numbers = 1
            for num in listLink:
                self.__dicti[numbers] = num
                numbers += 1

        return self.__dicti

    def chooseRecipe(self):

        status = 1
        while status == 1:  # so that user can take their time reading the options

            possible_answers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                                '17', '18', '19', '20']
            number = takeCommand().lower()

            if number in possible_answers:
                print("you chose option ", number)

                half_link = self.__link + self.__dicti[int(number)]  # link to the recipe chosen by user
                html_txt = requests.get(half_link).text
                soup = BeautifulSoup(html_txt, "lxml")  # convert to beautiful soup format
                self.__recipeLink += half_link

                title = soup.find('h1',
                                  class_="BaseWrap-sc-UABmB BaseText-fETRLB SplitScreenContentHeaderHed-fxqeFA hkSZSE dZbKMs imKTgC").text
                self.__recipeTitle += title  # so that we can have this info and access it on all functions
                quantity = soup.find('p', class_="BaseWrap-sc-UABmB BaseText-fETRLB Yield-hregIY hkSZSE eXuOnJ fqMLhB")

                speak("we are making " + title + "which yields " + quantity.text)
                status += 1

    def readDescription(self):  # reads the intro paragraph/preface to recipe
        html_txt = requests.get(self.__recipeLink).text
        soup = BeautifulSoup(html_txt, "lxml")
        description = soup.find('div', class_='container--body-inner').text
        print(description)
        speak(description)

    def readIngredients(self):
        html_txt = requests.get(self.__recipeLink).text
        soup = BeautifulSoup(html_txt, "lxml")

        ingredients = soup.find('div', class_='List-Xtjuf hIqrKk').text  # this one finds the whole list of ingredients

        palabras = soup.find_all('div',
                                 class_="BaseWrap-sc-UABmB BaseText-fETRLB Description-dTsUqb hkSZSE kBLSTT gmvWnL")
        numeros = soup.find_all('p', class_="BaseWrap-sc-UABmB BaseText-fETRLB Amount-WAmkd hkSZSE kBLSTT bGuCpx")

        # format the ingredients
        listWords = []
        listNumbers = []

        for word in palabras:
            listWords += [word.text]

        for number in numeros:
            listNumbers += [number.text]

        print("ingredients:")
        for j in range(0, len(listWords)):
            print(listNumbers[j], end="")
            print(' ' + listWords[j])
            speak(listNumbers[j])
            speak(listWords[j])

        speak("if you want to cook the dish now, say 'cook recipe' ")
        speak("or, if you want to add the recipe to a menu say 'add to menu' ")

    def readSteps(self):

        html_txt = requests.get(self.__recipeLink).text
        soup = BeautifulSoup(html_txt, "lxml")

        # find steps
        stepsList = []
        instructions = soup.find_all('div',
                                     class_="BaseWrap-sc-UABmB BaseText-fETRLB InstructionBody-huDCkh hkSZSE hJquu eCKSnz")
        for step in instructions:
            stepsList += [(step).text]

        # dictionary for the steps/procedure
        number = 1
        for step in stepsList:
            self.__stepsDicti[number] = ("step " + str(number) + ": " + step)
            number += 1

        speak("this is the procedure. To continue to next step say 'next, done, or continue' ")
        count = 1
        status = 1

        print(self.__stepsDicti[count])  # print first step
        speak(self.__stepsDicti[count])

        while status < len(stepsList):
            answer = takeCommand().lower()
            if (answer == 'next') or (answer == 'done') or (answer == 'continue'):
                print(" the next step is: ")
                count += 1
                print(self.__stepsDicti[count])
                speak(self.__stepsDicti[count])
                status += 1

        print('all done! bon appetit')
        speak('all done! bon appetit')

    def addToMenu(self):
        # if user doesn't want to cook it right away, they can choose
        # to add the name of the recipe to a menu

        title = self.__recipeTitle
        fout = open('menu.txt', 'a')  # append name of recipe to the menu
        fout.write(title)
        fout.close()


def getNews(command):
    newsLink = {}  # this will save the link of each news title articles
    for i in range(1, 6):  # amount of titles you want printed
        news = command
        print(str(i) + ":  " + news[i]['title'])
        speak(news[i]['title'])
        newsLink[str(i)] = news[i]['url']

    time.sleep(5)

    speak("if you want me to open a particular article, please tell me the number assigned to the news title you would\
     like to read.else, say 'next' ")

    answer = takeCommand().lower()
    if answer == 'next':
        pass
    else:
        link = newsLink[str(answer)]
        speak('opening article on your browser')
        webbrowser.open(link)


def Hello():
    print("hello Sara, I am your desktop assistant! Tell me how may I help you")
    speak("hello Sara, I am your desktop assistant! Tell me how may I help you")


def Take_query():
    Hello()

    while True:
        query = takeCommand().lower()
        recipe = searchRecipe(query)

        # establish values for spotify
        client_id = 'replace with client id'
        client_secret = 'replace with client secret id'
        device_name = 'replace with devide name'
        redirect_uri = 'http://google.com/callback/'
        scope = 'user-read-private user-read-playback-state user-modify-playback-state'
        username = 'replace with spotify username'

        # Connecting to the Spotify account
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            username=username)
        spotify = sp.Spotify(auth_manager=auth_manager)

        # Selecting device to play from
        devices = spotify.devices()
        deviceID = None
        for d in devices['devices']:
            d['name'] = d['name'].replace('’', '\'')
            if d['name'] == device_name:
                deviceID = d['id']
                break

        if "open google" in query:
            speak("Opening Google ")
            webbrowser.open("www.google.com")
            continue

        elif "spotify" in query:
            speak("opening spotify")
            os.system("spotify")
            continue

        elif "which day it is" in query:
            tellDay()
            continue

        elif "tell me the time" in query:
            tellTime()
            continue

        elif "remind me to" in query:
            reminder = query.replace("remind me to", '')
            speak("adding reminder to list")
            setReminder(reminder)
            continue

        elif "calculate" in query:
            def getOperator(op):
                return {
                    '+': operator.add,
                    '-': operator.sub,
                    '*': operator.mul,
                    '/': operator.__truediv__,
                    'Mod': operator.mod,
                    'mod': operator.mod,
                    '^': operator.xor,
                }[op]

            def eval_binary_expr(op1, oper, op2):
                op1, op2 = int(op1), int(op2)
                return getOperator(oper)(op1, op2)

            equation = query.replace('calculate', '')
            print("the answer is" + str(eval_binary_expr(*(equation.split()))))
            speak("the answer is" + str(eval_binary_expr(*(equation.split()))))
            continue


        elif "pantry inventory" in query:
            speak("pantry inventory")
            pantry = inventory("pantryInventory.txt")  # init inventory
            pantry.query()
            continue


        elif "grocery list" in query:
            speak("grocery list")
            shoppingList = groceryList("groceryList.txt")  # init grocery list
            shoppingList.query()  # take list of items for grocery list
            shoppingList.checkMissing()  # add basics missing
            continue


        elif "bought groceries" in query:
            speak("adding items to pantry inventory and resetting shopping list")
            boughtGroceries()
            continue


        elif "find recipe" in query:
            query = query.replace('find recipe for', '')  # get only the item being looked up
            speak("searching recipes for " + query + " on the Bon Appetit website")

            recipe.readTitles()  # find all recipes with the keyword

            speak("which one would you like to prepare? please tell me the number assigned")
            recipe.chooseRecipe()

            speak("would you like to learn more about this dish?")
            if takeCommand() == 'yes':
                speak("ok, lets go!")
                recipe.readDescription()

            speak("the ingredients needed for this dish are: ")
            recipe.readIngredients()
            continue


        elif 'cook recipe' in query:
            recipe.readSteps()
            continue

        elif 'add to menu' in query:
            recipe.addToMenu()
            continue

        elif "from wikipedia" in query:
            speak("Checking the wikipedia ")
            query = query.replace("wikipedia", "")
            # read first 4 sentences
            result = wikipedia.summary(query, sentences=4)
            speak("According to wikipedia")
            print(result)
            speak(result)
            continue

        # the following are part of the spotify features

        elif 'album' in query:
            words = query.split()
            name = ' '.join(words[1:])
            uri = get_album_uri(spotify=spotify, name=name)
            play_album(spotify=spotify, device_id=deviceID, uri=uri)
            continue

        elif 'artist' in query:
            words = query.split()
            name = ' '.join(words[1:])
            uri = get_artist_uri(spotify=spotify, name=name)
            play_artist(spotify=spotify, device_id=deviceID, uri=uri)
            continue


        elif 'play' in query:
            words = query.split()
            name = ' '.join(words[1:])
            uri = get_track_uri(spotify=spotify, name=name)
            play_track(spotify=spotify, device_id=deviceID, uri=uri)
            continue

        elif 'next' in query:
            next_track(spotify=spotify, device_id=deviceID)
            continue

        elif 'stop' in query:
            pause_playback(spotify=spotify, device_id=deviceID)
            continue

        elif 'resume' in query:
            resume_playing(spotify=spotify, device_id=deviceID)
            continue

        elif 'top news' in query:
            getNews(GNews().get_top_news())
            continue

        elif 'find news about' in query:
            topic = query.replace('find news about', '')
            command = GNews().get_news(topic)
            getNews(command)
            continue

        # this will exit and terminate the program
        elif "bye" in query:
            speak("Bye! Have a good one")
            exit()


if __name__ == '__main__':
    Take_query()
