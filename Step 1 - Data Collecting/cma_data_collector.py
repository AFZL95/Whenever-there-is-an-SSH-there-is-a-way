################################################
# Author:         Ali Fazeli (a84119306)       #
# Huawei Email:   ali.fazeli@huawei.com        #
# Personal Email: a.fazeli95@gmail.com         #
################################################

from selenium import webdriver
import time
from io import BytesIO
import codecs
import pytz
import datetime
from datetime import datetime
import os
import shutil
import schedule
import re

list_of_cma_nodes = {'CMAS-192-168-34-52' :'192.168.34.52',
'CMAS-192-168-32-127' :'192.168.32.127',
'CMAS-192-168-35-238' :'192.168.35.238',
'CMAS-192-168-34-138' :'192.168.34.138',
'CMAS-192-168-35-146' :'192.168.35.146',
'CMAS-192-168-36-142' :'192.168.36.142',
'CMAS-192-168-33-51'  :'192.168.33.51',
'CMAS-192-168-34-232' :'192.168.34.232',
'CMAS-192-168-32-204' :'192.168.32.204',
'CMAS-192-168-34-82'  :'192.168.34.82',
'CMAS-192-168-32-109' :'192.168.32.109',
'CMAS-192-168-32-149' :'192.168.32.149',
'CMAS-192-168-33-173' :'192.168.33.173'}


login_address="http://127.0.0.1:8888/"
CEMIP = "10.221.209.28"
CEMUsername= "omc"
CEMPassword = ""
CMA_password = ""
CEMPort = "22"
cc = "ls\n"
defultDirectory= os.getcwd() + "/log"
chromeDriverPath= os.getcwd() + "/chromedriver.exe"

#Definning some basic functions for later usage
def clickOnId(id):
	browser.find_element_by_id(id).click()
	
def clickOnXpath(xpath):
	browser.find_element_by_xpath(xpath).click()

def clickOnClass(class_name):
	browser.find_element_by_class_name(class_name).click()

def TypeInId(id,toBeTyped):
	elems = browser.find_elements_by_id(id)
	elems[0].send_keys(toBeTyped)
	
def TypeInXpath(xpath,toBeTyped):
	elems = browser.find_elements_by_xpath(xpath)
	elems[0].send_keys(toBeTyped)

#Opens Chrome with specific settings
def openBrowser(downloadingDirectory):
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"download.default_directory" : downloadingDirectory+"/Audit_Logs"}
	chromeOptions.add_experimental_option("prefs",prefs)
	chromedriver = chromeDriverPath
	global browser
	browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)
	browser.fullscreen_window()	
	return browser

def login_and_scp(element_ip_address,element_name):
    time.sleep(3)
    TypeInXpath('//*[@id="terminal"]/div','ssh omc@'+element_ip_address+'\n')
    time.sleep(3)
    TypeInXpath('//*[@id="terminal"]/div','yes\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div',CEMPassword+'\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','su\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div',CMA_password+'\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','cd /var/log/appserver/10/CMA/counter/\n')
    time.sleep(1)

    # calculating the common items for further use
    TypeInXpath('//*[@id="terminal"]/div','Now=`date "+%F_"`\n')
    time.sleep(1)  
    TypeInXpath('//*[@id="terminal"]/div','Ip_name="'+element_name+'__"\n')
    time.sleep(1)
    

    # doing the stuff for the Huawei Pool
    TypeInXpath('//*[@id="terminal"]/div','ll hwlte_*\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','tmp_name_H=`ls hwlte_* | head -1`\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','var_H="$Ip_name$Now$tmp_name_H"\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','grep -hnr -C1 "CMA LTE jion IMSI succ call num:" $tmp_name_H > $var_H.csv\n')
    time.sleep(1)   
    # make an scp to the main server of ours and send the desired file to it
    TypeInXpath('//*[@id="terminal"]/div','sudo scp $var_H.csv omc@192.168.32.24:/home/omc/cma_tmp\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div', CEMPassword+'\n')
    time.sleep(3)

    # doing the stuff for the Ericsson Pool
    TypeInXpath('//*[@id="terminal"]/div','ll hwlte_*\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','tmp_name_E=`ls mvericlte_* | head -1`\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','var_E="$Ip_name$Now$tmp_name_E"\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div','grep -hnr -C1 "CallModel correlate imsi failed Num:" $tmp_name_E > $var_E.csv\n')
    time.sleep(1)   
    # make an scp to the main server of ours and send the desired file to it
    TypeInXpath('//*[@id="terminal"]/div','sudo scp $var_E.csv omc@192.168.32.24:/home/omc/cma_tmp\n')
    time.sleep(1)
    TypeInXpath('//*[@id="terminal"]/div', CEMPassword+'\n')
    time.sleep(3)

    # end of tehe process #
    TypeInXpath('//*[@id="terminal"]/div','exit\n')
    time.sleep(1)
    

# Login to PLatform		
def login_to_server(browser):
    browser.get(login_address)
    # time.sleep(3)
    try:
        clickOnXpath('//*[@id="hostname"]')
        TypeInId("hostname",CEMIP)
        time.sleep(1)

        # clickOnXpath('//*[@id="username"]')
        TypeInId("username",CEMUsername)
        time.sleep(1)

        clickOnXpath('//*[@id="password"]')
        TypeInId("password",CEMPassword)
        time.sleep(1)

        clickOnXpath('//*[@id="port"]')
        TypeInId("port",CEMPort)
        time.sleep(1)
        
        clickOnXpath('//*[@id="connect"]/button[1]')
        
        # wait for the platform to load the ssh request
        time.sleep(3)
        
        # loging to the CMA number one and do the stuff (single IP)
        # login_and_scp(element_ip_address = list_of_cma_nodes['CMAS-192-168-34-52'], element_name = 'CMAS-192-168-34-52')

        # loging to the CMA number one and do the stuff for the all CMA nodes
        
        for ip_add in list_of_cma_nodes.items():
            login_and_scp(element_ip_address = ip_add[1], element_name = ip_add[0])
        
        
    except Exception as e:
        print("error :"+ e)
        pass

def main_area():
        #  calling the agents
        downloadingDirectory=defultDirectory+"/TempDownloadingDir"
        browser=openBrowser(downloadingDirectory)
        login_to_server(browser)

schedule.every().day.at("23:15").do(main_area)

main_area()
while 1:
    schedule.run_pending()
    time.sleep(1)
