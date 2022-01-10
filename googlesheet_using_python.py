
#https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/
# importing the required libraries
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('botany-323415-9b4259b41fa1.json', scope)

# authorize the clientsheet 
client = gspread.authorize(creds)

# get the instance of the Spreadsheet
sheet = client.open('Flora_data')

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)

# get the total number of columns
sheet_instance.col_count
## >> 26


# get the value at the specific cell
sheet_instance.cell(col=3,row=3)
## >> <Cell R2C3 '63881'>

# get all the records of the data
records_data = sheet_instance.get_all_records()

# view the data
records_data

# convert the json to dataframe
records_df = pd.DataFrame.from_dict(records_data)

# view the top records
records_df.head()

