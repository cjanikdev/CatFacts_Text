#Imports
from selenium import webdriver
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from credentials import user
from credentials import pw
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

def main():
        #Create bot
        catFactsBot = CatFactsBot()

        #Initialize bot
        catFactsBot.initialize()

        #Log in
        if catFactsBot.login() == False:
            return
        
        #Close popup
        if not (catFactsBot.wait_for_page_load("vm.dismiss()", 1, 60)):
            return
        catFactsBot.close_popup()
        
        #Start loop
        catFactsBot.start()

        #Finish
        catFactsBot.debug("Program terminated.")
        return

class CatFactsBot:
    #Overall bot class

    visibility = True
    running = False
    tick_delay = 15
    driver = None
    
    def __init__(self):
        return

    def initialize(self):
        #Start browser and connect to website
        self.start_browser()
        self.debug("Directing to textfree")
        self.driver.get("https://www.textfree.us")

        #Verify that the website is correct
        if "Textfree" not in self.driver.title:
            self.debug("The wrong website has been reached. Check Internet connection and try again.")
            return
        else:
            self.debug("Textfree has been reached")

        #Wait for page to load
        if not (self.wait_for_page_load("Username or phone number", 1, 60)):
            return

    def start(self):
        #Start loop
        self.running = True
        
        while self.running:
            start_time = int(round(time.time() * 1000))
            self.debug("Tick started")
            self.debug("Reloading Conversations")
            self.wait_for_page_load("(219) 292-4990", 1, 60)
            self.refresh()
            
            #Check for new messages
            convos = self.find_all_convos()
            unread = self.find_all_unread_convos(convos)
            
            #Check time

                #If time is appropriate, send message to each subscriber

            #Sleep
            if(int(round(time.time() * 1000)) - start_time) <= (self.tick_delay * 1000):
                time.sleep(((self.tick_delay * 1000) - (int(round(time.time() * 1000)) - start_time))/1000)

    def find_all_convos(self):
        self.debug("Searching for all current conversations...")
        convos = self.driver.find_elements_by_xpath("//div[@ng-bind='vm.getContactAddressName()']")
        self.debug("Found the following conversations: ")
        for convo in convos:
            self.debug("Conv ->" + convo.text)
        return convos

    def find_all_unread_convos(self, convos):
        unread = []
        self.debug("Searching for all unread conversations...")
        self.debug("Found the following unread conversations: ")
        for convo in convos:
            if convo.find_element_by_xpath("../div[@ng-show='vm.showUnreadMessages()']").is_displayed():
                unread.append(convo)
                self.debug("Unr Conv-> " + convo.text)
        return unread

    def close_popup(self):
        popup_X = self.driver.find_element_by_xpath("//div[@ng-click='vm.dismiss()']")
        popup_X.click()

    def set_visibility(self, boolean):
        if(boolean == True):
            self.visibility = True
        elif(boolean == False):
            self.visibility = False
        else:
            return

    def get_visibility(self):
        return (self.visibility)

    def set_tick_delay(self, delay):
        self.tick_delay = delay

    def get_tick_delay(self):
        return (self.tick_delay)
    
    def wait_for_page_load(self, evidence, delay, timeout):
        start_time =  int(round(time.time() * 1000))
        self.debug("Waiting for page load.")
        while evidence not in self.driver.page_source:
            time.sleep(delay)
            if (int(round(time.time() * 1000)) - start_time) >= (timeout * 1000):
                debug("Page could not be loaded.")
                return False
        self.debug("Page loaded")
        return True

    def debug(self, message):
        now = datetime.datetime.now()
        prefix = now.strftime("[%Y/%m/%d | %X]")
        print(prefix, message)
        return
        
    def refresh(self):
        refresh_button = self.driver.find_element_by_xpath("//span[@id='topBarRefreshIcon']")
        refresh_button.click()
        return

    def send_message(self, message):
        #Type a message
        self.debug("Typing message...")
        msg_bar = self.driver.find_element_by_xpath("//div[@class='emojionearea-editor']")
        self.debug("Attempting to send message...")
        msg_bar.send_keys(message + Keys.ENTER)
        self.debug("Message sent.")

    def send_new_message(self, message, recipient):
        #Start a new convo
        self.debug("Creating conversation...")
        
        new_msg_btn = self.driver.find_element_by_xpath("//div[@ng-click='vm.startNewConversation()']")
        new_msg_btn.click()

        num_bar = self.driver.find_element_by_xpath("//input[@id='contactInput']")
        num_bar.send_keys(recipient + Keys.ENTER)
        
        self.debug("Conversation created.")
        
        self.send_message(message)
        return

    def login(self):
        self.debug("Attempting login...")
        
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
            self.debug("Invalid username or password. Please check credentials file.")
            return False
        else:
            self.debug("Login successful.")
            return True

    def start_browser(self):
        if (self.visibility): #Visible mode
            self.driver = webdriver.Firefox()
            self.debug("Firefox initialized")
        else:            #Invisible mode
            options = Options()
            options.add_argument("--headless")
            self.driver = webdriver.Firefox(firefox_options=options)
            self.debug("Firefox initialized in headless mode")
    

    



main()
