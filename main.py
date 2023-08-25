import os
from sys import platform
from flask import Flask, render_template, request, jsonify

paths = []
if platform == "win32":
    paths = ["C:\\Temp\\mnt\\dev", "C:\\Temp\\mnt\\qa", "C:\\Temp\\mnt\\released"]
else:
    paths = ["/mnt/tank/dev/images/lenovo", "/mnt/tank/qa/images/lenovo", "/mnt/tank/released/images/lenovo"]

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_paths")
def get_paths():
    return jsonify(paths)

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
    subfolders = [[[f, get_size(os.path.join(path, f))] for f in os.listdir(path)] for path in paths]

    return jsonify(subfolders)


@app.route("/copy_folder")
def copy_folder():
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")
    dest_path = request.args.get("dest_path")

    try:
        # copy subfolder
        cmd = f"rsync -r -v {os.path.join(src_path, sub_folder)} {dest_path}"
        # print (cmd)
        os.system(cmd)

        return jsonify({"message": f"{sub_folder} copied successfully to {dest_path}."})

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@app.route("/delete_folder")
def delete_folder():
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")

    try:
        # delete folder
        cmd = f"rm -rf {os.path.join(src_path, sub_folder)}"
        print (cmd)
        os.system(cmd)

        return jsonify({"message": f"{sub_folder} deleted successfully."})

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
