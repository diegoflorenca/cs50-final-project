from flask import Flask, request, render_template, redirect
import sqlite3 as sql

app = Flask(__name__)

DATABASE = './db/data.db'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        con = sql.connect(DATABASE)
        con.row_factory = sql.Row
        cursor = con.cursor()
        cursor.execute(
            "SELECT * FROM `users` WHERE email = ?", [email])
        rows = cursor.fetchall()
        row = rows[0]
        # Hash Password
        if row['password'] != password:
            msg = 'Password incorect, please try again.'
            return render_template('result.html', page='/login', text='Go Back', msg=msg)
        return redirect('/schools')
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            photo = request.form.get('photo')

            with sql.connect(DATABASE) as con:
                cursor = con.cursor()

                cursor.execute("INSERT INTO `users` (name, email, password, photo)VALUES (?,?,?,?)", (
                    name, email, password, photo))

                con.commit()
                msg = 'New user added successfully, login to continue!'
        except:
            con.rollback()
            msg = 'Error in insert operation'
        finally:
            return render_template('result.html', page='/login', text='Go to login page', msg=msg)
    else:
        return render_template('add_user.html')


@app.route('/schools')
def schools():
    con = sql.connect(DATABASE)
    con.row_factory = sql.Row

    cursor = con.cursor()
    cursor.execute('SELECT * FROM schools')

    rows = cursor.fetchall()
    return render_template('schools.html', rows=rows)


@app.route('/school')
def ong():
    school = request.args.get('name')
    return f"<h1>School page: {school} </h1> <a href='/donate?name=Etec%20Carapicuiba'>Donate</a>"


@app.route('/donate')
def donate():
    school = request.args.get('name')
    return f"<h1>Donate to {school} </h1> <a href='/schools'>schools</a>"


@app.route('/admin')
def admin():
    con = sql.connect(DATABASE)
    con.row_factory = sql.Row

    cursor = con.cursor()
    cursor.execute('SELECT * FROM schools')

    rows = cursor.fetchall()
    return render_template('admin/index.html', rows=rows)


@app.route('/admin/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            address = request.form.get('address')
            phone = request.form.get('phone')
            email = request.form.get('email')
            items_collected = request.form.get('items_collected')
            longitude = request.form.get('longitude')
            latitude = request.form.get('latitude')
            photo = request.form.get('photo')
            photo_profile = request.form.get('photo_profile')

            with sql.connect(DATABASE) as con:
                cursor = con.cursor()

                cursor.execute("INSERT INTO `schools` (name, address, phone, email, items_collected, longitude, latitude, photo, photo_profile) VALUES (?,?,?,?,?,?,?,?,?)", (
                    name, address, phone, email, items_collected, longitude, latitude, photo, photo_profile))

                con.commit()
                msg = 'School successfully added'
        except:
            con.rollback()
            msg = 'Error in insert operation'
        finally:
            return render_template('result.html', page='/admin', text='Go Back', msg=msg)
    else:
        return render_template('admin/add_school.html')


if __name__ == '__main__':
    app.run(debug=True)
