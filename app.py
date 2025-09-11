
#WORK ON THE REGISTER PART

from flask import Flask, render_template, request, jsonify, redirect
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

    def fetch(self, info):
        dbcursor.execute(f"SELECT * FROM {self.table} WHERE username = \"{info}\"")
        results = dbcursor.fetchall()
        return results
    
    def add_username(self, username): #for register page
        dbcursor.execute(f"SELECT ID FROM {users}")
        userid_checker = dbcursor.fetchone()
        dbcursor.execute(f"SELECT ID FROM {money}")
        moneyid_checker = dbcursor.fetchone()
        if userid_checker == None and moneyid_checker == None: 
            userid = 1
            dbcursor.execute(f"INSERT INTO {users} (ID, username) VALUES ({userid},{username})")
            dbcursor.execute(f"INSERT INTO {money} (ID, username, money) VALUES ({userid},{username}, 0)")
            return "success"
        else:
            userid = userid_checker
            userid += 1 
            dbcursor.execute(f"INSERT INTO {users} (ID, username) VALUES ({userid}, {username})")
            dbcursor.execute(f"INSERT INTO {money} (ID, username) VALUES ({userid}, {username})")
            return f"success with userid = {userid}"

            
            


        


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



@app.route('/createuser')

def createuser(): 
    submittedusername = request.form.get("username")
    dbrequest = myDB(users)
    result = dbrequest.add_username(submittedusername)
    return result 




@app.route('/submitlogin', methods = ['POST']) #validation for login 

def validateLogin():
    submittedusername = request.form.get("username") 
    dbrequest = myDB(users)
    result = dbrequest.fetch(submittedusername)
    if result: 
        return redirect("/dashboard")
    else: 
        return f"No {submittedusername} in the database"


@app.route('/dashboard')  #dashboard

def render_dashboard():
    return render_template('dashboard.html')


@app.route('/fetchdata')

def fetchdatabase():
    pass



if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')