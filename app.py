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

now = datetime.now() # current date NOT TIME since time must be serber local
#dateTime = now.strftime("%m/%d/%Y, %I:%M %p")
dateTime = now.strftime("%m/%d/%Y")

titleHeader = "66 West"

def get_db_connection():
    conn = sqlite3.connect('facilityDB.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_id(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM facilityDBInventory WHERE id = ?',(item_id,)).fetchone()
    conn.close()
    if item is None:
        abort(404)
    return item

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    conn = get_db_connection()
    facilityDBInventory = conn.execute('SELECT * FROM facilityDBInventory').fetchall()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    return render_template('shop.html', facilityDBInventory=facilityDBInventory,facilityDBCategory=facilityDBCategory)

##### Admin tools #####

@app.route('/admin')
def admin():
    conn = get_db_connection()
    facilityDBInventory = conn.execute('SELECT * FROM facilityDBInventory').fetchall()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    return render_template('admin.html', facilityDBInventory=facilityDBInventory,facilityDBCategory=facilityDBCategory)

# Create
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        newCategory = request.form['category']
        newItem = request.form['item']
        newHave = request.form['have']
        newNeed = request.form['goal']
        conn = get_db_connection()
        conn.execute('INSERT INTO facilityDBInventory (category, item, have, goal) VALUES (?, ?, ?, ?)',(newCategory, newItem, newHave, newNeed))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    else:
        conn = get_db_connection()
        facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
        conn.close()
        return render_template('create.html',facilityDBCategory=facilityDBCategory)

# Add New Category
@app.route('/add_category', methods=('GET', 'POST'))
def add_category():
    if request.method == 'POST':
        newCategory = request.form['category']
        conn = get_db_connection()
        conn.execute('INSERT INTO facilityDBCategories (category) VALUES (?)',(newCategory,))
        conn.commit()
        conn.close()
        return redirect(url_for('create'))

    elif request.method == 'GET':
        conn = get_db_connection()
        facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
        conn.close()
        return render_template('add_category.html',facilityDBCategory=facilityDBCategory)

@app.route('/categories')
def categories():
    conn = get_db_connection()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    return render_template('categories.html', facilityDBCategory=facilityDBCategory)

@app.route('/delete_empty_category', methods=('GET', 'POST'))
def delete_empty_category():
    if request.method == 'POST':
        toDelete = (request.form.getlist('cbox[]'))
        toDelete = [category for category in zip(*[iter(toDelete)])]

        conn = get_db_connection()
        conn.executemany('DELETE FROM facilityDBCategories WHERE category = ?', (toDelete))
        conn.commit()

        checkInventory = conn.execute('SELECT category FROM facilityDBInventory').fetchall()
        checkCategories = conn.execute('SELECT category FROM facilityDBCategories').fetchall()
        conn.close()

        deduplicatedCheckInventory = list(set(checkInventory))
        emptyCategoryList = list(set(checkCategories).difference(deduplicatedCheckInventory))

        flash('"{}" successfully deleted!'.format(toDelete),'info')

        return render_template('delete_empty_category.html', emptyCategoryList=emptyCategoryList)
    else:
        conn = get_db_connection()
        checkInventory = conn.execute('SELECT category FROM facilityDBInventory').fetchall()
        checkCategories = conn.execute('SELECT category FROM facilityDBCategories').fetchall()
        conn.close()

        deduplicatedCheckInventory = list(set(checkInventory))
        emptyCategoryList = list(set(checkCategories).difference(deduplicatedCheckInventory))

        return render_template('delete_empty_category.html', emptyCategoryList=emptyCategoryList)

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    facilityDBInventory = conn.execute('SELECT * FROM facilityDBInventory').fetchall()
    conn.close()
    return render_template('inventory.html', facilityDBInventory=facilityDBInventory)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    itemID = get_id(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM facilityDBInventory WHERE id=? ',(id,))
    conn.commit()
    conn.close()
    flash('"{}" successfully deleted!'.format(itemID['item']),'info')
    return redirect(url_for('admin'))

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    item = get_id(id)
    conn = get_db_connection()
    facilityDBCategory = conn.execute('SELECT * FROM facilityDBCategories').fetchall()
    conn.close()
    if request.method == 'POST':
        item = request.form['item']
        category = request.form['category']
        have = request.form['have']
        goal = request.form['goal']
        conn = get_db_connection()
        conn.execute('UPDATE facilityDBInventory SET item = ?, category = ?, have = ?, goal = ? WHERE id = ?',(item, category, have, goal, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    return render_template('edit.html', item=item, facilityDBCategory=facilityDBCategory)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=('POST',))
def authenticate():
    if request.method == 'POST':
        uName = request.form['username']
        pWord = request.form['password']
        pWord = pWord.encode('utf-8')

        conn = get_db_connection()
        #cur.execute('SELECT * FROM facilityDBUsers WHERE userName = ?',(uName,))
        facilityDBUsers = conn.execute('SELECT * FROM facilityDBUsers WHERE userName = ?',(uName,))
        userDBRows = facilityDBUsers.fetchone()
        #conn = get_db_connection()
        conn.close()

        if userDBRows is not None:
            pWordCheck = userDBRows[5]
            pWordCheck = pWordCheck.encode('utf-8')
            pWordTest = bcrypt.checkpw(pWord,pWordCheck)

        elif userDBRows is None:
             flash('Login failed. This user name does not exits')
             return render_template('login.html')
        elif pWordTest == False:
             flash('login failed. This password is incorrect')
             return render_template('login.html')

        session['logged_in'] = True
        flash('You are logged in. Use the extended menu to see your options.','info')
        return render_template('index.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('login.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    msg = ''
    if request.method == 'POST': #and 'firstName' in request.form and 'lastName' in request.form and 'eMail' in request.form and 'userName' in request.form and 'passWord' in request.form:
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        eMail = request.form['eMail']
        userName = request.form['userName']
        passWord = request.form['passWord']

        # converting password to array of bytes
        passWord = passWord.encode('utf-8')

        # generating the salt
        salt = bcrypt.gensalt()

        # Hashing the password
        passWord = bcrypt.hashpw(passWord, salt)


        conn = get_db_connection()
        account = conn.execute('SELECT * FROM facilityDBUsers WHERE username = ?', (userName,)).fetchone()
        if account:
            msg = 'User name not available. Please chose another.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', eMail):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', userName):
            msg = 'Username must contain only letters and numbers!'
        elif not userName or not passWord or not eMail:
            msg = 'Please fill out the form!'
        else:
            conn.execute('INSERT INTO facilityDBUsers VALUES (NULL, ?, ?, ?, ?, ?)', (firstName, lastName, eMail, userName, passWord))
            conn.commit()
            conn.close()
            msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)

@app.route('/check_users')
def check_users():
    conn = get_db_connection()
    facilityDBUsers = conn.execute('SELECT * FROM facilityDBUsers').fetchall()
    conn.close()
    return render_template('check_users.html', facilityDBUsers=facilityDBUsers)

##### starting password reset functionality

##### user requests reset
@app.route('/reset_request')
def reset_request():
    return render_template('reset_request.html')

##### response to request

########## testing email ##########
# @app.route("/foo")
# def foo():
#    sendTo = 'dgrc@crowswood.com'
#    msg = Message('Test from Local', sender = 'inventory.response@gmail.com', recipients = [sendTo])
#    msg.body = "Test running properly from VSCode"
#    mail.send(msg)
#    return "Sent"
########## testing email ##########


@app.route('/reset_response', methods=('GET', 'POST'))
def reset_response():
    msg = ''
    if request.method == 'POST':
        eMail = request.form['eMail']

        # search db for username
        conn = get_db_connection()

        emailExists = conn.execute('SELECT eMail FROM facilityDBUsers WHERE eMail = ?',(eMail,)).fetchone()
        conn.close()
        if emailExists is not None:
            #return "succeed"
            msg = 'We found your email address in our records. We will send an email to that address with password recovery instructions'
            randomLettersDigits = string.ascii_letters + string.digits
            resetCode = ''.join(random.choice(randomLettersDigits) for index in range(7))
         	#update database
            resetStatus = 1
            conn = get_db_connection()
            conn.execute('UPDATE facilityDBUsers SET resetStatus = ?, resetCode = ? WHERE eMail = ?',(resetStatus, resetCode, eMail))
            conn.commit()
            conn.close()
        	
         	#compose email
             
            sendTo = str(emailExists[0])
            # msg = Message('Reset Request', sender = 'inventory.response@gmail.com', recipients = [sendTo])
            # msg.body = "Your reset code is "+resetCode+" Use this code at web address to reset"
            # mail.send(msg)
            #return sendTo
            msg = Message('Responding to password reset request', sender = 'inventory.response@gmail.com', recipients = [sendTo])
            msg.body = "Your reset code is "+resetCode+" Use this code at web address to reset"
            #msg.html="<html><body><p>This is a test email sent with the <a href=\\\"https://foo.bar\\\">foo bar</a> SMTP server!</p></body></html>"
            argumentsToRender = [eMail, resetCode]
            msg.html = render_template('emailText.html', argumentsToRender = argumentsToRender)
            mail.send(msg)
            return render_template('reset_response.html')
        else:
            #return "fail"
            msg = 'This email address is not in our records. You may either try again or contact your admin for assistance'
            return render_template('reset_request.html', msg=msg)
##### interim end password reset functionality

@app.route("/pdf_list") #don't want this to be homepage
def pdf_list():
    # Run the inventory query
    conn = get_db_connection()
    facilityDBInventory = conn.execute('SELECT category, item, goal, have FROM facilityDBInventory').fetchall()
    conn.close()

#start with header row for FPDF2 table maker
    resultList = [['category','item','needed']]

# calculate needed
    calculatedList = []
    for row in facilityDBInventory:
        newRow = [row[0], row[1], row[2] - row[3]]
        calculatedList.append(newRow)

#use list comprehension for converting all elements to strings
# then append to result list
    for row in calculatedList:
        newRow = [str(x) for x in row]
        resultList.append(newRow)

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

@app.route("/pdf_inventory") #don't want this to be homepage
def pdf_inventory():
    # Run the inventory query
    conn = get_db_connection()
    facilityDBInventory = conn.execute('SELECT category, item, goal, have FROM facilityDBInventory').fetchall()
    conn.close()

#start with header row for FPDF2 table maker
    resultList = [['category','item', 'goal', 'needed']]

# calculate needed
    calculatedList = []
    for row in facilityDBInventory:
        newRow = [row[0], row[1], row[2], row[2] - row[3]]
        calculatedList.append(newRow)

#use list comprehension for converting all elements to strings
# then append to result list
    for row in calculatedList:
        newRow = [str(x) for x in row]
        resultList.append(newRow)

    # Instantiation of inherited class
    pdf = PDF()
    pdf.set_font("helvetica", size=10)

    # Basic table:
    pdf.add_page()

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    headings_style = FontFace(emphasis="BOLD", color=0, fill_color=(255, 255, 255))

    pdf.cell(0,10, 'Current Inventory', border=False, align="C", ln=True)

    with pdf.table(
        borders_layout="NO_HORIZONTAL_LINES",
        cell_fill_color=(211, 211, 211),
        cell_fill_mode=TableCellFillMode.ROWS,
        col_widths=(42, 39, 35, 44),
        headings_style=headings_style,
        line_height=6,
        text_align=("LEFT", "CENTER", "RIGHT", "RIGHT"),
        width=160,
    ) as table:
        for data_row in resultList:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    response = make_response(bytes(pdf.output()))
    response.headers["Content-Type"] = "application/pdf"
    return response
