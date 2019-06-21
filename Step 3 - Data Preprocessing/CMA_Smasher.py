################################################
# Author:         Ali Fazeli (a84119306)       #
# Huawei Email:   ali.fazeli@huawei.com        #
# Personal Email: a.fazeli95@gmail.com         #
################################################

from glob import glob 
import pandas as pd
import schedule
import datetime
import time
import os


x = datetime.datetime.now()
what_date_is_it = x.strftime("%Y-%m-%d")

# csvs will contain all CMAS node report CSV files names ends with .csv in a list
csvs = glob('CMAS*.csv')
# remove the trailing .csv from CSV files names
list_of_csv_files = [csv for csv in csvs]

def cma_number_calculator(df_statistics):
    cma_node_name = df_statistics.split("__")[0]
    cma_node_brand = df_statistics.split("lte")[0][-1:]
    df_statistics = pd.read_csv(df_statistics, header = None)
    print(cma_node_name)
    
    if cma_node_brand == 'w':
        df_statistics['cma_lte_succ_call_num_separated'] = df_statistics[0].str.split("CMA LTE jion IMSI succ call num:")
        df_statistics['cma_lte_failed_call_num_separated'] = df_statistics[0].str.split("failed call num:")
    elif cma_node_brand == 'c':
        df_statistics['cma_lte_succ_call_num_separated'] = df_statistics[0].str.split("CallModel correlate imsi successful Num:")
        df_statistics['cma_lte_failed_call_num_separated'] = df_statistics[0].str.split("CallModel correlate imsi failed Num:")
    
    # preprocessing for the successful call attempts
    df_succ_call_num = pd.DataFrame()
    df_succ_call_num[['cma_lte_succ_call_num_separated_names','cma_lte_succ_call_num_separated_values']] = pd.DataFrame(df_statistics['cma_lte_succ_call_num_separated'].values.tolist())
    df_succ_call_num['cma_lte_succ_call_num_separated_values'] = pd.to_numeric(df_succ_call_num['cma_lte_succ_call_num_separated_values'], downcast='float')
    df_succ_call_num['cma_lte_succ_call_num_separated_values'] = df_succ_call_num['cma_lte_succ_call_num_separated_values'].dropna()
    # print(df_succ_call_num['cma_lte_succ_call_num_separated_values'].sum())
    sum_of_succ_call_nums = df_succ_call_num['cma_lte_succ_call_num_separated_values'].sum()
    
    # preprocessing for the failed call attempts
    df_failed_call_num = pd.DataFrame()
    df_failed_call_num[['cma_lte_failed_call_num_separated_names','cma_lte_failed_call_num_separated_values']] = pd.DataFrame(df_statistics['cma_lte_failed_call_num_separated'].values.tolist())
    df_failed_call_num['cma_lte_failed_call_num_separated_values'] = pd.to_numeric(df_failed_call_num['cma_lte_failed_call_num_separated_values'], downcast='float')
    df_failed_call_num['cma_lte_failed_call_num_separated_values'] = df_failed_call_num['cma_lte_failed_call_num_separated_values'].dropna()
    # print(df_failed_call_num['cma_lte_failed_call_num_separated_values'].sum())
    sum_of_failed_call_nums = df_failed_call_num['cma_lte_failed_call_num_separated_values'].sum()
    
    # creating the result file report (per CMA node)
    result_columns = ['CMA_Name','Brand_Name','Date','Value','Value_Numbers']
    results = pd.DataFrame(columns=result_columns)
    results.at[0,'CMA_Name'] = cma_node_name
    results.at[1,'CMA_Name'] = cma_node_name
    
    if cma_node_brand == 'w':
        print("Huawei")
        results.at[0,'Brand_Name'] = 'Huawei'
        results.at[1,'Brand_Name'] = 'Huawei'
    elif cma_node_brand == 'c':
        print("Ericsson")
        results.at[0,'Brand_Name'] = 'Ericsson'
        results.at[1,'Brand_Name'] = 'Ericsson'

    results.at[0,'Date'] = what_date_is_it
    results.at[1,'Date'] = what_date_is_it
    results.at[0,'Value'] = 'sum_of_succ_call_nums'
    results.at[1,'Value'] = 'sum_of_failed_call_nums'
    results.at[0,'Value_Numbers'] = sum_of_succ_call_nums
    results.at[1,'Value_Numbers'] = sum_of_failed_call_nums
    results.to_csv("results_{}.csv".format(str(cma_node_name+"__"+cma_node_brand+"__"+what_date_is_it)),index=False)    

def main_area():

    # multiple caller for the main engine
    for raw_csv in list_of_csv_files:
        cma_number_calculator(df_statistics = raw_csv )
    time.sleep(5)

    #  reading the results and make it one singular file (from all the reports we have created by previous step)
    result_csvs = glob('results*.csv')
    result_csv_batch = [pd.read_csv(csv, header = None) for csv in result_csvs]
    #concatenate all dataframes into a single dataframe
    final_df = pd.concat(result_csv_batch,axis=0, ignore_index=True)
    final_df=final_df.drop_duplicates()
    # handling the extra shit...
    new_header = final_df.iloc[0] #grab the first row for the header
    final_df = final_df[1:] #take the data less the header row
    final_df.columns = new_header #set the header row as the final_df header
    final_df.to_csv("Final_Result_{}.csv".format(what_date_is_it), index=False)

    # deleting the redundant stuff
    r_csvs = glob('results*.csv')
    list_of_r_csv_files = [csv for csv in r_csvs]
    for redundant_stuff in list_of_r_csv_files:
        os.remove(redundant_stuff)

    r_csvs = glob('CMAS*.csv')
    list_of_r_csv_files = [csv for csv in r_csvs]
    for redundant_stuff in list_of_r_csv_files:
        os.remove(redundant_stuff)

schedule.every().day.at("23:45").do(main_area)

main_area()
while 1:
    schedule.run_pending()
    time.sleep(1)