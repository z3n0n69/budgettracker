from flask import Flask, render_template, request, jsonify, redirect, make_response
import mysql.connector 
from datetime import date, timedelta, datetime
import time

# =====================================
# DATE CONFIGURATION
# =====================================

date_today = date.today()
 

# =====================================
# DATABASE CONFIGURATION
# =====================================


mydb = mysql.connector.connect(
    host = "localhost", 
    user = "root",
    password = "root", 
    database = "testbudgettracker",
    connection_timeout = 30,
    auth_plugin = 'mysql_native_password'
)







# =====================================
# DATABASE CLASS
# =====================================

class dbfunctions:
    def __init__(self, username):
        self.username = username
    
    def createuser(self):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute("SELECT MAX(userID) FROM users")
        userid_count = dbcursor.fetchone()[0]
        dbcursor.execute(f"SELECT * FROM users WHERE username = %s" , (self.username, ))
        usernamecheck = dbcursor.fetchone()

        if userid_count == None and usernamecheck == None: 
            userid_count = 1 
            dbcursor.execute(f"INSERT INTO users (userID, username) VALUES (%s,%s)", (userid_count, self.username))
            dbcursor.execute(f"INSERT INTO sessiontracker (userID, username, useractive) VALUES (%s,%s,%s)", (userid_count,self.username,1))
            dbcursor.execute(f"INSERT INTO money (userID, username, balance) VALUES (%s,%s,%s)", (userid_count, self.username, 0))
            mydb.commit()
            logininfo = [self.username, userid_count]
            return logininfo
        
        elif userid_count and usernamecheck == None: 
            userid_count = int(userid_count)
            userid_count += 1 
            dbcursor.execute(f"INSERT INTO users (userID, username) VALUES (%s,%s)", (userid_count, self.username))
            dbcursor.execute(f"INSERT INTO sessiontracker (userID, username, useractive) VALUES (%s,%s,%s)", (userid_count,self.username,1))
            dbcursor.execute(f"INSERT INTO money (userID, username, balance) VALUES (%s,%s,%s)", (userid_count, self.username, 0))
            mydb.commit()
            logininfo = [self.username, userid_count]
            return logininfo
        
        elif usernamecheck:
            return "existing user"
    
    def loginvalidation(self):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT * FROM users WHERE username = %s", (self.username, ))
        result = dbcursor.fetchone()
        print(result)
        if result == None:
            return "None"
        else: 
            return result
    
    def add_expenses(self,  userID, description, amount): 
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT MAX(transaction_id) FROM expenses WHERE userID = %s", (userID, ))
        transaction_idcheck = dbcursor.fetchone()[0]
        if transaction_idcheck == None: 
            transaction_id = 1 
            dbcursor.execute(f"INSERT INTO expenses (userID, username, transaction_id, expense_description, amount) VALUES (%s, %s,%s,%s,%s)" , (userID, self.username, transaction_id, description, amount))
            mydb.commit()
        else: 
            transaction_id = transaction_idcheck + 1 
            dbcursor.execute(f"INSERT INTO expenses (userID, username, transaction_id, expense_description,amount) VALUES (%s, %s,%s,%s,%s)", (userID, self.username, transaction_id, description, amount))
            mydb.commit() 

    def remove_expenses(self, userID, transactionid):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT userID FROM expenses WHERE transaction_id = %s", (int(transactionid), ))
        result = dbcursor.fetchone()
        if result == None: 
            return "invalid"
        else: 
            dbcursor.execute(f"DELETE FROM expenses WHERE transaction_id = %s", (int(transactionid), ))
            mydb.commit()
            return "deleted"
    def addremove_money(self, userID, username, balance, option):
        dbcursor = mydb.cursor(buffered = True)
        if option == "add":
            dbcursor.execute(f"INSERT INTO money (userID, username, balance) VALUES(%s,%s,%s)",(userID, username, balance))
            mydb.commit()
        elif option == "remove":
            balance = 0 - balance 
            dbcursor.execute(f"INSERT INTO money (userID, username, balance) VALUES (%s,%s,%s)",(userID, username, balance))
            mydb.commit()
    
    def schedulepayment(self, userID, paymentname, amount , duedate):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT scheduleid FROM scheduledpayments WHERE username = %s", (self.username, ))
        scheduleid = dbcursor.fetchone()
        if scheduleid == None:
            scheduleid = 1
            dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)", (userID, self.username,scheduleid,paymentname,amount,duedate))
            mydb.commit()
        else:
            scheduleid = scheduleid[0]+ 1 
            dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)", (userID, self.username,scheduleid,paymentname,amount,duedate))
            mydb.commit()
    
    def multischedule(self, userID, paymentname, amount, duedate, scheduletype, months,enddate):
        dbcursor = mydb.cursor(buffered = True)
        print("[MULTI SCHEDULE FUNCTION INITIALIZED]")
        dbcursor.execute(f"SELECT scheduleid from scheduledpayments WHERE username = %s", (self.username, ))
        scheduleid = dbcursor.fetchone()


        if scheduleid == None: 
            scheduleid = 1
            startdate = datetime.strptime(duedate, "%Y-%m-%d").date()
            enddate = datetime.strptime(enddate, "%Y-%m-%d").date()
            print(f"START DATE: {startdate}")
            processed_date = None
            if scheduletype == "biweekly": 
                for i in range(months): 
                    startdate = startdate + timedelta(weeks = 2)
                    dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)",(userID,self.username,scheduleid,paymentname, amount, startdate))
                    mydb.commit()
                    scheduleid = scheduleid + 1
                    startdate = startdate
            #work on semi monthly
            elif scheduletype== "semimonthly": #prototype
                    print("[SCHEDULED ID == NONE ELIF SCHEDULETYPE]")
                    startdate_day = startdate.day
                    enddate_day = enddate.day
                    print(f"[START DATE DAY:{startdate_day}]")
                    print(f"[END DATE DAY: {enddate_day}]")
                    for i in range(months): 
                        processed_date = startdate + timedelta(weeks = 4)
                        processed_date = f"{processed_date.year}-{processed_date.month}-{startdate_day}"
                        print(f"Processed_Date: {processed_date}")
                        dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)",(userID,self.username,scheduleid,paymentname, amount, processed_date))
                        mydb.commit()
                        processed_date = datetime.strptime(processed_date, "%Y-%m-%d").date()
                        scheduleid = scheduleid + 1
                        processed_date = f"{processed_date.year}-{processed_date.month}-{enddate_day}"
                        print(f"Processed_Date: {processed_date}")
                        dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)",(userID,self.username,scheduleid,paymentname, amount, processed_date))
                        mydb.commit()
                        startdate = datetime.strptime(processed_date, "%Y-%m-%d").date()
                        scheduleid = scheduleid + 1
                        

        elif scheduleid:
            scheduleid = scheduleid[0] + 1
            startdate = datetime.strptime(duedate, "%Y-%m-%d").date()
            if scheduletype == "biweekly": 
                for i in range(months):
                    dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)",(userID,self.username,scheduleid,paymentname, amount, startdate))
                    mydb.commit()
                    scheduleid = scheduleid + 1
                    startdate = startdate
                    
            elif scheduletype== "semimonthly": #prototype
                    print("[SCHEDULED ID == VALUE ELIF SCHEDULETYPE]")
                    startdate_day = startdate.day
                    enddate_day = enddate.day
                    print(f"[START DATE DAY:{startdate_day}]")
                    print(f"[END DATE DAY: {enddate_day}]")
                    for i in range(months): 
                        processed_date = startdate + timedelta(weeks = 4)
                        processed_date = f"{processed_date.year}-{processed_date.month}-{startdate_day}"
                        print(f"Processed_Date: {processed_date}")
                        dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)",(userID,self.username,scheduleid,paymentname, amount, processed_date))
                        mydb.commit()
                        scheduleid = scheduleid + 1
                        processed_date = datetime.strptime(processed_date, "%Y-%m-%d").date()
                        processed_date = f"{processed_date.year}-{processed_date.month}-{enddate_day}"
                        print(f"Processed_Date: {processed_date}")
                        dbcursor.execute(f"INSERT INTO scheduledpayments(userID, username, scheduleid, paymentname, amount, duedate) VALUES(%s,%s,%s,%s,%s,%s)",(userID,self.username,scheduleid,paymentname, amount, processed_date))
                        mydb.commit()
                        startdate = datetime.strptime(processed_date, "%Y-%m-%d").date()
                        scheduleid = scheduleid + 1
                    
                    
            
#GET REQUEST

class fetchdb:
    def __init__(self, username):
        self.username = username
    def expenses(self):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT * FROM expenses WHERE username = %s", (self.username, ))
        fetch_result = dbcursor.fetchall()
        print(fetch_result)
        return fetch_result

    def money(self):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT balance FROM money WHERE username = %s", (self.username,)) 
        fetch_result = dbcursor.fetchall()
        return fetch_result   

    def expenseamount(self):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT amount FROM expenses WHERE username = %s", (self.username,))
        fetch_result = dbcursor.fetchall()
        return fetch_result

    def schedule(self):
        dbcursor = mydb.cursor(buffered = True)
        dbcursor.execute(f"SELECT * FROM scheduledpayments WHERE username = %s", (self.username, ))
        fetch_result = dbcursor.fetchall()
        print(date.today())
        return fetch_result

# =====================================
# FLASK APPLICATION
# ===================================== 

app = Flask(__name__)


# =====================================
# PAGE ROUTES
# ===================================== 
@app.route('/') #Main page 

def indexpage():
    return render_template('index.html')




@app.route('/signuppage') #create a new user
def signuppage():
    return render_template('signup.html')


@app.route('/createuser', methods = ['POST']) #signup function 
def createuser():
    submittedusername = request.form.get('username')
    print(submittedusername)
    dbrequest = dbfunctions(submittedusername)
    query_result = dbrequest.createuser()
    print(query_result)
    if query_result == "existing user": 
        return f"user {submittedusername} already exists"
    else: 
        cookiemaker = redirect('/dashboard')
        cookiemaker.set_cookie("username", query_result[0], max_age=60*60*24)
        cookiemaker.set_cookie("userID", str(query_result[1]), max_age = 60*60*24)
        return cookiemaker
        



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@app.route('/loginpage') #loginpage 

def loginpage():
    return render_template('login.html')

@app.route('/submitlogin', methods = ['POST']) #Login functions 
def submitlogin():
    submittedusername = request.form.get('username')
    dbrequest = dbfunctions(submittedusername)
    query_result = dbrequest.loginvalidation()
    
    print(query_result)

    if query_result == "None":
        return f"No {submittedusername} in the database. Please try again."
    else:
        cookiemaker = redirect('/dashboard')
        cookiemaker.set_cookie("username", query_result [1], max_age = 60*60*24)
        cookiemaker.set_cookie("userID", str(query_result[0]), max_age = 60*60*24)
        return cookiemaker

@app.route('/logout') #logout
def logout():
    return redirect('/')

@app.route('/schedule')
def schedulepage():
    return render_template('schedule.html')

# =====================================
# POST REQUEST
# ===================================== 

@app.route('/addremove_expense', methods = ['POST'])

def addremove_expense(): 
    user = request.cookies.get('username')
    userid = int(request.cookies.get('userID'))
    option = request.form.get("addremove") 
    dbrequest = dbfunctions(user)
    print(f"user selected {option}")
    
    if option == "add": 
        expense_descriptionweb = request.form.get('expenseDescription')
        expense_amountweb = request.form.get('expenseAmount')
        dbrequest.add_expenses(userid, expense_descriptionweb,expense_amountweb) 
        return redirect('/dashboard')
    
    elif option == "remove":
        input_transactionID = request.form.get('transactionID')
        request_result = dbrequest.remove_expenses(userid,input_transactionID)
        if request_result == "deleted": 
            return redirect('/dashboard')
        elif request_result == "invalid":
            return "Transaction ID not found"
        else: 
            return "something went wrong with the request"


        
@app.route('/addremove_money', methods = ['POST'])

def addremove_money(): 
    user = request.cookies.get('username')
    userid = int(request.cookies.get('userID'))
    input_balance = int(request.form.get('input_money'))
    option = request.form.get('addremove')

    dbrequest = dbfunctions(user)
    dbrequest.addremove_money(userid,user,input_balance,option)
    return redirect('/dashboard')

@app.route('/addschedule', methods = ['POST'])
def addschedule():
    user = request.cookies.get('username')
    userid = int(request.cookies.get('userID'))
    paymentname = request.form.get('name')
    paymentamount = request.form.get('amount')
    scheduleddate = request.form.get('duedate')
    dbrequest = dbfunctions(user)
    dbrequest.schedulepayment(userid, paymentname, paymentamount, scheduleddate)
    print(scheduleddate)
    return redirect('/schedule')


@app.route('/multischedule', methods = ['POST'])

def multischedule():
    user = request.cookies.get('username')
    userid = int(request.cookies.get('userID'))
    paymentname = request.form.get('name')
    paymentamount = request.form.get('amount')
    scheduleddate = request.form.get('duedate')
    scheduletype = request.form.get('scheduletype')
    enddate = request.form.get('enddate')
    months = int(request.form.get('months'))
    dbrequest = dbfunctions(user)
    dbrequest.multischedule(userid, paymentname, paymentamount,scheduleddate,scheduletype,months, enddate)
    return redirect('/schedule')
#STILL WORKING ON THIS
    

    
    



# =====================================
# GET REQUEST
# ===================================== 

@app.route('/fetch_expenses', methods=['GET'])
def fetch_expenses():

    user = request.cookies.get('username')
    dbrequest = fetchdb(user)
    result = dbrequest.expenses()

    expense_list = []

    for row in result: 
        expense_list.append({
            "username": row[1],
            "transaction_ID": row[2],
            "transaction_name": row[3],
            "amount": row[4]
        })

    return jsonify(expense_list)

@app.route('/fetch_balance', methods = ['GET'])

def fetch_balance():
    user = request.cookies.get('username')
    dbrequest = fetchdb(user)
    balance_result = dbrequest.money()
    expense_result = dbrequest.expenseamount()
    balance = []
    expenses = []
    

    for row in expense_result:
        expenses.append(row[0])

        
    for row in balance_result:
        balance.append(row[0])


    total_balance = sum(balance)
    total_expenses = sum(expenses)
    fordisplay = total_balance - total_expenses
    return_json = [{"money":fordisplay}]
    return jsonify(return_json)


@app.route('/fetch_schedule', methods = ['GET'])

def fetch_schedule():
    user = request.cookies.get('username')
    dbrequest = fetchdb(user)
    dbrequest_result = dbrequest.schedule()
    print(dbrequest_result)
    scheduledpaymentslist = []
    for row in dbrequest_result:
         scheduledpaymentslist.append({
             "scheduleID": row[2], 
             "schedule_name": row[3],
             "schedule_amount": row[4], 
             "schedule_date":row[5]
         })
    print(scheduledpaymentslist)
    
    return jsonify(scheduledpaymentslist)
    


if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')

