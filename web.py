from flask import Flask, render_template, request, jsonify, redirect, make_response
import mysql.connector 
from waitress import serve  

# =====================================
# DATABASE CONFIGURATION
# ===================================== 

try: 
    mydb = mysql.connector.connect(
        host = "localhost", 
        user = "root",
        password = "root",
        database = "testbudgettracker"
    )
except mysql.connector.Error as error: 
    print(error)


dbcursor = mydb.cursor()





# =====================================
# DATABASE CLASS
# =====================================

class dbfunctions:
    def __init__(self, username):
        self.username = username
    
    def createuser(self):
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
        dbcursor.execute(f"SELECT * FROM users WHERE username = %s", (self.username, ))
        result = dbcursor.fetchone()
        print(result)
        if result == None:
            return "None"
        else: 
            return result
    
    def add_expenses(self,  userID, description, amount): 
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
        dbcursor.execute(f"SELECT userID FROM expenses WHERE transaction_id = %s", (int(transactionid), ))
        result = dbcursor.fetchone()
        if result == None: 
            return "invalid"
        else: 
            dbcursor.execute(f"DELETE FROM expenses WHERE transaction_id = %s", (int(transactionid), ))
            mydb.commit()
            return "deleted"
    def add_money(self, userID, username, balance):
        dbcursor.execute(f"INSERT INTO money (userID, username, balance) VALUES(%s,%s,%s)"(userID, username, balance))
        mydb.commit()
        #gonna work with this one later



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
        cookiemaker.set_cookie("username", query_result[1], max_age=60*60*24)
        cookiemaker.set_cookie("userID", str(query_result[0]), max_age = 60*60*24)
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



# =====================================
# PAGE FUNCTIONS
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
    pass





if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')

