import time
import datetime
import random
import requests
import threading

print("Starting Camera")


message_codes = ["saw a frog","saw a cat",'saw a dog']
message_cache = []
lock = threading.Lock()

def long_polling() -> None:
    global message_cache
    while True:
        try:
            url = "http://server:5000/poll"
        
            response = requests.post(url, json={}, timeout=35)
            
            if response.status_code == 200:
                data = response.json()

                if "command" in data and data["command"] == "send_logs":
                    print('recieved send_logs command, sending logs...')

                with lock:
                    logs_to_send = message_cache.copy()
                
                if logs_to_send:
                    log_response = requests.post(url, json=logs_to_send, timeout=10)

                    if log_response.status_code == 200:
                        print(f"Successfully sent {len(logs_to_send)} logs")
                        with lock:
                            # Remove only logs that were successfully sent
                            message_cache = [log for log in message_cache if log not in logs_to_send]                        
                    else:
                        print(f"Failed to send logs: {log_response.status_code}")
                else:
                    print("No logs to send")

        except requests.exceptions.Timeout:
            print("Request timed out. Keeping logs for retry.")
        except requests.exceptions.RequestException as e:
            print("Error:", e)
        
        print("Backing off long polling for 5 seconds")
        time.sleep(5)
    
def generate_logs() -> None:
    global message_cache
    while True:
        log = {
            'message_code':random.choice(message_codes),
            'datetime': datetime.datetime.now().isoformat()
        }
        with lock:
            message_cache.append(log)
            print(f'Log loop ran. Current cache length:{len(message_cache)}')
        time.sleep(1)

while __name__ == '__main__':
    log_thread = threading.Thread(target=generate_logs, daemon=True)
    poll_thread = threading.Thread(target=long_polling, daemon=True)

    log_thread.start()
    poll_thread.start()

    log_thread.join()
    poll_thread.join()