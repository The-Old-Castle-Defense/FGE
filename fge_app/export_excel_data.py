from __future__ import print_function

import json
import traceback
import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from db import db
from config import config
from config import bot

config.init_config()
db.connect_to_database(config.connectionString)
bot.init(config.tg_bot_token, config.tg_log_channel)

def main():
    """
    Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    print("AIRDROP")
    update_competitions(client)


def update_competitions(client):
    try:
        sheets = client.open_by_url(config.config['FGE_SPREADSHEET'])
        sheet = sheets.get_worksheet(0)
        values = sheet.get_all_values()
        header = values[0] 
        values = values[1:]
        print(header)
        print(values)

        def format_data(header, values):
            _data = []
            for _x in values:
                _dict = {}
                for _index, _y in enumerate(_x):
                    _dict[header[_index]] = _y
                _data.append(_dict)
            return _data

        _data = format_data(header, values)
        print(_data)
        for _x in _data:
            _x['updated_at'] = datetime.datetime.utcnow()
            _x['follow_check'] = True if _x['follow_check'].lower() == "true" else None
            _x['add_user'] = True if _x['add_user'].lower() == "true" else None
            _x['image'] = json.loads(_x['image']) if _x['image'] else []
            _x['buttons'] = json.loads(_x['buttons']) if _x['buttons'] else []
            _x['buttons_handler'] = json.loads(_x['buttons_handler']) if _x['buttons_handler'] else []

            db.db.frames.update_one(
                {"_id": _x['_id']},
                {"$set": _x}, upsert=True
            )
            print(f"Updated _id: {_x['_id']} with data: {str(_x)}")
        print(f"Updated {len(_data)} items")
    except Exception as exc:
        print(exc)
        traceback.print_exc()



main()
