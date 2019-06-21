################################################
# Author:         Ali Fazeli (a84119306)       #
# Huawei Email:   ali.fazeli@huawei.com        #
# Personal Email: a.fazeli95@gmail.com         #
################################################

import os
import pysftp
import datetime
import time
from glob import glob 
import schedule

myHostname = "10.221.209.28"
myUsername = "omc"
myPassword = ""
where_to_seek = "/home/omc/cma_tmp/"
localFilePath = os.getcwd()+ "/cma_tmp/"
# where to save the downloaded data
desired_folder = str(localFilePath)

x = datetime.datetime.now()
what_date_is_it = x.strftime("%Y-%m-%d")

# ignoring the SSH private key
my_cnopts = pysftp.CnOpts()
my_cnopts.hostkeys = None 


def delete_the_past_data():
    # deleting the redundant stuff
    previous_csvs = glob(localFilePath+'CMAS*.csv')
    list_of_redundant_csv_files = [csv for csv in previous_csvs]
    for redundant_stuff in list_of_redundant_csv_files:
        os.remove(redundant_stuff)

def download_todays_data():
    with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword, cnopts=my_cnopts) as sftp:
        print("Connection succesfully stablished ... ")

        # Switch to a the appropriate directory
        sftp.cwd(where_to_seek)

        # Obtain structure of the remote directory 
        directory_structure = sftp.listdir_attr()

    # Print the stuff
    #     for attr in directory_structure:
    #         print (attr.filename, attr)
        for attr in directory_structure:
            try:
                if attr.filename.split("__")[1][:10] == what_date_is_it :

                    sftp.get(where_to_seek+"/"+str(attr.filename), desired_folder+str(attr.filename))
                    print(attr.filename)
            except:
                print ("no matter mate!")
    # connection closed automatically at the end of the with-block


def main_area():
    try:
        delete_the_past_data()
        download_todays_data()
    except Exception as error: 
        print (str(error))
    

schedule.every().day.at("23:40").do(main_area)

main_area()
while 1:
    schedule.run_pending()
    time.sleep(1)