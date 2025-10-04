
#WORK ON THE REGISTER PART

from flask import Flask, render_template, request, jsonify, redirect, make_response
import mysql.connector 
from waitress import serve 





#tables 
users = "users"
expenses = "expenses"
money = "money"


#database connection 
try:
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root", 
        password = "root",
        database =  "budgettracker"
    )
except mysql.connector.Error as error:
    print(error)


dbcursor = mydb.cursor() 


class myDB:
    def __init__(self, table):
        self.table = table 

    def fetch_username(self, info):
        dbcursor.execute(f"SELECT * FROM {self.table} WHERE username = \"{info}\"")
        results = dbcursor.fetchall()
        return results
    
    def fetch_db(self, username):
        dbcursor.execute(f"SELECT * FROM {self.table} WHERE username = \"{username}\"" ,)
        results = dbcursor.fetchall()
        return results

    
    def add_usernametoDB(self, username): #for register page
        dbcursor.execute(f"SELECT MAX(ID) FROM {users}")
        userid_checker = dbcursor.fetchone()[0]
        dbcursor.execute(f"SELECT MAX(ID) FROM {money}")
        moneyid_checker = dbcursor.fetchone()[0]
        if userid_checker == None and moneyid_checker == None: 
            userid = 1
            dbcursor.execute(f"INSERT INTO {users} (ID, username) VALUES (%s, %s)", (userid , username))
            dbcursor.execute(f"INSERT INTO {money} (ID, username, money) VALUES (%s,%s, 0)", (userid, username))
            mydb.commit()
            return f"success with userid = {userid} [add_username() if statement]"
        else:
            userid = userid_checker
            userid += 1 
            dbcursor.execute(f"INSERT INTO {users} (ID, username) VALUES (%s, %s)", (userid , username))
            dbcursor.execute(f"INSERT INTO {money} (ID, username, money) VALUES (%s,%s, 0)", (userid, username))
            mydb.commit()
            return f"success with userid = {userid} [add_username() else statement]"
        
    def add_expensetoDB(self, usernamecookie, input_expense_name, input_expense_amount): #add to expense database 
        #check the transaction_ID in the database 
        dbcursor.execute(f"SELECT MAX(transaction_ID) FROM {expenses}") 
        transactionID_count = dbcursor.fetchone()[0]
        print(transactionID_count)
        if transactionID_count == None:
            transactionID_count = 0
            dbcursor.execute(f"INSERT INTO {expenses} (username,transaction_ID, transaction_name, amount) VALUES (%s,%s,%s,%s)", (usernamecookie, transactionID_count, input_expense_name, input_expense_amount))
            mydb.commit()
        else:
            transactionID_count = transactionID_count + 1 
            dbcursor.execute(f"INSERT INTO {expenses} (username,transaction_ID, transaction_name, amount) VALUES (%s, %s, %s, %s)", (usernamecookie,transactionID_count,input_expense_name, input_expense_amount))
            mydb.commit()
    
    def remove_expensetoDB(self, transactionID):
        dbcursor.execute(f"DELETE FROM {self.table} WHERE transaction_ID = %s", (transactionID,)) 
        mydb.commit() 
        

            
            


        


#flask code 
app = Flask(__name__)


@app.route('/') #main page
def indexpage():
    return render_template('index.html')



@app.route('/loginpage') #login page
def loginpage():
    return render_template('login.html')

@app.route('/signuppage') #signup page 

def signuppage():
    return render_template('signup.html')



@app.route('/createuser', methods = ['POST']) #to create user in the database

def createuser(): 
    submittedusername = request.form.get("username")
    print("createuser() activated" + submittedusername)
    dbrequest = myDB(users)
    dbrequest.add_usernametoDB(submittedusername)
    if submittedusername: 
        cookiemaker = redirect("dashboard")
        cookiemaker.set_cookie("username", submittedusername, max_age = 60*60*24)
        return cookiemaker
    else: 
        return f"Shit happened. dont know what tho"




@app.route('/submitlogin', methods = ['POST']) #validation for login 

def validateLogin():
    submittedusername = request.form.get("username") 
    dbrequest = myDB(users)
    result = dbrequest.fetch_username(submittedusername)
    if result: 
        cookiemaker = redirect("/dashboard")
        cookiemaker.set_cookie("username", submittedusername, max_age=60*60*24)
        return cookiemaker
    else: 
        return f"No {submittedusername} in the database"
    

@app.route('/dashboard')  #dashboard

def render_dashboard():
    return render_template('dashboard.html')


@app.route('/addremove_expense', methods = ['POST']) #to add an expense 

def addremove_expense():
    expense_editopt = request.form.get("addremove")
    expense_description = request.form.get("expenseDescription")
    expense_amount = request.form.get("expenseAmount")
    expense_transactionID = request.form.get("transactionID")
    
    
    dbrequest = myDB(expenses)
    
    print(expense_editopt)
    print(expense_transactionID)
    username_cookie = request.cookies.get("username")
    
    
    if username_cookie:
        #add the expense_description and amount in the database
        if expense_editopt == "add":
            dbrequest.add_expensetoDB(username_cookie, expense_description, expense_amount)
            return redirect("/dashboard")
        else:
            dbrequest.remove_expensetoDB(expense_transactionID)
            return redirect("dashboard")
    else: 
        return "error occured"

@app.route("/fetch_balance", methods = ['GET']) #get updates from the money database

def fetch_balance(): 
    print("fetch_balance initiated")
    username_cookie = request.cookies.get('username')
    dbrequest = myDB(money) 
    query = dbrequest.fetch_db(username_cookie)
    account_money = [] 
    print(query)
    for row in query:
        account_money.append({
            "userID":row[0],
            "username":row[1],
            "money":row[2]
        })
    return jsonify(account_money)

@app.route("/fetch_expenses", methods = ['GET']) #get updates from the expenses database

def fetch_expenses():
    print("expense fetch initiated")
    username_cookie = request.cookies.get('username')

    dbrequest = myDB(expenses)
    query = dbrequest.fetch_db(username_cookie)
    print(query)
    expense_list = []
    for row in query: 
        expense_list.append({
            "username":row[0], 
            "transaction_ID": row[1],
            "transaction_name": row[2], 
            "amount":row[3]
        })
    return jsonify(expense_list)


if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')