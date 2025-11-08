# THIS SHIT IS BROKEN

from flask import Flask, render_template, request, jsonify, redirect, make_response
import mysql.connector 
 

# =====================================
# DATABASE CONFIGURATION
# =====================================

# Tables 
users = "users"
expenses = "expenses"
money = "money"
scheduledpayments = "scheduledpayments"

# Database connection 
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root", 
        password="root",
        database="testbudgettracker"
    )
except mysql.connector.Error as error:
    print(error)

dbcursor = mydb.cursor() 


# =====================================
# DATABASE CLASS
# =====================================
class myDB: 
    def __init__(self, table):
        self.table = table 

    def fetch_username(self, info):
        dbcursor.execute(f"SELECT * FROM {self.table} WHERE username = \"{info}\"")
        results = dbcursor.fetchall()
        return results
    
    def fetch_db(self, username):
        dbcursor.execute(f"SELECT * FROM {self.table} WHERE username = \"{username}\"")
        results = dbcursor.fetchall()
        return results
    
    def fetch_scheduledpayments(self, username):
        dbcursor.execute(f"SELECT * FROM {self.table} WHERE username = %s", (username,))
        results = dbcursor.fetchall()
        return results
    
    def add_usernametoDB(self, username):  # For register page
        dbcursor.execute(f"SELECT MAX(userID) FROM {users}")
        userid_checker = dbcursor.fetchone()[0]
        dbcursor.execute(f"SELECT MAX(userID) FROM {money}")
        moneyid_checker = dbcursor.fetchone()[0]
        
        if userid_checker == None and moneyid_checker == None: 
            userid = 1
            dbcursor.execute(f"INSERT INTO {users} (userID, username) VALUES (%s, %s)", (userid, username))
            dbcursor.execute(f"INSERT INTO {money} (userID, username, balance) VALUES (%s, %s, 0)", (userid, username))
            dbcursor.execute(f"INSERT INTO sessiontracker (userID, username, useractive) VALUES (%s,%s,0)", (userid, username))
            mydb.commit()
            return userid
        else:
            userid = userid_checker
            userid += 1 
            dbcursor.execute(f"INSERT INTO {users} (userID, username) VALUES (%s, %s)", (userid, username))
            dbcursor.execute(f"INSERT INTO {money} (userID, username, balance) VALUES (%s, %s, 0)", (userid, username))
            dbcursor.execute(f"INSERT INTO sessiontracker (userID, username, useractive) VALUES (%s,%s,0)", (userid, username))
            mydb.commit()
            return userid
        
    def add_expensetoDB(self, usernamecookie, input_expense_name, input_expense_amount):  # Add to expense database 
        dbcursor.execute(f"SELECT MAX(transaction_ID) FROM {expenses}") 
        transactionID_count = dbcursor.fetchone()[0]
        print(transactionID_count)
        
        if transactionID_count == None:
            transactionID_count = 0
            dbcursor.execute(
                f"INSERT INTO {expenses} (username, transaction_ID, transaction_name, amount) VALUES (%s, %s, %s, %s)", 
                (usernamecookie, transactionID_count, input_expense_name, input_expense_amount)
            )
            mydb.commit()
        else:
            transactionID_count = transactionID_count + 1 
            dbcursor.execute(
                f"INSERT INTO {expenses} (username, transaction_ID, transaction_name, amount) VALUES (%s, %s, %s, %s)", 
                (usernamecookie, transactionID_count, input_expense_name, input_expense_amount)
            )
            mydb.commit()
    
    def add_moneytoDB(self, username, amount):
        dbcursor.execute(f"SELECT balance FROM {money} WHERE username = %s", (username,))
        currentbalance = dbcursor.fetchone()[0]
        print(type(currentbalance), type(amount))
        
        setbalance = currentbalance + amount
        dbcursor.execute(f"UPDATE {money} SET balance = %s WHERE username = %s", (setbalance, username))
        mydb.commit()

    def remove_expensetoDB(self, transactionID):
        dbcursor.execute(f"DELETE FROM {self.table} WHERE transaction_ID = %s", (transactionID,)) 
        mydb.commit() 
    
    def add_schedulepaymentstoDB(self, username, schedulename, scheduleamount, scheduledate):
        dbcursor.execute(
            f"INSERT INTO {self.table}(username, schedulename, scheduleamount, scheduledate) VALUES (%s, %s, %s, %s)",
            (username, schedulename, scheduleamount, scheduledate)
        )
        mydb.commit() 
    
    def usertrackerDB(self, username, status):
        dbcursor.execute(f"UPDATE sessiontracker SET useractive = {status} WHERE username = %s", (username, ))
        mydb.commit()




# =====================================
# FLASK APPLICATION
# =====================================
app = Flask(__name__)


# ---------- ROUTES ----------

@app.route('/')  # Main page
def indexpage():
    return render_template('index.html')


@app.route('/loginpage')  # Login page
def loginpage():
    return render_template('login.html')


@app.route('/signuppage')  # Signup page 
def signuppage():
    return render_template('signup.html')


@app.route('/dashboard')  # Dashboard
def render_dashboard():
    return render_template('dashboard.html')


@app.route('/schedule')
def render_schedule(): 
    return render_template('schedule.html')


# ---------- AUTH ----------

@app.route('/createuser', methods=['POST'])  # To create user in the database
def createuser(): 
    submittedusername = request.form.get("username")
    print("createuser() activated " + submittedusername)
    
    dbrequest = myDB(users)
    userid = dbrequest.add_usernametoDB(submittedusername)
    if submittedusername: 
        print(userid)
        cookiemaker = redirect("dashboard")
        cookiemaker.set_cookie("username", submittedusername, max_age=60*60*24)
        cookiemaker.set_cookie("userid",str(userid),  max_age=60*60*24)
        return cookiemaker
    else: 
        return "Shit happened. dont know what tho"

@app.route('/logout')
def logout():
    username_cookie = request.cookies.get("username")
    tracksession = myDB("sessiontracker")
    tracksession.usertrackerDB(username_cookie, 0)
    return redirect('/loginpage')

@app.route('/submitlogin', methods=['POST'])  # Validation for login 
def validateLogin():
    submittedusername = request.form.get("username") 
    dbrequest = myDB(users)
    result = dbrequest.fetch_username(submittedusername)
    tracksession = myDB("sessiontracker")
    
    if result: 
        cookiemaker = redirect("/dashboard")
        cookiemaker.set_cookie("username", submittedusername, max_age=60*60*24)
        tracksession.usertrackerDB(submittedusername, 1)
        return cookiemaker

    else: 
        return f"No {submittedusername} in the database"


# ---------- MONEY ----------

@app.route('/add_money', methods=['POST'])
def add_money():
    username_cookie = request.cookies.get("username")
    input_money = int(request.form.get("input_money"))
    
    dbrequest = myDB(money) 
    dbrequest.add_moneytoDB(username_cookie, input_money)
    return redirect("/dashboard")


# ---------- EXPENSES ----------

@app.route('/addremove_expense', methods=['POST'])  # To add or remove an expense 
def addremove_expense():
    expense_editopt = request.form.get("addremove")
    expense_description = request.form.get("expenseDescription")
    expense_amount = request.form.get("expenseAmount")
    expense_transactionID = request.form.get("transactionID")
    
    dbrequest = myDB(expenses)
    username_cookie = request.cookies.get("username")
    
    print(expense_editopt)
    print(expense_transactionID)
    
    if username_cookie:
        if expense_editopt == "add":
            dbrequest.add_expensetoDB(username_cookie, expense_description, expense_amount)
            return redirect("/dashboard")
        else:
            dbrequest.remove_expensetoDB(expense_transactionID)
            return redirect("dashboard")
    else: 
        return "error occured"


# ---------- SCHEDULED PAYMENTS ----------

@app.route('/addschedule', methods=['POST'])
def add_schedule(): 
    print("adding a schedule")
    username_cookie = request.cookies.get('username')
    schedname = request.form.get('name')
    schedamount = request.form.get('amount')
    scheddate = request.form.get('duedate')
    
    dbrequest = myDB(scheduledpayments)
    dbrequest.add_schedulepaymentstoDB(username_cookie, schedname, schedamount, scheddate)
    
    print(username_cookie, schedname, schedamount, scheddate)
    return redirect('/schedule')




# ---------- FETCH FUNCTIONS FOR FRONTEND ----------

@app.route("/fetch_balance", methods=['GET'])  # Get updates from the money database
def fetch_balance(): 
    print("fetch_balance initiated")
    username_cookie = request.cookies.get('username')
    
    dbrequest = myDB(money) 
    query = dbrequest.fetch_db(username_cookie)
    
    account_money = [] 
    print(query)
    
    for row in query:
        account_money.append({
            "userID": row[0],
            "username": row[1],
            "money": row[2]
        })
    return jsonify(account_money)


@app.route("/fetch_expenses", methods=['GET'])  # Get updates from the expenses database
def fetch_expenses():
    print("expense fetch initiated")
    username_cookie = request.cookies.get('username')

    dbrequest = myDB(expenses)
    query = dbrequest.fetch_db(username_cookie)
    
    print(query)
    expense_list = []
    
    for row in query: 
        expense_list.append({
            "username": row[0], 
            "transaction_ID": row[1],
            "transaction_name": row[2], 
            "amount": row[3]
        })
    return jsonify(expense_list)

@app.route("/fetch_schedule", methods=['GET'])
def fetch_schedule():
    print("fetching scheduled payments...")
    username_cookie = request.cookies.get('username')
    
    dbrequest = myDB(scheduledpayments)
    result = dbrequest.fetch_scheduledpayments(username_cookie)
    schedule_list = []

    for row in result:
        schedule_list.append({
            "schedule_name": row[1], 
            "schedule_amount": row[2], 
            "schedule_date":row[3]
        })

    print(schedule_list)
    return jsonify(schedule_list)

# ---------- TESTING ROUTE ----------

@app.route("/form_testing", methods=['POST'])  # Testing ground 
def form_testing(): 
    username_cookie = request.cookies.get('username')
    schedname = request.form.get('name')
    schedamount = request.form.get('amount')
    scheddate = request.form.get('duedate')

    print(username_cookie, schedname, schedamount, scheddate)
    return redirect('/schedule')



# =====================================
# MAIN EXECUTION
# =====================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
