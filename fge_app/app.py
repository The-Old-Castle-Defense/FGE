import os
import traceback
import requests
import io
import threading

from flask import Flask, request, render_template, send_from_directory, send_file
from PIL import Image, ImageDraw, ImageFont

from db import db
from config import config
from the_graph import TheGraph
from pinata import Pinata

config.init_config()
db.connect_to_database(path=config.connectionString)

from api import evm_api, evm_apis
evm_api.init(8453, config.chains)

the_graph = TheGraph(config.config['the_graph_rpc'])
pinata = Pinata(config.config['PINATA_BEARER'])


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    return app


app = create_app()


@app.route('/robots.txt', methods=['GET'])
def robots():
    return {}


def create_image(frame, width=800, height=418):
    text_array = frame['image']

    if "http" not in str(text_array[0][0]):
        return send_from_directory("static/images/", frame['image'][0][0])

    if not text_array:
        return

    response = requests.get(frame['image'][0][0])
    image_bytes = io.BytesIO(response.content)

    # Create an image with white background
    image = Image.new('RGB', (width, height), 'white')
    overlay_image = Image.open(image_bytes)
    # Optionally resize or manipulate overlay_image here
    image_position = (0, 0)
    image.paste(overlay_image, image_position)

    draw = ImageDraw.Draw(image)
    # Load a font
    point_to_pixels = 1.33
    font_path = "/fonts/Montserrat-Bold.ttf"

    # Insert Text
    for _text in text_array:
        if len(_text) > 2:
            draw.text(
                (_text[0], _text[1]),
                str(_text[2]),
                fill=_text[3],
                font=ImageFont.truetype(font_path, int(int(_text[4]) * point_to_pixels))
            )

    # Save image to a bytes buffer
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr


def get_verified_address(user_fid):
    try:
        _user_data = pinata.user_by_fid(user_fid)['data']
        if len(_user_data.get("verifications", [])) > 0:
            ver_addr = [evm_api.w3.to_checksum_address(_x) for _x in _user_data["verifications"] if "0x" == _x[0:2]]
            ver_addr = ver_addr[0] if ver_addr else None
        else:
            ver_addr = None
    except:
        traceback.print_exc()
        ver_addr = None
    print(f"Verified Address of the User {user_fid} - {ver_addr}")
    return ver_addr


def return_frame(_frame, userFid=0, add_args=""):
    return render_template(
        "main_frame.html",
        title=_frame['title'],
        image=f"{_frame['_id']}?fid={userFid}{add_args}",
        text_placeholder=_frame['text_placeholder'],
        buttons=_frame['buttons'],
        post_url=_frame['next_url']
    )

@app.route('/api/next/<string:_action>', methods=['POST'])
def next_frame(_action=None):
    try:
        _json = request.json
        print(request.json)
        _redirect = request.args.get("redirect")

        _btn_actions = {
            '1': request.args.get("btn_1"),
            '2': request.args.get("btn_2"),
            '3': request.args.get("btn_3"),
            '4': request.args.get("btn_4")
        }

        buttonIndex = _json['untrustedData']['buttonIndex']
        input_text = _json['untrustedData'].get("inputText")
        userFid = _json['untrustedData']['fid']

        if _btn_actions[buttonIndex]:
            _frame = db.db.frames.find_one({"_id": _btn_actions[buttonIndex]})
            if not _frame:
                return
            threading.Thread(target=pinata.send_analytics, args=(userFid, _json, _frame['event_type'],)).start()
            return return_frame(_frame, userFid)

        _frame = db.db.frames.find_one({"_id": _action})
        if not _frame:
            print("FRAME DOESN'T NOT EXIST")
            return

        threading.Thread(target=pinata.send_analytics, args=(userFid, _json, _frame['event_type'],)).start()

        return return_frame(_frame, userFid)

    except Exception as exc:
        traceback.print_exc()
        return None


@app.route('/image/<string:name>', methods=['GET'])
def image(name):
    try:
        args = request.args
        _frame = db.db.frames.find_one({"_id": name})
        image_bytes = create_image(_frame)
        return send_file(image_bytes, mimetype='image/png')
    except Exception as exc:
        traceback.print_exc()
        return None

@app.route('/frame/<string:event_type>', methods=['GET', 'POST'])
def frame(event_type):
    try:
        _frame = db.db.frames.find_one({"event_type": event_type})
        return return_frame(_frame)
    except Exception as exc:
        print(exc)
        traceback.print_exc()


@app.after_request
def add_header(r):
    try:
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Expires"] = "0"
        r.headers["Access-Control-Allow-Headers"] = "Content-Type"
        r.headers["Access-Control-Allow-Methods"] = "GET, POST"
        return r
    except Exception as exc:
        print(exc)
        traceback.print_exc()


def main():
    host = '127.0.0.1'
    port = 10000
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config["CACHE_TYPE"] = "null"
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
