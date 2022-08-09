
import gspread
import datetime

#importing from spreadsheet
gspread_client = gspread.service_account(filename="C:/Users/cathe/Downloads/furnace-index-card-data-3663bd4611da.json")
spreadsheets = gspread_client.openall()
if spreadsheets:
    print("Available spreadsheets:")
    for spreadsheet in spreadsheets:
        print("Title:", spreadsheet.title, "URL:", spreadsheet.url)
else:
    print("No spreadsheets available")
    print("Please share the spreadsheet with Service Account email")
    print(gspread_client.auth.signer_email)

#taking only the last row 
worksheet = gspread_client.open("Furnace Index Card Form (Responses)").get_worksheet(0)
recent = worksheet.row_values(len(worksheet.col_values(1)))
print(recent)

graph_data = []
time = [0]*7
temp = [0]*7
dwell = [0]*7
if recent[5] == 'Single Zone':
    graph_data.append([-5,25])
    graph_data.append([0,25])
    time[0] = 0
    temp[0] = 25

    for i in range(1,7):
        temp[i] = int(recent[7 + 8*(i-1)])
        time[i] = time[i-1] + dwell[i-1] + (temp[i]-temp[i-1])/int(recent[6 + 8*(i-1)])
        dwell[i] = int(recent[8 + 8*(i-1)])
    
        graph_data.append([time[i], temp[i]])
        graph_data.append([time[i] + dwell[i], temp[i]])
        
        if recent[9 + 8*(i-1)] != 'Yes':
            break
print(graph_data)

timestamp = recent[0]
print(timestamp)

year = int(timestamp.split(" ")[0].split("/")[2])
month = int(timestamp.split(" ")[0].split("/")[0])
day = int(timestamp.split(" ")[0].split("/")[1])
hour = int(timestamp.split(" ")[1].split(":")[0])
minute = int(timestamp.split(" ")[1].split(":")[1])
second = int(timestamp.split(" ")[1].split(":")[2])

sheet_time = datetime.datetime(year, month, day, hour, minute, second)
first_date = datetime.datetime(1970, 1, 1)
time_since =  sheet_time - first_date
seconds = int(time_since.total_seconds())
print(seconds)
