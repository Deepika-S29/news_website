
from flask import render_template, Blueprint, Flask, request, redirect, url_for, session
from news_project.news_source.ndtv_api import fetch_general_news
import re
import secrets
import mysql.connector

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'geeklogin',
}

# Initialize MySQL
mysql = mysql.connector.connect(**mysql_config)
cursor = mysql.cursor(dictionary=True)

core = Blueprint("core", __name__)

# Rest of your routes and code...

# Registration route
@core.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Use parameterized query to prevent SQL injection
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@core.route("/news_grid", methods=['GET'])
def news_grid():
    # Establish a MySQL database connection
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'geeklogin',
    }
    conn = mysql.connector.connect(**mysql_config)
   
    # Fetch image and description data from the database
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT image, description FROM images')
    news_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('news_grid.html', news_data=news_data)
from flask import request, render_template
import re
import io
import mysql.connector

@core.route("/contact", methods=['GET', 'POST'])
def contact():
    msg = ''

    if request.method == 'POST':
        image = request.files.get('image')  # Get the uploaded image file
        description = request.form.get('description')

        if not image or not description:
            msg = 'Please fill out the form!'
        else:
            # Check if the uploaded file is an allowed image file type (e.g., JPEG, PNG)
            allowed_extensions = {'jpg', 'jpeg', 'png'}
            if '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                # Read the image data as bytes
                image_data = image.read()

                # Establish a MySQL database connection
                mysql_config = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': '',
                    'database': 'geeklogin',
                }
                conn = mysql.connector.connect(**mysql_config)

                # Insert the image data and description into the database table
                cursor = conn.cursor(dictionary=True)
                cursor.execute('INSERT INTO images (image, description) VALUES (%s, %s)', (image_data, description))
                conn.commit()
                conn.close()

                msg = 'You have successfully registered with an image and description!'
            else:
                msg = 'Invalid file format. Please upload a valid image (e.g., JPG, JPEG, PNG).'

    return render_template('contact.html', msg=msg)
# Login route
@core.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Use parameterized query to prevent SQL injection
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            msg = 'Logged in successfully!'
            return redirect(url_for('core.index'))
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

# Home Page View
@core.route("/")
def index():
    uri = "https://ndtvapi.vercel.app/{}?{}=values({})"
    
    home_latest_news = fetch_general_news(uri=uri.format("general", "category", "latest"))
    home_india_news = fetch_general_news(uri=uri.format("general", "category", "india"))
    home_world_news = fetch_general_news(uri=uri.format("general", "category", "world"))
    home_business_news = fetch_general_news(uri=uri.format("general", "category", "business"))
    home_football_news = fetch_general_news(uri=uri.format("sports", "sport", "football"))
    home_cricket_news = fetch_general_news(uri=uri.format("sports", "sport", "cricket"))
    home_tennis_news = fetch_general_news(uri=uri.format("sports", "sport", "tennis"))
    
    return render_template(
        "index.html",
        home_latest_news=home_latest_news,
        home_india_news=home_india_news,
        home_world_news=home_world_news,
        home_business_news=home_business_news,
        home_football_news=home_football_news,
        home_cricket_news=home_cricket_news,
        home_tennis_news=home_tennis_news,
    )

# 404 Error View
@core.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

# Run the Flask app
if __name__ == "__main__":
    app.register_blueprint(core)
    app.run(debug=True)
