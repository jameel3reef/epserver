#!/usr/bin/env python3
import os
import socket
import fcntl
import struct
from flask import Flask, render_template , request , send_from_directory , redirect , url_for
from http.server import SimpleHTTPRequestHandler, HTTPServer
import argparse
# Done by: MrAlphaQ

# ANSI color codes
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
YELLOW = '\033[33m'

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip_address = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])
    except IOError:
        ip_address = '127.0.0.1'  # Default to localhost if interface is not found
    return ip_address

# Function to recursively find all files in a directory
def find_all_files(base_path):
    files = []
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)
        if os.path.isdir(full_path):
            files.extend(find_all_files(full_path))
        else:
            files.append(full_path)
    return files
def start_http_server_cli(server_address, base_path):
    all_files = find_all_files(base_path)
    linux_files, windows_files = categorize_files(all_files)
    print(f"{BOLD}{GREEN}Linux Files:{RESET}")
    print(f"{YELLOW}{BOLD}├───Enumeration:{RESET}")
    I,P=server_address
    l = "http://"+I+":"+str(P)+"/{f}"
    if P==80:
        l = "http://"+I+"/{f}"
    for file in linux_files['enumeration']:
        print(f"{YELLOW}{BOLD}│   ├─── {RESET}{YELLOW}{l.format(f=file)}{RESET}")
        if file == linux_files['enumeration'][-1]:
            print(f"{YELLOW}{BOLD}│   └─── {RESET}{YELLOW}{l.format(f=file)}{RESET}")
    print(f"{RED}{BOLD}└───Attacking:{RESET}")
    for file in linux_files['attacking']:
        print(f"{RED}{BOLD}    ├─── {RESET}{RED}{l.format(f=file)}{RESET}")
        if file == linux_files['attacking'][-1]:
            print(f"{RED}{BOLD}    └─── {RESET}{RED}{l.format(f=file)}{RESET}")
    print(f"{BLUE}{BOLD}Windows Files:{RESET}")
    print(f"{YELLOW}{BOLD}├───Enumeration:{RESET}")
    for file in windows_files['enumeration']:
        print(f"{YELLOW}{BOLD}│   ├─── {RESET}{YELLOW}{l.format(f=file)}{RESET}")
        if file == windows_files['enumeration'][-1]:
            print(f"{YELLOW}{BOLD}│   └─── {RESET}{YELLOW}{l.format(f=file)}{RESET}")
    print(f"{RED}{BOLD}└───Attacking:{RESET}")
    for file in windows_files['attacking']:
        print(f"{RED}{BOLD}    ├─── {RESET}{RED}{l.format(f=file)}{RESET}")
        if file == windows_files['attacking'][-1]:
            print(f"{RED}{BOLD}    └─── {RESET}{RED}{l.format(f=file)}{RESET}")
    os.chdir(base_path)
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(server_address, handler)
    print(f"{GREEN}Serving HTTP on {server_address[0]} port {server_address[1]} ( {BLUE}{l.format(f='')}{RESET}{GREEN} ) ...{RESET}")
    httpd.serve_forever()
    
# Function to categorize files into Linux and Windows, enumeration and attacking
def categorize_files(files):
    global linux_files, windows_files
    linux_files = {'enumeration': [], 'attacking': []}
    windows_files = {'enumeration': [], 'attacking': []}
    
    for file in files:
        relative_path = os.path.relpath(file, base_path)
        if "linux" in relative_path:
            if "enumeration" in relative_path:
                linux_files['enumeration'].append(file.split("/")[-1])
            elif "attacking" in relative_path:
                linux_files['attacking'].append(file.split("/")[-1])
        elif "windows" in relative_path:
            if "enumeration" in relative_path:
                windows_files['enumeration'].append(file.split("/")[-1])
            elif "attacking" in relative_path:
                windows_files['attacking'].append(file.split("/")[-1])
    
    return linux_files, windows_files

# Flask setup
app = Flask(__name__)
# Define the route for the web interface
@app.route('/')
def index():
    all_files = find_all_files(base_path)
    linux_files, windows_files = categorize_files(all_files)
    return render_template('index.html', linux_files=linux_files, windows_files=windows_files, server_ip=server_ip)


def get_unique_filename(directory, filename, ip):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = f"{ip}_{filename}"

    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{ip}_{base}{counter}{extension}"
        counter += 1

    return unique_filename

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['f']
    if not file:
        return 'No file received', 400
    # Extract file name
    filename = file.filename
    if '..' in filename:
        return 'Invalid filename', 400
    unique_filename = get_unique_filename(app.config['UPLOAD_FOLDER'], filename,request.remote_addr)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    # Save the received file
    with open(file_path, 'wb') as f:
        f.write(request.data)
    return f'File {unique_filename} uploaded successfully', 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if '..' in filename:
        return 'Invalid filename', 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/<filename>')
def serve_file(filename):
    if filename == 'favicon.ico':
        return send_from_directory(base_path, filename)
    if '..' in filename:
        return 'Invalid filename', 400
    if filename in linux_files['enumeration']:
        return send_from_directory(base_path+'linux/enumeration/', filename)
    elif filename in linux_files['attacking']:
        return send_from_directory(base_path+'linux/attacking/', filename)
    elif filename in windows_files['enumeration']:
        return send_from_directory(base_path+'windows/enumeration/', filename)
    elif filename in windows_files['attacking']:
        return send_from_directory(base_path+'windows/attacking/', filename)
    else:
        return 'File not found', 404

def list_uploaded_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return files

# Route to serve the uploaded files
@app.route('/uploaded_files')
def uploaded_files():
    files = list_uploaded_files()
    return render_template('uploaded_files.html', files=files, server_ip=server_ip)

# Route to handle file deletion
@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    if '..' in filename:
        return 'Invalid filename', 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('uploaded_files'))
    else:
        return 'File not found', 404
    
if __name__ == "__main__":
    try:
        base_path = os.path.expanduser("~")+"/epserver/"
        parser = argparse.ArgumentParser(description='Enumeration, Attacking and Privilege escalation Server')
        parser.add_argument('-p', '--port', type=int, default=80, help='Port number for the server (default: 80)')
        parser.add_argument('-i', '--interface', default='lo', help='Network interface to use (default: lo)')
        parser.add_argument('--cli', action='store_true',help='Run the server in CLI mode')
        args = parser.parse_args()
        network_interface = args.interface
        server_ip = get_ip_address(network_interface)
        server_port = args.port
        print(f"{BOLD}{GREEN}IF YOU WANT TO ADD YOUR OWN TOOLS, ADD THEM TO THE {BLUE}{base_path}{GREEN} LINUX OR WINDOWS FOLDERS{RESET}")
        if args.cli:
            start_http_server_cli((server_ip, server_port), base_path)
            exit(0)
        all_files = find_all_files(base_path)
        categorize_files(all_files)
        app.template_folder = base_path + 'templates'
        app.config['UPLOAD_FOLDER'] = base_path+'uploads'
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Start the Flask server
        app.run(host=server_ip, port=server_port)
    except KeyboardInterrupt:
        print("\nServer stopped by the user.\nGoodbye!")
        exit(0)
