#Handles the database 

import mysql.connector 
import datetime 
import time

date = datetime.date.today()

try: 
    mydb = mysql.connector.connect(
        host = "localhost", 
        user = "root",
        password = "root", 
        database = "testbudgettracker"
    )
except mysql.connector.Error as err: 
    print(err)


dbcursor = mydb.cursor()


def scheduledpayments():
    mydb.connect()
    dbcursor.execute("SELECT * FROM sessiontracker WHERE useractive = 1") #checks who is currently logged in
    loggeduser = dbcursor.fetchall()
    


    if loggeduser: 
        for users in loggeduser:
            print(f"[{users[0]}] {users[1]} is online")
        
    else:
        print("No data available")
    mydb.disconnect()


while True:
    scheduledpayments()
    time.sleep(1)