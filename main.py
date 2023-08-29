import os, io
from subprocess import Popen, PIPE
import time
from sys import platform
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Lock
import time

_lock = Lock()
_lines = []
_paths = []

if platform == "win32":
    _paths = ["C:\\Temp\\mnt\\dev", "C:\\Temp\\mnt\\qa", "C:\\Temp\\mnt\\released"]
else:
    _paths = ["/mnt/tank/dev/images/lenovo", "/mnt/tank/qa/images/lenovo", "/mnt/tank/released/images/lenovo"]

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_paths")
def get_paths():
    return jsonify(_paths)

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)

@app.route("/get_subfolders")
def get_subfolders():
    subfolders = [[[f, get_size(os.path.join(path, f))] for f in os.listdir(path)] for path in _paths]

    return jsonify(subfolders)


@app.route("/copy_folder")
def copy_folder():
    _lock.acquire()
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")
    dest_path = request.args.get("dest_path")

    try:
        # copy subfolder
        if platform == "win32":
            command=f"robocopy /e /np {os.path.join(src_path, sub_folder)} {os.path.join(dest_path, sub_folder)}"
        else:
            command=f"rsync -r -v {os.path.join(src_path, sub_folder)} {dest_path}"
        
        proc = Popen(command, shell=True, stdout=PIPE)
        for msg in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
            msg = msg.replace('\t', '  ').replace('\n', '')
            socketio.emit("message", msg, broadcast=True)
            time.sleep(0.001)

        return jsonify({"message": f"{sub_folder} copied successfully to {dest_path}."})

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    finally:
        _lock.release()

@app.route("/delete_folder")
def delete_folder():
    _lock.acquire()
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")

    try:
        # delete folder
        if platform == "win32":
            command = f"rmdir /S /Q {os.path.join(src_path, sub_folder)}"
        else:
            command = f"rm -rf {os.path.join(src_path, sub_folder)}"

        proc = Popen(command, shell=True, stdout=PIPE)
        for msg in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
            msg = msg.replace('\t', '  ').replace('\n', '')
            socketio.emit("message", msg, broadcast=True)
            time.sleep(0.001)

        return jsonify({"message": f"{sub_folder} deleted successfully."})

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    finally:
        _lock.release()


@socketio.on("connect")
def connect():
    print("socket connected")

@socketio.on('message')
def handle_message(data):
    print('message received: ' + data)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    # socketio.run(app)
