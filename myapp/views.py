import smtplib
from email.message import EmailMessage
from django.shortcuts import render, redirect
from datetime import datetime
import threading
import time
import schedule

# Global variables
sent_emails = []
scheduler_thread = None
terminate_scheduler = False
email_count_limit = 0  # Maximum number of emails to send
email_body_words = []  # List to store the body text as words
email_subject = ""  # Initial subject

def send_email(sender_email, sender_password, recipient_email, subject, body):
    global sent_emails

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sent_emails.append({'count': len(sent_emails) + 1, 'timestamp': timestamp})
            print(f"Email sent to {recipient_email} at {timestamp}")
    except Exception as e:
        print(f"Error: {e}")

def run_scheduler():
    global terminate_scheduler, email_count_limit
    while not terminate_scheduler:
        schedule.run_pending()
        time.sleep(1)

        # Stop when the count limit is reached
        if len(sent_emails) >= email_count_limit:
            terminate_scheduler = True
            schedule.clear()

def home(request):
    return render(request, 'index.html')

def show_data(request):
    global scheduler_thread, terminate_scheduler, sent_emails, email_count_limit, email_body_words, email_subject

    if request.method == 'POST':
        sender = request.POST['sender']
        app_password = request.POST['appPass']
        receiver = request.POST['receiver']
        email_subject = request.POST['subject']  # Set the initial subject
        message = request.POST['mail_body']
        time_interval = int(request.POST['time'])  # Time in seconds
        email_count_limit = int(request.POST['email_count'])  # Count of emails to send

        # Split the email body into words and store them in the global list
        email_body_words = message.split()

        sent_emails = []
        terminate_scheduler = False

        # Define the job
        def job():
            global email_subject
            if email_body_words:  # Only send an email if there are still words left
                body = ' '.join(email_body_words)  # Join the remaining words to form the body
                send_email(sender, app_password, receiver, email_subject, body)
                # Remove the first word from the body text
                email_body_words.pop(0)
                # Add the word "new" to the subject
                email_subject += " n"

        # Schedule the email
        schedule.every(time_interval).seconds.do(job)

        # Start the scheduler in a separate thread
        if not scheduler_thread or not scheduler_thread.is_alive():
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()

        return redirect('email_status')  # Redirect to email_status view
    else:
        return redirect('home')  # Redirect to home if not a POST request

def email_status(request):
    global terminate_scheduler
    # If terminated, redirect to home
    if terminate_scheduler:
        return redirect('home')

    return render(request, 'app.html', {'sent_emails': sent_emails})

def terminate_scheduler_view(request):
    global terminate_scheduler
    terminate_scheduler = True
    schedule.clear()  # Clear scheduled jobs
    return redirect('home')  # Redirect to home
