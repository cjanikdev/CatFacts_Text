#Imports
from selenium import webdriver
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from credentials import user
from credentials import pw
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

VISIBILITY = True
RUNNING = True

def main():
        #Start browser and connect to website
        driver = start_browser()
        print("Directing to textfree")
        driver.get("https://www.textfree.us")

        #Verify that the website is correct
        if "Textfree" not in driver.title:
            print("The wrong website has been reached. Check Internet connection and try again.\n")
            return
        else:
            print("Textfree has been reached\n")

        if login(driver) == False:
            return

        #Close popup
        time.sleep(1)
        popup_X = driver.find_element_by_xpath("//div[@ng-click='vm.dismiss()']")
        popup_X.click()
        time.sleep(1)

        #Start loop
        while RUNNING:

            #Check for new messages
            
            
            #Check time

                #If time is appropriate, send message to each subscriber

            #Sleep
        

        print("Program terminated.")
        return
    
def get_all_senders(driver):
    convos = driver.find_elements_by_xpath("div[@ng-bind='vm.getContactAddressName()']")
    return convos

def send_message(driver, message):
    #Type a message
    print("Typing message...")
    msg_bar = driver.find_element_by_xpath("//div[@class='emojionearea-editor']")
    print("Attempting to send message...")
    msg_bar.send_keys(message + Keys.ENTER)
    print("Message sent.\n")

def send_new_message(driver, message, recipient):
    #Start a new convo
    print("Creating conversation...")
    new_message(driver, recipient)
    print("Conversation created.\n")
    
    send_message(driver, message)
    
    return

def new_message(driver, recipient):
    new_msg_btn = driver.find_element_by_xpath("//div[@ng-click='vm.startNewConversation()']")
    new_msg_btn.click()

    num_bar = driver.find_element_by_xpath("//input[@id='contactInput']")
    num_bar.send_keys(recipient + Keys.ENTER)
    
    
    return

def select_conversation():
    return

def login(driver):
        print("Attempting login...")

        time.sleep(1)
        
        #Find textboxes
        user_input = driver.find_element_by_name("username")
        pw_input = driver.find_element_by_name("password")

        #Enter info
        user_input.send_keys(user)
        pw_input.send_keys(pw)

        #Submit
        login_button = driver.find_element_by_xpath("//div[@class='sign-in']/button[@class='ng-binding']")
        login_button.click()
        time.sleep(3)
        

        #Validate
        if "Invalid username or password. Typo perhaps?" in driver.page_source:
            print("Invalid username or password. Please check credentials file.")
            return False
        else:
            print("Login successful.\n")
            return True
    

def start_browser():
    if (VISIBILITY): #Visible mode
        driver = webdriver.Firefox()
        print("Firefox initialized\n")
    else:            #Invisible mode
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options)
        print("Firefox initialized in headless mode\n")
    return driver

main()
