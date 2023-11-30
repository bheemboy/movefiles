import os, io, shutil
from subprocess import Popen, PIPE
import time
from sys import platform
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Lock
import time

_paths = []
_lock = Lock()
_subfolders = []
_progressLines = []
_statusMessage = ''

if platform == "win32":
    _paths = ["C:\\Temp\\mnt\\dev", "C:\\Temp\\mnt\\qa", "C:\\Temp\\mnt\\released"]
else:
    _paths = ["/mnt/tank/dev/images/lenovo", "/mnt/tank/qa/images/lenovo", "/mnt/tank/released/images/lenovo"]

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)


def update_subfolders():
    global _paths, _lock, _subfolders, _progressLines, _statusMessage
    _subfolders = [[[f, get_size(os.path.join(path, f))] for f in os.listdir(path)] for path in _paths]
    return

def get_state():
    global _paths, _lock, _subfolders, _progressLines, _statusMessage
    return jsonify({"paths": _paths,
                    "disable_btns": _lock.locked(),
                    "subfolders": _subfolders,
                    "statusMessage": _statusMessage,
                    "progressLines": _progressLines})

####################################################

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/copy_folder")
def copy_folder():
    global _paths, _lock, _subfolders, _progressLines, _statusMessage
    _lock.acquire()
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")
    dest_path = request.args.get("dest_path")
    
    def _copy_function (src, dst):
        global _progressLines
        _progressLines.append(f"Copying {src} [{os.path.getsize(src)} bytes]...")
        socketio.emit("state", get_state().json, broadcast=True)
        retval = shutil.copy2(src, dst)
        update_subfolders()
        _progressLines.pop()
        _progressLines.append(f"Copying {src} [{os.path.getsize(src)}]...done.")
        socketio.emit("state", get_state().json, broadcast=True)
        return retval
        
    try:
        # copy subfolder
        _progressLines = []
        _statusMessage = f"Copying {os.path.join(src_path, sub_folder)} to {dest_path}"
        socketio.emit("state", get_state().json, broadcast=True)
        shutil.copytree(os.path.join(src_path, sub_folder), 
                        os.path.join(dest_path, sub_folder), 
                        copy_function= _copy_function)

                
        # proc = Popen(command, shell=True, stdout=PIPE)
        # i = 0
        # for msg in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        #     msg = msg.replace('\t', '  ').replace('\n', '')
        #     _progressLines.append(msg)
        #     time.sleep(0.001)

        #     # while copying a folder send status updates every 1 seconds
        #     i = i + 1
        #     if i == 1000:
        #         i = 0
        #         update_subfolders()
        #         socketio.emit("state", get_state().json, broadcast=True)

    except Exception as e:
        _statusMessage = f"An error occurred while copying the folder: {str(e)}"

    finally:
        _lock.release()
        update_subfolders()
    
    return get_state().json


@app.route("/delete_folder")
def delete_folder():
    global _paths, _lock, _subfolders, _progressLines, _statusMessage
    _lock.acquire()
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")

    try:
        # delete folder
        if platform == "win32":
            command = f'rmdir /S /Q "{os.path.join(src_path, sub_folder)}"'
        else:
            command = f'rm -rf "{os.path.join(src_path, sub_folder)}"'

        _statusMessage = command
        _progressLines = []
        socketio.emit("state", get_state().json, broadcast=True)

        proc = Popen(command, shell=True, stdout=PIPE)
        for msg in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
            msg = msg.replace('\t', '  ').replace('\n', '')
            _progressLines.append(msg)
            time.sleep(0.001)

        _statusMessage = f"{command}. Done!"

    except Exception as e:
        _statusMessage = f"An error occurred: {str(e)}"

    finally:
        _lock.release()
        update_subfolders()
    
    return get_state().json


@socketio.on("connect")
def connect():
    print("socket connected")
    update_subfolders()
    socketio.emit("state", get_state().json, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
