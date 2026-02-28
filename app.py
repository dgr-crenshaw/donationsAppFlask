import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session, make_response
from werkzeug.exceptions import abort
import re
import bcrypt

import string
import random

from fpdf import FPDF
from fpdf.fonts import FontFace
from fpdf.enums import TableCellFillMode

from datetime import datetime

from flask_mail import Mail, Message

import os
from flask import send_from_directory

now = datetime.now() # current date NOT TIME since time must be server local
#dateTime = now.strftime("%m/%d/%Y, %I:%M %p")
dateTime = now.strftime("%m/%d/%Y")

titleHeader = "66 West"

def getDBConnection():
    conn = sqlite3.connect('/home/dgrCrenshaw/donationsAppFlask/facilityDB.db')
    conn.row_factory = sqlite3.Row
    return conn

def getItemID(itemID):
    conn = getDBConnection()
    item = conn.execute('SELECT * FROM facilityDBInventory WHERE id = ?',(itemID,)).fetchone()
    conn.close()
    if item is None:
        abort(404)
    return item

def getUserID(userID):
    conn = getDBConnection()
    user = conn.execute('SELECT * FROM facilityDBUSERS WHERE id = ?',(userID,)).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user

def sendEmail(eMailAddress, eMailSender, eMailTextSource, eMailSubjectLine, resetCode):
    msg = Message(eMailSubjectLine, sender = eMailSender, recipients = [eMailAddress])
    msg.html = render_template(eMailTextSource, argumentsToRender = [eMailAddress, resetCode])
    mail.send(msg)

class validatePassword:

    def __init__(self, passWord):
        self.passWord = passWord

    def testPasswordLength(self):
        testLength = len(self.passWord)
        if testLength < 8:
            return True
        else:
            return False

    def testPasswordUpperCase(self):
        testUpper = re.match(r'^(?=.*[A-Z]).*$', self.passWord)
        if not testUpper:
            return True
        else:
            return False

    def testPasswordNumeric(self):
        testNumeric = re.match(r'^(?=.*[0-9]).*$', self.passWord)
        if not testNumeric:
            return True
        else:
            return False

    def testPasswordSpecial(self):
        testSpecial = re.match(r'^(?=.*[-+_!@#$%^&*.,?]).*$', self.passWord)
        if not testSpecial:
            return True
        else:
            return False

### new instance to work with headers and footers
class PDF(FPDF):
    def header(self):
        # Rendering logo:
        # self.image("../docs/fpdf2-logo.png", 10, 8, 33)
        # Setting font: helvetica bold 15
        self.set_font("helvetica", style="B", size=15)
        # Printing title:
        self.cell(0,5, titleHeader, border=False, align="C", ln=True)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", style="I", size=8)
        # Printing time stamp
        self.cell(0, 10, "Current as of " + dateTime, border=False, align="C", ln=True)
        # Printing page number:
        self.cell(0, 0, f"Page {self.page_no()} of {{nb}}", align="C")

### main app -- decorators for routes
app = Flask(__name__)

#configure email service using a gmail account
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'inventory.response@gmail.com'
app.config['MAIL_PASSWORD'] = 'kmhb wfuf gfhb gqbr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.config['SECRET_KEY'] = '917190101'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico')

@app.route('/')
def index():
    session['logged in'] = True
    return render_template('index.html', session=session)

@app.route('/shop')
def shop():
    conn = getDBConnection()
    facilityDBInventory = conn.execute('SELECT * FROM facilityDBInventory').fetchall()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    return render_template('shop.html', facilityDBInventory=facilityDBInventory,facilityDBCategory=facilityDBCategory)

##### Admin tools #####

@app.route('/admin')
def admin():
    conn = getDBConnection()
    facilityDBInventory = conn.execute('SELECT * FROM facilityDBInventory').fetchall()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    return render_template('admin.html', facilityDBInventory=facilityDBInventory,facilityDBCategory=facilityDBCategory)

@app.route('/userAdmin')
def userAdmin():
    conn = getDBConnection()
    facilityDBUsers = conn.execute('SELECT * FROM facilityDBUsers').fetchall()
    conn.close()
    return render_template('userAdmin.html', facilityDBUsers=facilityDBUsers)

# Create
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        newCategory = request.form['category']
        newItem = request.form['item']
        newHave = request.form['have']
        newNeed = request.form['goal']
        conn = getDBConnection()
        conn.execute('INSERT INTO facilityDBInventory (category, item, have, goal) VALUES (?, ?, ?, ?)',(newCategory, newItem, newHave, newNeed))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    else:
        conn = getDBConnection()
        facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
        conn.close()
        return render_template('create.html',facilityDBCategory=facilityDBCategory)

# Add New Category
@app.route('/add_category', methods=('GET', 'POST'))
def add_category():
    if request.method == 'POST':
        newCategory = request.form['category']
        conn = getDBConnection()
        conn.execute('INSERT INTO facilityDBCategories (category) VALUES (?)',(newCategory,))
        conn.commit()
        conn.close()
        return redirect(url_for('create'))

    elif request.method == 'GET':
        conn = getDBConnection()
        facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
        conn.close()
        return render_template('add_category.html',facilityDBCategory=facilityDBCategory)

@app.route('/categories')
def categories():
    conn = getDBConnection()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    return render_template('categories.html', facilityDBCategory=facilityDBCategory)

@app.route('/deleteEmptyCategory', methods=('GET', 'POST'))
def deleteEmptyCategory():
    if request.method == 'POST':
        toDelete = (request.form.getlist('cbox[]'))
        toDelete = [category for category in zip(*[iter(toDelete)])]

        conn = getDBConnection()
        conn.executemany('DELETE FROM facilityDBCategories WHERE category = ?', (toDelete))
        conn.commit()

        checkInventory = conn.execute('SELECT category FROM facilityDBInventory').fetchall()
        checkCategories = conn.execute('SELECT category FROM facilityDBCategories').fetchall()
        conn.close()

        deduplicatedCheckInventory = list(set(checkInventory))
        emptyCategoryList = list(set(checkCategories).difference(deduplicatedCheckInventory))

        flash('"{}" successfully deleted!'.format(toDelete),'info')

        return render_template('deleteEmptyCategory.html', emptyCategoryList=emptyCategoryList)
    else:
        conn = getDBConnection()
        checkInventory = conn.execute('SELECT category FROM facilityDBInventory').fetchall()
        checkCategories = conn.execute('SELECT category FROM facilityDBCategories').fetchall()
        conn.close()

        deduplicatedCheckInventory = list(set(checkInventory))
        emptyCategoryList = list(set(checkCategories).difference(deduplicatedCheckInventory))

        return render_template('deleteEmptyCategory.html', emptyCategoryList=emptyCategoryList)

@app.route('/inventory')
def inventory():
    conn = getDBConnection()
    facilityDBInventory = conn.execute('SELECT * FROM facilityDBInventory').fetchall()
    conn.close()
    return render_template('inventory.html', facilityDBInventory=facilityDBInventory)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    itemID = getItemID(id)
    conn = getDBConnection()
    conn.execute('DELETE FROM facilityDBInventory WHERE id=? ',(id,))
    conn.commit()
    conn.close()
    flash('"{}" successfully deleted!'.format(itemID['item']),'info')
    return redirect(url_for('admin'))

@app.route('/<int:id>/deleteUser', methods=('POST',))
def deleteUser(id):
    userID = getUserID(id)
    conn = getDBConnection()
    conn.execute('DELETE FROM facilityDBUsers WHERE id=? ',(id,))
    conn.commit()
    conn.close()
    flash('"{}" successfully deleted!'.format(userID['userName']),'info')
    return redirect(url_for('userAdmin'))

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    item = getItemID(id)
    conn = getDBConnection()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    if request.method == 'POST':
        item = request.form['item']
        category = request.form['category']
        have = request.form['have']
        goal = request.form['goal']
        conn = getDBConnection()
        conn.execute('UPDATE facilityDBInventory SET item = ?, category = ?, have = ?, goal = ? WHERE id = ?',(item, category, have, goal, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    return render_template('edit.html', item=item, facilityDBCategory=facilityDBCategory)

@app.route('/<int:id>/editUser', methods=('GET', 'POST'))
def editUser(id):
    user = getUserID(id)
    #conn = getDBConnection()
    #facilityDBUser = conn.execute('SELECT * FROM facilityDBUsers').fetchall()
    #conn.close()
    if request.method == 'POST':
        lastName = request.form['lastName']
        firstName = request.form['firstName']
        eMail = request.form['eMail']
        userName = request.form['userName']
        conn = getDBConnection()
        conn.execute('UPDATE facilityDBUsers SET lastName = ?, firstName = ?, eMail = ?, userName = ? WHERE id = ?',(lastName, firstName, eMail, userName, id))
        conn.commit()
        conn.close()
        return redirect(url_for('userAdmin'))
    return render_template('editUser.html', user=user)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=('POST',))
def authenticate():
    if request.method == 'POST':
        uName = request.form['username']
        pWord = request.form['password']
        pWord = pWord.encode('utf-8')

        conn = getDBConnection()
        #cur.execute('SELECT * FROM facilityDBUsers WHERE userName = ?',(uName,))
        facilityDBUsers = conn.execute('SELECT * FROM facilityDBUsers WHERE userName = ?',(uName,))
        userDBRows = facilityDBUsers.fetchone()
        #conn = getDBConnection()
        conn.close()

        if userDBRows is not None:
            permissions = userDBRows[5]
            pWordCheck = userDBRows[6]
            pWordCheck = pWordCheck.encode('utf-8')
            pWordTest = bcrypt.checkpw(pWord,pWordCheck)

        elif userDBRows is None:
             flash('Login failed. This user name does not exist.','warning')
             return render_template('login.html')
        elif pWordTest == False:
             flash('login failed. This password is incorrect','warning')
             return render_template('login.html')

        session['logged_in'] = True
        session['permissions'] = permissions
        flash('You are logged in. Use the extended menu to see your options.','info')
        return render_template('index.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['permissions'] = 'N'
    return render_template('index.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        eMail = request.form['eMail']
        userName = request.form['userName']
        permissions = request.form['permissions']
        #passWord = request.form['passWord']

        #update values for entry to return
        contentDictionary = {
        'attribute': 'value',
        'attributeValueFirstName': firstName,
        'attributeValueLastName': lastName,
        'attributeValueEmailAddress': eMail,
        'attributeValueUserName': userName,
        'attributeValuePermissions': permissions,
        #'attributeValuePassWord': passWord
        }

        # converting password to array of bytes
        #passWordHash = passWord.encode('utf-8')

        # generating the salt
        #salt = bcrypt.gensalt()

        # Hashing the password
        #passWordHash = bcrypt.hashpw(passWordHash, salt)

        #convert it to a string for storage
        #passWordHash = str(passWordHash)
        #chop off first two characters
        #passWordHash = passWordHash[2:]

        #begin entry error tests

        entryErrors = False #initialize

        #testPasswordTests = validatePassword(passWord)

        # test for length
        #if testPasswordTests.testPasswordLength():
        #    flash('Password must be at least 8 characters!', 'warning')
        #    entryErrors = True

        # test for upper case
        #if testPasswordTests.testPasswordUpperCase():
        #    flash('Password must have at least one upper case character.','warning')
        #    entryErrors = True

        # test for digits
        #if testPasswordTests.testPasswordNumeric():
        #    flash('Password must have at least one number.','warning')
        #    entryErrors = True

        # test for special chars
        #if testPasswordTests.testPasswordSpecial():
        #    flash('Password must have at least one of the following special characters - + _ ! @ # $ % ^ & * . , ?','warning')
        #    entryErrors = True

        conn = getDBConnection()
        account = conn.execute('SELECT * FROM facilityDBUsers WHERE username = ?', (userName,)).fetchone()

        #test if user name exists
        if account:
            flash('This user name not available. Please chose another.','warning')
            entryErrors = True

        #test if email proper form
        if not re.match(r'[^@]+@[^@]+\.[^@]+', eMail):
            flash('This is not a valid format for an email address!','warning')
            entryErrors = True

        #test if user name proper form
        if not re.match(r'[A-Za-z0-9]+', userName):
            flash('The username must contain only letters and numbers. Please enter a different user name.','warning')
            entryErrors = True

        #test if requred field not complete
        if not userName or not eMail:
            flash('Please fill out the required fields on the form!','warning')
            entryErrors = True

        if entryErrors == True:
            return render_template('register.html', contentDictionary=contentDictionary)

        else:
            #create a code
            randomLettersDigits = string.ascii_letters + string.digits
            resetCode = ''.join(random.choice(randomLettersDigits) for index in range(7))
         	#update database
            resetStatus = 1

            conn.execute('INSERT INTO facilityDBUsers VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)', (firstName, lastName, eMail, userName, permissions,'$2a$12$6fdvh9u0WVr3hWRLh5dsSeYWfgbqKQc8Bg9nfrieMJCi4K72y4vAy', resetStatus, resetCode))
            conn.commit()
            conn.close()

         	#compose email

            #####
            # def sendEmail(eMailAddress, eMailSender, eMailTextSource, eMailSubjectLine, resetCode):
            #     msg = Message(eMailSubjectLine, sender = eMailSender, recipients = eMailAddress)
            #     msg.html = render_template(eMailTextSource, argumentsToRender = [eMailAddress, resetCode])
            #     mail.send(msg)
            #####

            #####
            eMailAddress = eMail
            eMailSender = 'inventory.response@gmail.com'
            eMailTextSource = 'emailCreationText.html'
            eMailSubjectLine = 'Responding to password creation request'

            sendEmail(eMailAddress, eMailSender, eMailTextSource, eMailSubjectLine, resetCode)
            #####


            # msg = Message('Responding to password creation or reset request', sender = 'inventory.response@gmail.com', recipients = [sendTo])
            # argumentsToRender = [eMail, resetCode]
            # msg.html = render_template('emailText.html', argumentsToRender = argumentsToRender)
            # mail.send(msg)

            flash('You have successfully registered {eMail}!','success')
            return render_template('register.html',contentDictionary=contentDictionary)

    elif request.method == 'GET':
        contentDictionary = {
        'attribute': 'placeholder',
        'attributeValueFirstName': 'First Name',
        'attributeValueLastName': 'Last Name',
        'attributeValueEmailAddress': 'Email Address',
        'attributeValueUserName': 'User Name',
        'attributeValuePermissions': 'Permissions',
        #'attributeValuePassWord': 'Password'
    }
        return render_template('register.html', contentDictionary = contentDictionary)

@app.route('/checkUsers')
def checkUsers():
    conn = getDBConnection()
    facilityDBUsers = conn.execute('SELECT * FROM facilityDBUsers').fetchall()
    conn.close()
    return render_template('checkUsers.html', facilityDBUsers=facilityDBUsers)

##### new user set password
@app.route('/newPassword', methods=('GET', 'POST'))
def newPassword():
    if request.method == 'POST':
        eMail = request.form['eMail']
        userName = request.form['userName']

        # search db for username
        conn = getDBConnection()

        emailExists = conn.execute('SELECT eMail FROM facilityDBUsers WHERE eMail = ? AND userName = ?',(eMail,userName)).fetchone()
        conn.close()
        if emailExists is not None:
            flash('We found your email address in our records. We will send an email to that address with password recovery instructions.','success')
            randomLettersDigits = string.ascii_letters + string.digits
            resetCode = ''.join(random.choice(randomLettersDigits) for index in range(7))
         	#update database
            resetStatus = 1
            conn = getDBConnection()
            conn.execute('UPDATE facilityDBUsers SET resetStatus = ?, resetCode = ? WHERE eMail = ?',(resetStatus, resetCode, eMail))
            conn.commit()
            conn.close()

         	#compose email

            sendTo = str(emailExists[0])
            msg = Message('Responding to password reset request', sender = 'inventory.response@gmail.com', recipients = [sendTo])
            argumentsToRender = [eMail, resetCode]
            msg.html = render_template('emailText.html', argumentsToRender = argumentsToRender)
            mail.send(msg)
            return render_template('resetPasswordResponse.html')
        else:
            flash('This email address is not in our records. You may either try again or contact your admin for assistance.','warning')
            return render_template('resetRequest.html')


##### user requests reset
@app.route('/resetRequest')
def resetRequest():
    return render_template('resetRequest.html')

##### response to request

@app.route('/resetResponse', methods=('GET', 'POST'))
def resetResponse():
    if request.method == 'POST':
        eMail = request.form['eMail']
        userName = request.form['userName']

        # search db for username
        conn = getDBConnection()

        emailExists = conn.execute('SELECT eMail FROM facilityDBUsers WHERE eMail = ? AND userName = ?',(eMail,userName)).fetchone()
        conn.close()
        if emailExists is not None:
            flash('We found your email address in our records. We will send an email to that address with password recovery instructions.','success')
            randomLettersDigits = string.ascii_letters + string.digits
            resetCode = ''.join(random.choice(randomLettersDigits) for index in range(7))
         	#update database
            resetStatus = 1
            conn = getDBConnection()
            conn.execute('UPDATE facilityDBUsers SET resetStatus = ?, resetCode = ? WHERE eMail = ?',(resetStatus, resetCode, eMail))
            conn.commit()
            conn.close()

         	#compose email

            sendTo = str(emailExists[0])

            # msg = Message('Responding to password reset request', sender = 'inventory.response@gmail.com', recipients = [sendTo])
            # argumentsToRender = [eMail, resetCode]
            # msg.html = render_template('emailText.html', argumentsToRender = argumentsToRender)
            # mail.send(msg)

            sendEmail(eMailAddress, eMailSender, eMailTextSource, eMailSubjectLine, resetCode)

            return render_template('resetPasswordResponse.html')
        else:
            flash('This email address is not in our records. You may either try again or contact your admin for assistance.','warning')
            return render_template('resetRequest.html')
    else:
        return render_template('resetPasswordResponse.html')

@app.route('/resetValidate', methods=('GET', 'POST'))
def resetValidate():
        if request.method == 'POST':
            resetCode = request.form['resetCode']
            newPassWord = request.form['newPassWord']

            entryErrors = False #initialize

            testNewPasswordTests = validatePassword(newPassWord)

            # test for length
            if testNewPasswordTests.testPasswordLength():
                flash('Password must be at least 8 characters!', 'warning')
                entryErrors = True

            # test for upper case
            if testNewPasswordTests.testPasswordUpperCase():
                flash('Password must have at least one upper case character.','warning')
                entryErrors = True

            # test for digits
            if testNewPasswordTests.testPasswordNumeric():
                flash('Password must have at least one number.','warning')
                entryErrors = True

            # test for special chars
            if testNewPasswordTests.testPasswordSpecial():
                flash('Password must have at least one of the following special characters - + _ ! @ # $ % ^ & * . , ?','warning')
                entryErrors = True

             #return render_template('resetPasswordResponse.html')
            if entryErrors == True:
                return render_template('resetPasswordResponse.html',)

            else:
                #hit database for resetCode validity
                conn = getDBConnection()
                resetCodeDB = conn.execute('SELECT resetCode FROM facilityDBUsers WHERE resetCode = ?',(resetCode,)).fetchone()
                conn.close()
                if resetCodeDB is not None:
                    #hash the password
                    # converting password to array of bytes
                    newPassWord = newPassWord.encode('utf-8')
                    # generating the salt
                    salt = bcrypt.gensalt()
                    # Hashing the password
                    newPassWord = bcrypt.hashpw(newPassWord, salt)
                    #convert it to a string for storage
                    newPassWord = str(newPassWord)
                    #chop off first two characters
                    newPassWord = newPassWord[2:]

                    #update the resetStatus to 0
                    #update the resetCode to none
                    conn = getDBConnection()
                    conn.execute('UPDATE facilityDBUsers SET passWord = ?, resetStatus = ?, resetCode = ? WHERE resetCode = ?',(newPassWord, '0', 'none', resetCode))
                    conn.commit()
                    conn.close()
                    flash('Your password has been reset. You can now log into the website','success')
                    return render_template('login.html')
                else:
                    flash('Your reset request failed. Please be sure you are using the right reset code.','danger')
                    return render_template('resetPasswordResponse.html')

@app.route("/pdfList")
def pdfList():
    # Run the inventory query
    conn = getDBConnection()
    facilityDBInventory = conn.execute('SELECT category, item, goal, have FROM facilityDBInventory').fetchall()
    conn.close()

#start with header row for FPDF2 table maker
    resultList = [['category','item','needed']]

# calculate needed
    calculatedList = []
    for rowInventory in facilityDBInventory:
        numberNeeded = rowInventory[2] - rowInventory[3]
        if numberNeeded < 0:
            numberNeeded = 0
        newInventoryRow = [rowInventory[0], rowInventory[1], numberNeeded]
        calculatedList.append(newInventoryRow)

#use list comprehension for converting all elements to strings
# then append to result list
    for rowEntry in calculatedList:
        newEntryRow = [str(x) for x in rowEntry]
        resultList.append(newEntryRow)

    # Instantiation of inherited class
    pdf = PDF()
    pdf.set_font("helvetica", size=10)

    # Basic table:
    pdf.add_page()

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    headings_style = FontFace(emphasis="BOLD", color=0, fill_color=(255, 255, 255))

    pdf.cell(0,10, 'Shopping List', border=False, align="C", ln=True)

    with pdf.table(
        borders_layout="NO_HORIZONTAL_LINES",
        cell_fill_color=(211, 211, 211),
        cell_fill_mode=TableCellFillMode.ROWS,
        col_widths=(42, 39, 35),
        headings_style=headings_style,
        line_height=6,
        text_align=("LEFT", "CENTER", "RIGHT"),
        width=160,
    ) as table:
        for data_row in resultList:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    response = make_response(bytes(pdf.output()))
    response.headers["Content-Type"] = "application/pdf"
    return response