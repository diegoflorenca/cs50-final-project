from flask import Flask, request, render_template, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'dYfgd91s5xH6vc7f8ykj6E5465-HvT'

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
        # Need to Hash Password
        if row['password'] != password:
            msg = 'Password incorect, please try again.'
            return render_template('result.html', page='/login', text='Go Back', msg=msg)
        session['userId'] = row['id']
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
    if 'userId' in session:
        con = sql.connect(DATABASE)
        con.row_factory = sql.Row

        cursor = con.cursor()
        cursor.execute('SELECT * FROM schools')

        rows = cursor.fetchall()
        return render_template('schools.html', rows=rows)
    else:
        return redirect('/login')


@app.route('/school/<schoolId>')
def ong(schoolId):
    if 'userId' in session:
        con = sql.connect(DATABASE)
        con.row_factory = sql.Row

        cursor = con.cursor()
        cursor.execute('SELECT * FROM `schools` WHERE id=?', [schoolId])

        rows = cursor.fetchall()
        row = rows[0]

        cursor.execute(
            'SELECT * FROM `schools_items` WHERE `school_id`=?', [schoolId])
        items = cursor.fetchall()
        return render_template('school.html', row=row, items=items)
    else:
        return redirect('/login')


@app.route('/donate')
def donate():
    if 'userId' in session:
        school = request.args.get('name')
        return f"<h1>Donate to {school} </h1> <a href='/schools'>schools</a>"
    else:
        return redirect('/login')


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
        rows = cursor.fetchall()
        row = rows[0]
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

            rows = cursor.fetchall()
            return render_template('admin/index.html', rows=rows)
        else:
            return render_template('admin/login.html')


@app.route('/admin/add', methods=['POST', 'GET'])
def add():
    if 'isAdmin' in session:
        if request.method == 'POST':
            try:
                # teste with: request.form['name']
                name = request.form['name']
                address = request.form['address']
                phone = request.form['phone']
                email = request.form['email']
                password = request.form['password']
                longitude = request.form['longitude']
                latitude = request.form['latitude']
                photo = request.form['photo']
                photo_profile = request.form['photo_profile']
                items = request.form.getlist('items')

                with sql.connect(DATABASE) as con:
                    cursor = con.cursor()

                    cursor.execute("INSERT INTO `schools` (name, address, phone, email, password, longitude, latitude, photo, photo_profile) VALUES (?,?,?,?,?,?,?,?,?)", (
                        name, address, phone, email, password, longitude, latitude, photo, photo_profile))

                    con.commit()

                    schoolId = cursor.lastrowid

                    for item in items:
                        cursor.execute(
                            "INSERT INTO `schools_items` (school_id, item_id) VALUES (?,?)", (schoolId, item))

                    msg = 'School successfully added'
            except:
                con.rollback()
                msg = 'Error in insert operation'
            finally:
                return render_template('result.html', page='/admin', text='Go Back', msg=msg)
        else:
            return render_template('admin/add_school.html')
    else:
        return redirect('/admin')


@app.route('/admin/remove/<id>')
def remove(id):
    if 'isAdmin' in session:
        try:
            with sql.connect(DATABASE) as con:
                cursor = con.cursor()

                cursor.execute("DELETE FROM `schools` WHERE id = ?", [id])
                cursor.execute(
                    "DELETE FROM `schools_items` WHERE school_id = ?", [id])

                con.commit()
                msg = 'School successfully removed'
        except:
            con.rollback()
            msg = 'Error in delete operation'
        finally:
            return render_template('result.html', page='/admin', text='Go Back', msg=msg)
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
