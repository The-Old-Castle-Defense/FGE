import os
import traceback
import datetime
import io
import threading

from flask import Flask, request, render_template, send_from_directory, send_file
from PIL import Image, ImageDraw, ImageFont

from pinata import Pinata
from the_graph import TheGraph
from db import db
from config import config

config.init_config()
db.connect_to_database(path=config.connectionString)
the_graph = TheGraph(config.config['the_graph_rpc'])


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    return app


app = create_app()
pinata = Pinata(config.config['PINATA_BEARER'])


def parse_event_data(_event, data):
    print(data)
    if _event == "buyAttacks":
        _headers = ["Player", "Team", "Staked $DEGEN", "Attack"]
        _data = [
            [f"{_x['player'][0:4]}...{_x['player'][-4:]}",
             "👻Terrible" if _x['teamId'] == 0 else "🏰 Knights",
             "{0:,.0f} $DEGEN".format(float(int(_x['investedAmount']) / 1e18)),
             "{0:,.0f}".format(float(_x['attackValue']))
             ] for _x in data[_event]]
    elif _event == "siegeRewards":
        _headers = ["Player", "Team", "Reward $DEGEN", "Type"]
        _data = [
            [f"{_x['player'][0:4]}...{_x['player'][-4:]}",
             "👻Terrible" if _x['teamId'] == 0 else "🏰 Knights",
             "{0:,.0f} $DEGEN".format(float(int(_x['rewardAmount']) / 1e18)),
             "NFT" if _x['rewartType'] == 1 else "$ DEGEN Staking"
             ] for _x in data[_event]]
    return _headers, _data
    # TODO Parse all the events SC has


def create_image(frame, fid=None, width=800, height=418, deploy_id="3", siege_id=None):
    text_array = frame['image']
    if not text_array:
        return
    # Create an image with white background
    image = Image.new('RGB', (width, height), 'white')
    if len(text_array[0]) == 1 and os.path.exists(f'static/images/{text_array[0][0]}'):
        overlay_image = Image.open(f'static/images/{text_array[0][0]}')
        # Optionally resize or manipulate overlay_image here
        image_position = (0, 0)
        image.paste(overlay_image, image_position)

    draw = ImageDraw.Draw(image)
    # Load a font
    point_to_pixels = 1.33
    font_path = "fonts/Montserrat-Bold.ttf"

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


def return_frame(_frame, userFid=0, add_args=""):
    return render_template(
        "main_frame.html",
        title=_frame['title'],
        image=f"{_frame['_id']}?fid={userFid}{add_args}",
        text_placeholder=_frame['text_placeholder'],
        buttons=_frame['buttons'],
        post_url=_frame['next_url']
    )


# #################################### EVENTS Stream Frame #################################### #

@app.route('/events/<string:_action>', methods=['POST'])
def events_txs(_action=None):
    _args = request.args
    _json = request.json
    siege_id = _args.get('siege_id')
    userFid = _json['untrustedData']['fid']
    tx_hash = _json['untrustedData'].get('transactionId')
    buttonIndex = _json['untrustedData']['buttonIndex']
    input_text = _json['untrustedData'].get("inputText", "").strip()
    _frame = db.db.frames.find_one({"_id": _action})
    threading.Thread(target=pinata.send_analytics, args=(userFid, _json, _frame['event_type'],)).start()
    return return_frame(_frame, userFid, f"&event={input_text}&type=events")


@app.route('/image/<string:name>', methods=['GET'])
def image(name):
    try:
        args = request.args
        fid = args.get("fid")
        siege_id = args.get("siege_id")
        _frame = db.db.frames.find_one({"_id": name})
        if not _frame:
            return send_from_directory("static/images/", name)
        elif args.get("type", "") == "events" or name == "events":
            image_bytes = create_events_image(_frame, fid, args=args)
            return send_file(image_bytes, mimetype='image/png')
        else:
            if len(_frame['image']) == 1:
                return send_from_directory("static/images/", _frame['image'][0][0])
            image_bytes = create_image(_frame, fid, siege_id=siege_id)
            return send_file(image_bytes, mimetype='image/png')
    except Exception as exc:
        traceback.print_exc()
        return None


def create_events_image(frame, fid=None, width=800, height=418, args={}):
    text_array = frame['image']

    _image_name = frame['image'][0][0]
    image = Image.new('RGB', (width, height), 'white')
    if len(text_array[0]) == 1 and os.path.exists(f'static/images/{_image_name}'):
        overlay_image = Image.open(f'static/images/{_image_name}')
        # Optionally resize or manipulate overlay_image here
        image_position = (0, 0)
        image.paste(overlay_image, image_position)

    draw = ImageDraw.Draw(image)
    # Load a font
    point_to_pixels = 1.33
    font_path = "fonts/Montserrat-Bold.ttf"
    bold = ImageFont.truetype(font=font_path, size=int(38 * point_to_pixels))

    if frame['_id'] == "events":
        diff_height = 52
        diff_width = 220

        start_x, start_y = 50, 240

        count = 0

        for _k in config.GRAPH_QL_EVENTS.keys():
            # Calculate x, y position
            x = start_x + (count % 2) * diff_width
            y = start_y + (count // 2) * diff_height
            print(x, y)

            # Draw the currency key
            draw.text(
                (x, y),
                _k,
                fill="#FFFFFF",
                font=ImageFont.truetype(font_path, int(int(16) * point_to_pixels))
            )
            count += 1


    elif frame['_id'] == "events_txs":
        _event = args.get("event", "buyAttacks")
        if _event not in config.GRAPH_QL_EVENTS.keys():
            _event = list(config.GRAPH_QL_EVENTS.keys())[0]

        draw.text(
            (281, 36),
            _event,
            fill="#FF33F6",
            font=ImageFont.truetype(font_path, int(int(20) * point_to_pixels))
        )

        _events = get_graph_events(_event)
        _headers, _data = parse_event_data(_event, _events)
        diff_height = 54
        diff_width = 180

        start_x, start_y = 50, 107

        count = 0

        print(_data)
        for _item in _data[:5]:
            for _header, _v in zip(_headers, _item):
                # Calculate x, y position
                x = start_x + (count % 4) * diff_width
                y = start_y + (count // 4) * diff_height

                # Draw the currency key
                draw.text(
                    (x, y),
                    _header,
                    fill="#9191B0",
                    font=ImageFont.truetype(font_path, int(int(12) * point_to_pixels))
                )

                # Draw the balance value
                draw.text(
                    (x, y + 21),  # 25 is the difference in y for the value to be below the key
                    str(_v),
                    fill="#FFFFFF",
                    font=ImageFont.truetype(font_path, int(int(12) * point_to_pixels))
                )

                count += 1

    # Save image to a bytes buffer
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr


def get_graph_events(_event):
    _events = db.db.storage.find_one({"type": "the_graph", "event": _event})

    if not _events or _events['updated_at'] < (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)):
        print("NO EVENT DATA", _event)
        _events = the_graph.query(_event, config.GRAPH_QL_EVENTS[_event])
        if _event not in str(_events):
            _events = get_graph_events(_event)
        _events_to_add = _events.copy()
        _events_to_add['type'] = "the_graph"
        _events_to_add['updated_at'] = datetime.datetime.utcnow()
        _events_to_add = config.formatNestedDict(_events_to_add, to_decimals=False, to_string=True)
        db.db.storage.update_one(
            {"type": "the_graph", "event": _event},
            {"$set": _events_to_add}, upsert=True
        )
    _events = config.formatNestedDict(_events, to_decimals=True, to_string=False)
    return _events


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
    # app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config["CACHE_TYPE"] = "null"
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
