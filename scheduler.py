import requests
import schedule
import time

# Define the job to run
def send_warning_emails_job():
    # Call your Flask API endpoint to send warning emails
    requests.post('http://localhost:5000/api/send_warning_emails')
    pass

# Define the job to run
def delete_unsubscribed_data_job():
    # Call your Flask API endpoint to send warning emails
    requests.post('http://localhost:5000/api/delete_unsubscribers_data')
    pass

# Schedule the job to run every day at a specific time
schedule.every().day.at("08:00").do(send_warning_emails_job)
schedule.every().day.at("08:00").do(delete_unsubscribed_data_job)

# Run the scheduler continuously
while True:
    print('Scheduler Running')
    schedule.run_pending()
    time.sleep(1)  # Sleep for 1 second to avoid high CPU usage


