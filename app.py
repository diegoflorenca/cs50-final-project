from flask import Flask, request, render_template, redirect, session, flash
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import sqlite3 as sql
import hashlib
from datetime import datetime

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static\\uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'dYfgd91s5xH6vc7f8ykj6E5465-HvT'

DATABASE = './db/data.db'

# check the allowed files - Flask documentation example


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        isSchool = request.form.get('isSchool')

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()

        # Check if it's a school or user login
        if(isSchool):
            print('This is a school login!')
            cursor.execute(
                "SELECT * FROM `schools` WHERE email = ?", [email])
            redirectPage = '/school_page'
        else:
            cursor.execute("SELECT * FROM `users` WHERE email = ?", [email])
            redirectPage = '/schools'

        user = cursor.fetchone()
        if not user:
            flash('User not found.')
            return redirect('/login')

        # Need to Hash Password
        if user['password'] != password:
            flash('Password incorect, please try again.')
            return redirect('/login')
        session['userId'] = user['id']
        return redirect(redirectPage)
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        file = request.files['file']

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()

        # Check if user already existis
        cursor.execute("SELECT email FROM `users` WHERE email=?", [email])
        hasUser = cursor.fetchone()

        if hasUser:
            flash('User already registred.')
            return redirect('/register')

        # Check if the type of file is allowed
        if file and allowed_file(file.filename):
            # Take the file name
            filename = secure_filename(file.filename)
            # Save the file extension
            extension = filename.rsplit('.', 1)[1]
            # Sum the current date to the file name
            filename = filename.rsplit('.', 1)[0] + str(datetime.now().time())
            # Hash the filename and reinsert the extension
            h = hashlib.sha256()
            h.update(filename.encode('utf-8'))
            newFilename = h.hexdigest() + '.' + extension
            # Copy the file to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newFilename))
        else:
            flash('Error: Image not uploaded')
            return redirect('/register')

        cursor.execute("INSERT INTO `users` (name, email, password, photo)VALUES (?,?,?,?)", (
            name, email, password, newFilename))
        con.commit()

        flash('New user added successfully, login to continue!')
        return redirect('/login')
    else:
        return render_template('add_user.html')


@app.route('/schools')
def schools():
    if 'userId' in session:
        con = sql.connect(DATABASE)
        con.row_factory = sql.Row

        cursor = con.cursor()
        cursor.execute('SELECT * FROM schools')

        schools = cursor.fetchall()
        return render_template('schools.html', schools=schools)
    else:
        return redirect('/login')


@app.route('/school/<schoolId>')
def ong(schoolId):
    if 'userId' in session:
        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `schools` WHERE id=?', [schoolId])
        school = cursor.fetchone()

        # Show the info about the itens based on the type of itens needed by the school
        cursor.execute(
            'SELECT * FROM school_items INNER JOIN items ON items.id = school_items.item_id WHERE school_items.school_id=?', [schoolId])
        items = cursor.fetchall()
        return render_template('school.html', school=school, items=items)
    else:
        return redirect('/login')


@app.route('/donate/<schoolId>', methods=['POST', 'GET'])
def donate(schoolId):
    if 'userId' in session:
        if request.method == 'POST':

            # Get all items from form
            selectedItems = request.form.getlist('items')

            con = sql.connect(DATABASE)
            con.row_factory = sql.Row
            cursor = con.cursor()

            # Fetch school data
            cursor.execute('SELECT * FROM `schools` WHERE id=?', [schoolId])
            school = cursor.fetchone()

            items = []

            for item in selectedItems:
                cursor.execute('SELECT * FROM `items` WHERE id=?', [item])
                row = cursor.fetchone()
                items.append({"id": row['id'], "name": f"{row['name']}"})

            session['items'] = items

            return render_template('/donate.html', school=school, items=items)
        else:
            return redirect('/schools')
    else:
        return redirect('/login')


@app.route('/donated/<schoolId>', methods=['POST', 'GET'])
def donated(schoolId):
    if (request.method == 'POST'):

        userId = session['userId']

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()

        # Loop through all selected items
        for item in session['items']:
            itemAmount = request.form.get('item-' + str(item['id']))

            # Insert donation into donations table
            cursor.execute("INSERT INTO `donations` (user_id, school_id, item_id, amount, received) VALUES (?, ?, ?, ?, ?)",
                           (userId, schoolId, item['id'], itemAmount, 0))
            con.commit()

        return render_template('/donated.html')


@app.route('/user_page')
def userPage():
    if 'userId' in session:
        userId = session['userId']

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row

        cursor = con.cursor()
        cursor.execute(
            'SELECT donations.amount, donations.received, schools.name AS school, items.name AS item, items.scores FROM `donations` INNER JOIN `schools` ON schools.id = donations.school_id INNER JOIN `items` ON items.id = donations.item_id WHERE donations.user_id=?', [userId])

        donations = cursor.fetchall()

        score = 0
        for donation in donations:
            if donation['received'] == 1:
                score = score + \
                    (int(donation['amount']) * int(donation['scores']))

        return render_template('user_page.html', donations=donations, score=score)


@app.route('/school_page')
def schoolPage():
    if 'userId' in session:
        schoolId = session['userId']

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row

        cursor = con.cursor()

        itemId = request.args.get('id')
        if itemId:
            cursor.execute(
                'UPDATE `donations` SET `received` = 1 WHERE id = ?', [itemId])
            con.commit()

        cursor.execute(
            'SELECT donations.id, donations.amount, donations.received, users.name AS user, items.name AS item, items.scores FROM `donations` INNER JOIN `schools` ON schools.id = donations.school_id INNER JOIN `items` ON items.id = donations.item_id INNER JOIN `users` ON users.id = donations.user_id WHERE donations.school_id=?', [schoolId])

        donations = cursor.fetchall()

        return render_template('school_page.html', donations=donations)
    else:
        return redirect('/login')


@app.route('/rank')
def rank():
    if 'userId' in session:
        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()

        cursor.execute(
            "SELECT users.name, SUM(donations.amount * items.scores) AS score FROM donations INNER JOIN items ON items.id = donations.item_id INNER JOIN users ON users.id = donations.user_id WHERE donations.received=1 GROUP BY user_id ORDER BY SUM(donations.amount * items.scores) DESC")
        rank = cursor.fetchall()
        return render_template('rank.html', rank=rank)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()

        # TODO Create a field on database to identify an administrator!
        cursor.execute(
            "SELECT * FROM `users` WHERE email = ?", [email])
        row = cursor.fetchone()

        # TODO Hash Password
        if row['password'] != password:
            msg = 'Password incorect, please try again.'
            return render_template('result.html', page='/admin', text='Go Back', msg=msg)
        session['userId'] = row['id']
        session['isAdmin'] = True
        return redirect('/admin')
    else:
        if 'isAdmin' in session:
            con = sql.connect(DATABASE)
            con.row_factory = sql.Row

            cursor = con.cursor()
            cursor.execute('SELECT * FROM `schools`')

            schools = cursor.fetchall()
            return render_template('admin/index.html', schools=schools)
        else:
            return render_template('admin/login.html')


@app.route('/admin/add', methods=['POST', 'GET'])
def add():
    if 'isAdmin' in session:
        if request.method == 'POST':

            # Take the values from the form
            name = request.form['name']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            file = request.files['file']
            items = request.form.getlist('items')

            con = sql.connect(DATABASE)
            con.row_factory = sql.Row
            cursor = con.cursor()

            # Check if the type of file is allowed
            if file and allowed_file(file.filename):
                # Take the file name
                filename = secure_filename(file.filename)
                # Save the file extension
                extension = filename.rsplit('.', 1)[1]
                # Sum the current date to the file name
                filename = filename.rsplit(
                    '.', 1)[0] + str(datetime.now().time())
                # Hash the filename and reinsert the extension
                h = hashlib.sha256()
                h.update(filename.encode('utf-8'))
                newFilename = h.hexdigest() + '.' + extension
                # Copy the file to the upload folder
                file.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], newFilename))
            else:
                flash('Error: Image not uploaded')
                return redirect('/admin')

            cursor.execute("INSERT INTO `schools` (name, address, city, state, country, phone, email, password, latitude, longitude, photo) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                name, address, city, state, country, phone, email, password, latitude, longitude, newFilename))
            con.commit()

            schoolId = cursor.lastrowid

            for item in items:
                cursor.execute(
                    "INSERT INTO `school_items` (school_id, item_id) VALUES (?,?)", (schoolId, item))
                con.commit()

            flash('School successfully added.')
            return redirect('/admin')
        else:
            return render_template('admin/add_school.html')
    else:
        return redirect('/admin')


@app.route('/admin/remove/<id>')
def remove(id):
    if 'isAdmin' in session:
        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()

        cursor.execute("DELETE FROM `schools` WHERE id = ?", [id])
        cursor.execute(
            "DELETE FROM `school_items` WHERE school_id = ?", [id])

        con.commit()
        flash('School successfully removed')
        return redirect('/admin')
    else:
        return redirect('/admin')


@app.route('/logout')
def logout():
    session.pop('userId', None)
    if 'isAdmin' in session:
        session.pop('isAdmin', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
