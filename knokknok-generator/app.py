from flask import Flask, render_template, request, flash, redirect, url_for
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create the Flask application
application = Flask(__name__)
app = application

# Set secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def send_email(url, email):
    # Email settings
    sender_email = "noreply@knokknok.social"  # This can be any email
    receiver_email = "matt@knokknok.social"    # Your email where you want to receive notifications
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "New Video Generation Request"
    
    # Create the email body
    body = f"""
    New video generation request received:
    
    Property URL: {url}
    Customer Email: {email}
    Time: {datetime.now()}
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to email account using environment variables
        server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise e

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        email = request.form.get('email')
        
        if url and email:
            try:
                send_email(url, email)
                flash('Thank you! We will process your request soon.', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Error: {str(e)}")
                flash('Sorry, there was an error processing your request.', 'error')
                return redirect(url_for('index'))
        else:
            flash('Please fill in all fields.', 'error')
            
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
