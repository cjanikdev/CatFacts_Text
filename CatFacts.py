from selenium import webdriver
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from credentials import user, pw
from sql import sql_user, sql_pw, sql_host, sql_port, sql_db
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import mysql.connector
import re

def debug(msg, context):
    contexts = ["", "[INFO]", "[WARN]", "[ERROR]"]
    if context >= len(contexts) or context < 0:
        context = 0;
    now = datetime.datetime.now()
    prefix = now.strftime("[%Y/%m/%d | %X]") + contexts[context]
    print(prefix, msg)
    return  

class CatFactsBot:
    #Overall bot class
    users = {}
    facts = {}
    commands = {}
    visibility = True  #Change this value manually
    running = False
    tick_delay = 15
    driver = None
    cxn = None
    cursor = None
    iteration = 0
    
    def __init__(self):
        self.commands["help"] = self.help
        return

    def initialize(self):
        #Connect to SQL Server
        debug("Connecting to SQL database", 1)
        self.cxn = mysql.connector.connect(user=sql_user, database=sql_db, password=sql_pw, host=sql_host, port=sql_port)
        self.cursor = self.cxn.cursor()
        debug("Obtaining fact to test connection...", 1)
        self.cursor.execute("SELECT content FROM facts WHERE factID = 10")
        
        for content in self.cursor:
            print(content)

        debug("Connection verified.", 1)

        self.obtain_all_users()
        self.obtain_all_facts()

        self.start_browser()

        if not (self.wait_for_page_load("Username or phone number", 1, 60)):
            debug("Page did not load. Check Internet connection and try again.", 3)
            return False

        self.login()
        self.close_popup()
        
        return True

    def start(self):
        self.running = True

        while self.running:
            start_time = int(round(time.time() * 1000))
            debug("Tick started", 1)
            debug("Reloading Conversations", 1)
            self.wait_for_page_load("(219) 292-4990", 1, 60)
            self.refresh()

            #Check for new messages
            convos = self.find_all_convos()

            #Create new Users if necessary
            for convo in convos:
                if re.sub('[^0-9]','', convo.text) not in self.users.keys() and not convo.text == "Textfree":
                    debug("Unknown user found. Adding user to SQL database.", 2)
                    self.cursor.execute("INSERT INTO catfacts.users (phoneNumber) VALUES ('" + re.sub('[^0-9]','', convo.text) + "')")
                    self.cxn.commit()
                    self.cursor.execute("SELECT userID FROM users WHERE phoneNumber ='" + re.sub('[^0-9]','', convo.text) + "'")
                    for ID in self.cursor:
                        self.users[re.sub('[^0-9]','', convo.text)] = User(self.cursor, ID)
                        
            #Read the messages
            for convo in convos:
                if convo.text == "Textfree":
                    debug("Found Textfree conversation. Skipping.", 1)
                else:
                    convo.find_element_by_xpath("../../..").click()
                    user = self.users[re.sub('[^0-9]','', convo.text)]
                    
                    #Obtain all messages in this convo
                    msgs = user.read_all_messages(self.driver)

                    for msg in msgs:
                        if msg.get_attribute("class") == "text-item ng-binding received-message":
                            prefix = "User:     "
                        else:
                            prefix = "CatFacts: "
                        debug(prefix + str(msg.text), 0)
                        
                    if msgs[len(msgs) - 1].get_attribute("class") == "text-item ng-binding received-message":
                        debug("Most recent message is from the user. Parsing command.", 1)

                        #Parse Command
                        self.parse_cmd(msgs[len(msgs) - 1].text.split(), user)

            #Check iteration
            if self.iteration % 4 == 0:     #Minutely
                debug("Minutely action triggered.", 1)

            if self.iteration % 240 == 0:   #Hourly
                debug("Hourly action triggered.", 1)

            if self.iteration % 5760 == 0:  #Daily
                debug("Daily action triggered.", 1)

            if self.iteration % 40320 == 0: #Weekly
                debug("Weekly action triggered.", 1)

            if self.iteration == 40320 * 2:
                self.iteration = 1

            #Sleep
            if(int(round(time.time() * 1000)) - start_time) <= (self.tick_delay * 1000):
                time.sleep(((self.tick_delay * 1000) - (int(round(time.time() * 1000)) - start_time))/1000)
            self.iteration = self.iteration + 1

    def parse_cmd(self, args, user):
        for key in self.commands.keys():
            debug("Command '" + args[0].lower() + "' found.", 1)
            if key in args[0].lower():
                self.commands[args[0]](args, user)
                return True
        debug("Unknown command entered.", 2)
        return False
                

    def obtain_all_users(self):
        debug("Obtaining all users", 1)
        self.cursor.execute("SELECT userID, phoneNumber FROM users")

        for (userID, phoneNumber) in self.cursor:
            debug("Obtained user " + phoneNumber, 0)
            self.users[phoneNumber] = userID
            
        debug("Converting IDs to users", 1)

        for ID in self.users:
            debug("Converting user " + str(ID), 0)
            self.users[ID] = User(self.cursor, self.users[ID])
            debug(str(self.users[ID].get_phone_number()), 0)
        return

    def obtain_all_facts(self):
        return

    def start_browser(self):
        if (self.visibility): #Visible mode
            self.driver = webdriver.Firefox()
            debug("Firefox initialized", 1)
        else:                 #Invisible mode
            options = Options()
            options.add_argument("--headless")
            self.driver = webdriver.Firefox(firefox_options=options)
            debug("Firefox initialized in headless mode", 1)

        debug("Directing to textfree...", 1)
        self.driver.get("http://www.textfree.us")

        #Verify webpage reached
        if "Textfree" not in self.driver.title:
            debug("The wrong website has been reached. Check Internet connection and try again.", 3)
            return
        else:
            debug("Textfree has been reached", 1)

        return

    def refresh(self):
        refresh_button = self.driver.find_element_by_xpath("//span[@id='topBarRefreshIcon']")
        refresh_button.click()
        return

    def find_all_convos(self):
        debug("Searching for all current conversations...", 1)
        convos = self.driver.find_elements_by_xpath("//div[@ng-bind='vm.getContactAddressName()']")
        debug("Found the following conversations: ", 0)
        for convo in convos:
            debug("Conv ->" + convo.text, 0)
            
        return convos

    def wait_for_page_load(self, evidence, delay, timeout):
        start_time =  int(round(time.time() * 1000))
        debug("Waiting for page load.", 1)
        while evidence not in self.driver.page_source:
            time.sleep(delay)
            if (int(round(time.time() * 1000)) - start_time) >= (timeout * 1000):
                debug("Page could not be loaded.", 3)
                return False
        debug("Page loaded", 1)
        return True

    def login(self):
        debug("Attempting login...", 1)
        
        #Find textboxes
        user_input = self.driver.find_element_by_name("username")
        pw_input = self.driver.find_element_by_name("password")

        #Enter info
        user_input.send_keys(user)
        pw_input.send_keys(pw)

        #Submit
        login_button = self.driver.find_element_by_xpath("//div[@class='sign-in']/button[@class='ng-binding']")
        login_button.click()
        time.sleep(3)
        

        #Validate
        if "Invalid username or password. Typo perhaps?" in self.driver.page_source:
            debug("Invalid username or password. Please check credentials file.", 3)
            return False
        else:
            debug("Login successful.", 1)
            return True

    def close_popup(self):
        popup_X = self.driver.find_element_by_xpath("//div[@ng-click='vm.dismiss()']")
        popup_X.click()
            
    def shutdown(self):
        self.running = False
        return

    def help(self, args, user):
        debug("Help command executed by " + str(user.get_phone_number()), 1)
        user.send_message(self.driver, "You have executed the help command.")

class User:
    CONST_FREQ = ["weekly", "daily", "hourly", "minutely"]
    CONST_DNC = ["OK", "DNC"]
    CONST_PERM = ["admin", "mod", "user", "condemned"]
    first_name = None
    last_name = None
    phone_number = None
    user_ID = None
    frequency = None
    dnc_status = None
    permission_lvl = None

    def __init__(self, cursor, user_ID):
        cursor.execute("SELECT * FROM users WHERE userID = '" + str(user_ID) + "'")
        for (userID, phoneNumber, carrier, frequency, firstName, lastName, dncStatus, permissionLevel) in cursor:
            self.user_ID = userID
            self.set_name(firstName, lastName)
            self.set_phone_number(phoneNumber)
            self.set_frequency(frequency)
            self.set_dnc_status(dncStatus)
            self.set_permission_lvl(permissionLevel)
        return

    def set_first_name(self, name):
        self.first_name = name
        return

    def set_last_name(self, name):
        self.last_name = name
        return

    def set_name(self, first, last):
        self.set_first_name(first)
        self.set_last_name(last)
        return

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_user_ID(self):
        return self.user_ID

    def set_phone_number(self, num):
        self.phone_number = re.sub('[^0-9]','', num)
        return

    def get_phone_number(self):
        return self.phone_number

    def set_frequency(self, freq):
        for freq_opt in self.CONST_FREQ:
            if freq == freq_opt:
                self.frequency = freq
                return
            else:
                self.frequency = "daily"
            return

    def get_frequency(self):
        return self.frequency

    def get_dnc_status(self):
        return self.dnc_status

    def set_dnc_status(self, status):
        for status_opt in self.CONST_DNC:
            if status == status_opt:
                self.dnc_status = status
                return
            else:
                self.dnc_status = "DNC"
            return

    def set_permission_lvl(self, lvl):
        for lvl_opt in self.CONST_PERM:
            if lvl == lvl_opt:
                self.permission_lvl = lvl
                return
            else:
                self.permission_lvl = "user"
            return

    def update_record(self, cursor):
        #cursor.execute("UPDATE users SET phoneNumber = %s, frequency = %s, firstName = %s, lastName = %s, dncStatus = %s, permissionLevel = %s WHERE userID = %d", (phone_number, frequency, first_name, last_name, dnc_status, permission_lvl, user_ID))
        return

    def read_all_messages(self, driver):
        debug("Obtaining all messages for this convo...", 0)
        msgs = driver.find_elements_by_xpath("//div[@class='text-message']/div[@ng-bind-html='vm.getMessageText()']")
        
        return msgs

    def send_message(self, driver, message):
        debug("Creating conversation...", 1)
        
        new_msg_btn = driver.find_element_by_xpath("//div[@ng-click='vm.startNewConversation()']")
        new_msg_btn.click()

        num_bar = driver.find_element_by_xpath("//input[@id='contactInput']")
        num_bar.send_keys(str(self.get_phone_number()) + Keys.ENTER)
        
        debug("Conversation created.", 1)
        
        #Type a message
        debug("Typing message...", 1)
        msg_bar = driver.find_element_by_xpath("//div[@class='emojionearea-editor']")
        debug("Attempting to send message...", 1)
        msg_bar.send_keys(message + Keys.ENTER)
        debug("Message sent.", 1)

        return
        
        
