#Imports
from selenium import webdriver
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from credentials import user

VISIBILITY = True

if (VISIBILITY): #Visible mode
    driver = webdriver.Firefox()
    print("Firefox initialized")
else:            #Invisible mode
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options, executable_path="C:\\Utility\\BrowserDrivers\\geckodriver.exe")
    print("Firefox initialized in headless mode")




