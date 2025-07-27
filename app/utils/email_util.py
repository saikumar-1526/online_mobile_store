import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipient, subject, body):

    # Email setup
    sender_email = "your_email@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your_email@gmail.com"
    smtp_password = "Your 2FA Key"  # Use your App Password if 2FA is enabled

    # Create the email message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Attach the HTML content to the email
    msg.attach(MIMEText(body, 'html'))

    # Send the email using Gmail's SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade to a secure connection
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()

def verify_email(recipient, name, subject, verifier, base_url):
    # Read HTML content from file
    with open("templates/notification/account.html", "r", encoding='utf-8') as file:
        html_content = file.read()
    html_content = html_content.replace("__usr__", name)
    html_content = html_content.replace("__vrfy_url__", f"{base_url} auth/verify_user/?s={verifier}")
    send_email(recipient, subject, html_content)

def order_email(recipient, name, subject, order_data):
    with open("templates/notification/order.html", "r", encoding='utf-8') as file:
        html_content = file.read()
    html_content = html_content.replace("__usr__", name)
    html_content = html_content.replace("__order_id__", order_data["order_id"])
    html_content = html_content.replace("__order_status__", order_data["order_status"])
    html_content = html_content.replace("__order_details__", order_data["order_details"])
    send_email(recipient, subject, html_content)