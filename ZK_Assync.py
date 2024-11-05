import socket
from datetime import datetime
import logging
import threading
import json
import os
from queue import Queue
import time
import re
from attlog_parser import AttLogParser

# Configure logging with ANSI escape codes for colors
class CustomFormatter(logging.Formatter):
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    PINK = "\033[95m"
    RESET = "\033[0m"
    FORMATS = {
        logging.INFO: "%(asctime)s - %(levelname)s - %(message)s",
        'DEFAULT': "%(asctime)s - %(levelname)s - %(message)s"
    }

    def format(self, record):
        if "Connected by" in record.msg or "Server listening" in record.msg:
            log_fmt = self.GREEN + "%(asctime)s - %(levelname)s - %(message)s" + self.RESET
        elif "Received from client" in record.msg:
            log_fmt = self.YELLOW + "%(asctime)s - %(levelname)s - %(message)s" + self.RESET
        elif "Writing to file" in record.msg or "Parsed JSON packet" in record.msg:
            log_fmt = self.BLUE + "%(asctime)s - %(levelname)s - %(message)s" + self.RESET
        elif "Closing connection" in record.msg:
            log_fmt = self.RED + "%(asctime)s - %(levelname)s - %(message)s" + self.RESET
        elif "Writing new entries to sanatise.json" in record.msg:
            log_fmt = self.PINK + "%(asctime)s - %(levelname)s - %(message)s" + self.RESET
        else:
            log_fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# cSpell:ignore levelname ZKID atttime ATTSTATE verifymode clockid ATTLOG attlog

def extract_attlog(data):
    content_length_index = data.find("Content-Length:")
    if content_length_index == -1:
        return None

    content_length_start = content_length_index + len("Content-Length:")
    content_length_end = data.find("\n", content_length_start)
    content_length = int(data[content_length_start:content_length_end].strip())

    data_start = data.find("\n", content_length_end) + 1
    attlog_data = data[data_start:data_start + content_length].strip()
    
    return attlog_data

def extract_sn(data_str):
    sn_match = re.search(r'SN=([^&]+)', data_str)
    if sn_match:
        return sn_match.group(1)
    else:
        return None

def write_to_file(queue, filename):
    while True:
        json_packet = queue.get()
        if json_packet is None:
            break
        logging.debug(f"Writing to file: {json_packet}")
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump([], f)
        with open(filename, 'r+') as f:
            data = json.load(f)
            data.append(json_packet)
            f.seek(0)
            json.dump(data, f, indent=2)
        queue.task_done()

def handle_device(host, port, device_ip, queue):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        s.settimeout(10)  # Set socket timeout for faster handling
        logging.info(f"Server listening on {host}:{port}")
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    logging.info(f"Connected by {addr} (expected {device_ip})")
                    conn.settimeout(10)
                    while True:
                        try:
                            data = conn.recv(4096)
                            if not data:
                                break
                            try:
                                data_str = data.decode('utf-8')
                            except UnicodeDecodeError:
                                data_str = data.decode('utf-8', errors='ignore')
                                logging.warning("Invalid byte sequence encountered. Proceeding with ignored errors.")
                            
                            logging.debug(f"Received from client: {data_str}")

                            if "=ATTLOG&Stamp=9999" in data_str:
                                attlog_data = extract_attlog(data_str)
                                sn_value = extract_sn(data_str)
                                if attlog_data and sn_value:
                                    combined_value = f"{attlog_data}\t{addr}\t{sn_value}"
                                    json_packet = {
                                        "attlog": combined_value
                                    }
                                    logging.info(f"Parsed JSON packet: {json.dumps(json_packet, indent=2)}")
                                    logging.debug(f"Adding to queue: {json_packet}")
                                    queue.put(json_packet)

                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
                            response = f"Server Send Data: {timestamp}\nOK"
                            conn.sendall(response.encode())
                        except socket.timeout:
                            logging.info(f"Connection timeout with {addr}")
                            break
            except socket.timeout:
                logging.info("Listening socket timeout")

def start_server(host, devices, filename):
    queue = Queue()
    
    writer_thread = threading.Thread(target=write_to_file, args=(queue, filename))
    writer_thread.start()
    logging.debug("Writer thread started")
    
    threads = []
    
    for device in devices:
        thread = threading.Thread(target=handle_device, args=(host, device['port'], device['ip'], queue))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    queue.put(None)
    writer_thread.join()

if __name__ == "__main__":
    host = "0.0.0.0"  # Use the correct host IP
    devices = [ # map for potential ports to listen to if devices ports differ
        {"ip": "127.0.0.1", "port": 5001},
        {"ip": "127.0.0.1", "port": 5002},
        {"ip": "127.0.0.1", "port": 5003},
        {"ip": "127.0.0.1", "port": 5004},
        {"ip": "127.0.0.1", "port": 5005},
        {"ip": "127.0.0.1", "port": 5006},
        {"ip": "127.0.0.1", "port": 5007},
        {"ip": "127.0.0.1", "port": 5008},
        {"ip": "127.0.0.1", "port": 5009},
        {"ip": "127.0.0.1", "port": 5010}
    ]
    attlog_filename = "attlog.json"
    sanatise_filename = "sanatise.json"
    
    if not os.path.exists(attlog_filename):
        with open(attlog_filename, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(sanatise_filename):
        with open(sanatise_filename, 'w') as f:
            json.dump([], f)

    parser_thread = threading.Thread(target=AttLogParser().run)
    parser_thread.start()

    start_server(host, devices, attlog_filename)
