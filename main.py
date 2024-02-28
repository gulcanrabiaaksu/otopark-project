from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from roboflow import Roboflow
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

# Session güvenliği
app.secret_key = 'xyzsdfg'

# MySQL bağlantı bilgileri
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'psw'
app.config['MYSQL_DB'] = 'otopark'

# MySQL bağlantısı
mysql = MySQL(app)

# Roboflow bağlantıları
rf = Roboflow(api_key="Lqx7R0mEcLUX1DfexisP")
project = rf.workspace().project("car-space-find")

def admin():
    return 'loggedin' in session and session.get('role') == 'admin'

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/randevu', methods=['GET', 'POST'])
def randevu():
    if request.method == 'POST':
        selected_il = request.form.get('ilSelect')
        selected_ilce = request.form.get('ilceSelect')
        selected_otopark = request.form.get('otoparkSelect')
        kisi_sayisi = request.form.get('kisiSayisi')
        email = session.get('email')

        if selected_otopark == 'Adayel Otopark':
            file_name = "park1.jpg"
        elif selected_otopark == 'Engin Otopark':
            file_name = "park2.jpg"
        elif selected_otopark == 'Kıroğlu Otopark':
            file_name = "park3.jpg"
        elif selected_otopark == 'Cem Otopark':
            file_name = "park4.jpg"
        elif selected_otopark == 'Kardeşler Otopark':
            file_name = "park5.jpg"
        elif selected_otopark == 'Elit Otopark':
            file_name = "park6.jpg"
        elif selected_otopark == 'Çiçek Otopark':
            file_name = "park7.jpg"
        elif selected_otopark == 'Fatih Otopark':
            file_name = "park8.jpg"
        elif selected_otopark == 'Eray Otopark':
            file_name = "park8.jpg"
        else:
            return render_template('randevu.html', error='Geçersiz seçenek')

        # Modeli çalıştır ve sonuçları al
        model = project.version(2).model
        result = model.predict(file_name, confidence=20, overlap=30).json()

        # Boş park yerlerini say
        class_counts = {"occupied": 0, "empty": 0}
        for prediction in result["predictions"]:
            class_name = prediction["class"]
            if class_name in class_counts:
                class_counts[class_name] += 1

        # Boş park yerlerini kontrol et
        empty_park_spaces = class_counts["empty"]
        THRESHOLD = 1

        kisi_sayisi_from_db = get_kisi_sayisi_from_db(selected_il, selected_ilce, selected_otopark)

        if empty_park_spaces < THRESHOLD:
            message = "Boş park yerleri sayısı düşük. Randevu alma sistemi başlatılıyor..."
            # Burada randevu alma sistemi için gerekli işlemleri ekleyebilirsiniz.
        else:
            kisi_sayisi_from_db = get_kisi_sayisi_from_db(selected_il, selected_ilce, selected_otopark)
            # Eğer yeterli boş park yeri varsa, başka bir işlem yapabilirsiniz.

        save_appointment_data(selected_il, selected_ilce, selected_otopark, kisi_sayisi)
        save_appointment_data_to_db(email, selected_il, selected_ilce, selected_otopark)

        return render_template('randevu.html', kisi_sayisi_from_db=kisi_sayisi_from_db, empty_park_spaces=empty_park_spaces)
    return render_template('randevu.html', empty_park_spaces=0, kisi_sayisi_from_db=0)


@app.route('/user_profile')
def user_profile():
    # Your user profile logic here
    return render_template('user.html')

@app.route('/not_logged_in_randevu', methods=['GET', 'POST'])
def not_logged_in_randevu():
    try:
        message = ''
        if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
            name = request.form['name']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM notlogged WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                message = 'Bu e-posta adresine sahip bir hesap zaten mevcut!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Geçersiz e-posta adresi!'
            else:
                cursor.execute('INSERT INTO notlogged (name, email) VALUES (%s, %s)', (name, email))
                mysql.connection.commit()
                return redirect(url_for('not_logged_in_randevu2'))  # Başarı sayfasına yönlendirme
        elif request.method == 'POST':
            message = 'Lütfen boş bırakılan yerleri doldurun!'
        return render_template('not_logged_in_randevu.html', message=message)
    except Exception as e:
        print(f"An error occurred: {str(e)}")




@app.route('/not_logged_in_randevu2', methods=['GET', 'POST'])
def not_logged_in_randevu2():
    if request.method == 'POST':
        selected_il = request.form.get('ilSelect')
        selected_ilce = request.form.get('ilceSelect')
        selected_otopark = request.form.get('otoparkSelect')
        kisi_sayisi = request.form.get('kisiSayisi')

        if selected_otopark == 'Adayel Otopark':
            file_name = "park1.jpg"
        elif selected_otopark == 'Engin Otopark':
            file_name = "park2.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Kıroğlu Otopark':
            file_name = "park3.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Cem Otopark':
            file_name = "park4.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Kardeşler Otopark':
            file_name = "park5.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Elit Otopark':
            file_name = "park6.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Çiçek Otopark':
            file_name = "park7.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Fatih Otopark':
            file_name = "park8.jpg"  # Değiştirilecek dosya adı
        elif selected_otopark == 'Eray Otopark':
            file_name = "park8.jpg"  # Değiştirilecek dosya adı
        else:
            return render_template('not_logged_in_randevu2.html', error='Geçersiz seçenek')

        # Modeli çalıştır ve sonuçları al
        model = project.version(2).model
        result = model.predict(file_name, confidence=20, overlap=30).json()

        # Boş park yerlerini say
        class_counts = {"occupied": 0, "empty": 0}
        for prediction in result["predictions"]:
            class_name = prediction["class"]
            if class_name in class_counts:
                class_counts[class_name] += 1

        # Boş park yerlerini kontrol et
        empty_park_spaces = class_counts["empty"]
        THRESHOLD = 1

        kisi_sayisi_from_db = get_kisi_sayisi_from_db(selected_il, selected_ilce, selected_otopark)

        if empty_park_spaces < THRESHOLD:
            message = "Boş park yerleri sayısı düşük. Randevu alma sistemi başlatılıyor..."
            # Burada randevu alma sistemi için gerekli işlemleri ekleyebilirsiniz.
        else:
            kisi_sayisi_from_db = get_kisi_sayisi_from_db(selected_il, selected_ilce, selected_otopark)
            # Eğer yeterli boş park yeri varsa, başka bir işlem yapabilirsiniz.
        save_appointment_data(selected_il, selected_ilce, selected_otopark, kisi_sayisi)
        return render_template('not_logged_in_randevu2.html', kisi_sayisi_from_db=kisi_sayisi_from_db,empty_park_spaces=empty_park_spaces)
    return render_template('not_logged_in_randevu2.html', empty_park_spaces=0, kisi_sayisi_from_db=0)

def get_kisi_sayisi_from_db(il, ilce, otopark):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT kisi_sayisi FROM randevular WHERE il = %s AND ilce = %s AND otopark = %s',(il, ilce, otopark))
        result = cursor.fetchone()
        return result['kisi_sayisi'] if result else 0
    except Exception as e:
        print(f"Error fetching kisi_sayisi from database: {str(e)}")
        return 0

def save_appointment_data(il, ilce, otopark, kisi_sayisi):
    try:
        # MySQL connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if there is an existing record for the selected location
        cursor.execute('SELECT * FROM randevular WHERE il = %s AND ilce = %s AND otopark = %s', (il, ilce, otopark))
        existing_record = cursor.fetchone()

        if existing_record:
            # If there is an existing record, update the kisi_sayisi column by incrementing it by 1
            updated_kisi_sayisi = existing_record['kisi_sayisi'] + 1
            cursor.execute('UPDATE randevular SET kisi_sayisi = %s WHERE id = %s',
                            (updated_kisi_sayisi, existing_record['id']))
            mysql.connection.commit()
        else:
            # If there is no existing record, insert a new record with kisi_sayisi set to 1
            cursor.execute('INSERT INTO randevular (il, ilce, otopark, kisi_sayisi) VALUES (%s, %s, %s, 1)',
                            (il, ilce, otopark))
            mysql.connection.commit()

        message = "Randevu başarıyla alındı."
        return message
    except Exception as e:
        message = "Error saving appointment data: " + str(e)
        print(message)
        return message


def save_appointment_data_to_db(email, il, ilce, otopark):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO randevu_tablosu (email, il, ilce, otopark) VALUES (%s, %s, %s, %s)',
                       (email, il, ilce, otopark))
        mysql.connection.commit()
        return "Randevu başarıyla kaydedildi."
    except Exception as e:
        return "Error saving appointment data: " + str(e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            # Kullanıcının Rolünü Konsola Yazdır
            print("Kullanıcının Rolü:", user['role'])

            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']

            if admin():
                # Eğer kullanıcı adminse, admin sayfasına yönlendir
                return redirect(url_for('admin_page'))
            else:
                message = 'Başarıyla giriş yapıldı!'
                return render_template('user.html', message=message)
        else:
            message = 'Geçersiz e-posta veya şifre. Lütfen tekrar deneyin.'
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    try:
        message = ''
        if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
            name = request.form['name']
            password = request.form['password']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                message = 'Bu e-posta adresine sahip bir hesap zaten mevcut!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Geçersiz e-posta adresi!'
            elif not name or not password or not email:
                message = 'Lütfen formu doldurun!'
            else:
                cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s)', (name, email, password, 'user'))
                mysql.connection.commit()
                message = 'Başarıyla kayıt oldunuz!'

        elif request.method == 'POST':
            message = 'Lütfen boş bırakılan yerleri doldurun!'
        return render_template('register.html', message=message)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


@app.route('/admin')
def admin_page():
    # Admin sayfasının içeriği
    if admin():
        return render_template('admin.html')
    else:
        return redirect(url_for('home'))

@app.route('/update_empty_spaces', methods=['POST'])

def update_empty_spaces():
    if request.method == 'POST':
        selected_il = request.form.get('ilSelect')
        selected_ilce = request.form.get('ilceSelect')
        selected_otopark = request.form.get('otoparkSelect')
        empty_spaces = request.form['empty_spaces']

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE randevular SET kisi_sayisi = %s WHERE il = %s AND ilce = %s AND otopark = %s',
                           (empty_spaces, selected_il, selected_ilce, selected_otopark))
            mysql.connection.commit()
            message = "Bilgiler güncellendi."
        except Exception as e:
            message = "Bilgi güncelleme hatası: " + str(e)
            print(message)

        return render_template('admin.html', message=message)

if __name__ == "__main__":
    app.run()
