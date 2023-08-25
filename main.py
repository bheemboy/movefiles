import os
from flask import Flask, render_template, request, jsonify

paths = ["/mnt/tank/dev/images/lenovo", "/mnt/tank/qa/images/lenovo", "/mnt/tank/released/images/lenovo"]

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_paths")
def get_paths():
    return jsonify(paths)


@app.route("/get_subfolders")
def get_subfolders():
    return jsonify([os.listdir(path) for path in paths])


@app.route("/copy_folder")
def copy_folder():
    src_path = request.args.get("src_path")
    sub_folder = request.args.get("sub_folder")
    dest_path = request.args.get("dest_path")

    try:
        # copy subfolder
        cmd = f"rsync -r -v {os.path.join(src_path, sub_folder)} {os.path.join(dest_path, sub_folder)}"
        print (cmd)
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
