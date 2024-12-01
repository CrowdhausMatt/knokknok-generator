from flask import Flask, render_template, request, flash, redirect, url_for
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
import sys

# Create the Flask application
application = Flask(__name__)
app = application

app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"Connecting to database: {DATABASE_URL}")  # Debug log
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                url TEXT,
                email TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")  # Debug log
    except Exception as e:
        print(f"Error initializing database: {str(e)}")  # Debug log
        raise e

def save_submission(url, email):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO submissions (timestamp, url, email) VALUES (%s, %s, %s)",
            (datetime.now(), url, email)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"Saved submission: {url}, {email}")  # Debug log
    except Exception as e:
        print(f"Error saving submission: {str(e)}")  # Debug log
        raise e

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        email = request.form.get('email')
        
        print(f"Received form submission - URL: {url}, Email: {email}")  # Debug log
        
        if url and email:
            try:
                save_submission(url, email)
                flash('Thank you! We will process your request soon.', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing submission: {error_msg}", file=sys.stderr)  # Debug log
                flash(f'Error: {error_msg}', 'error')
                return redirect(url_for('index'))
        else:
            flash('Please fill in all fields.', 'error')
            
    return render_template('index.html')

# Add error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    print(f"500 error: {str(error)}", file=sys.stderr)  # Debug log
    return "500 Internal Server Error", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
