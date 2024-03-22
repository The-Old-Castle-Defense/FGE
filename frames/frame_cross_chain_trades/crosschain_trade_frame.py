import os
import traceback
import requests
import io
import threading

from flask import Flask, request, render_template, send_from_directory, send_file
from PIL import Image, ImageDraw, ImageFont

from pinata import Pinata

from db import db
from config import config
config.init_config()
from api import evm_api, evm_apis
TOKENS_LIST = {}
evm_api.init(8453, config.chains)
for _k, _v in config.chains.items():
    evm_apis[_k].init(int(_k), config.chains)
    TOKENS_LIST[_k] = requests.get(f"https://deswap.debridge.finance/v1.0/token-list?chainId={_k}").json()['tokens']

db.connect_to_database(path=config.connectionString)

BATCH_BALANCES = {
    "BASE": {"id": "8453", "batch_sc": "0x202eF28cA6D4d2B94C4Ea0534a8E6261581c70a4"},
    "OP": {"id": "10", "batch_sc": "0x55C93b20Dd2F790AC429D6341a022A781791654A"}
}

BATCH_CONTRACTS = {_v['id']: evm_apis[_v['id']].get_contract(_v['batch_sc'], config.ABIs['batchBalance']) for _k, _v in BATCH_BALANCES.items()}
DEGEN_TOKEN = "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed"



pinata = Pinata(config.config['PINATA_BEARER'])

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    return app

app = create_app()


@app.route('/robots.txt', methods=['GET'])
def robots():
    return {}


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


def get_parse_input(input_text):
    if ";" in str(input_text):
        _data = input_text.strip().split(";") if input_text else None
    elif " " in str(input_text):
        _data = input_text.strip().split(" ") if input_text else None
    else:
        _data = []
    return _data

@app.route('/tx/<string:_action>', methods=['POST'])
def tx(_action=None):
    try:
        _args = request.args
        _json = request.json

        input_text = _json['untrustedData'].get("inputText")
        userFid = _json['untrustedData']['fid']

        _data = get_parse_input(input_text)

        token_contract = evm_api.get_contract(DEGEN_TOKEN, config.ABIs['token'])
        _token_decimals = token_contract.functions.decimals().call()

        if _action == "deswap":
            _token_chain = _args['tc']
            _token, _chain = _token_chain.split(':')
            token_from_contract = [[evm_api.w3.to_checksum_address(_x['address']), 10**int(_x['decimals'])] for _x in TOKENS_LIST[BATCH_BALANCES[_chain]['id']].values() if _x['symbol'] == _token][0]
            amount = int(float(_args['amount']) * token_from_contract[1])
            _address = _args['address']
            default_blockchain = "8453"
            print(_token_chain, _token, _chain, amount)

            if str(BATCH_BALANCES[_chain]['id']) == default_blockchain:
                URI = f"https://api.dln.trade/v1.0/chain/transaction?chainId={default_blockchain}&tokenIn={token_from_contract[0]}&tokenInAmount={amount}&slippage=1&tokenOut={DEGEN_TOKEN}&tokenOutRecipient={_address}"
            else:
                URI = f"https://deswap.debridge.finance/v1.0/dln/order/create-tx?srcChainId={BATCH_BALANCES[_chain]['id']}&srcChainTokenIn={token_from_contract[0]}&srcChainTokenInAmount={amount}&dstChainId={default_blockchain}&dstChainTokenOut={DEGEN_TOKEN}&dstChainTokenOutRecipient={_address}&senderAddress={_address}&srcChainOrderAuthorityAddress={_address}&referralCode=84&srcChainRefundAddress={_address}&dstChainOrderAuthorityAddress={_address}&enableEstimate=false&prependOperatingExpenses=false&additionalTakerRewardBps=0&deBridgeApp=DESWAP&otc=false"
            print(URI)
            _deswap_r = requests.get(URI).json()
            print(_deswap_r)
            value = str(amount) if "0x0000000000000000000" in token_from_contract[0] else "0"
            value = int(value) + int(_deswap_r['fixFee']) if _deswap_r.get('fixFee') else value

            _allowance_addr = evm_api.w3.to_checksum_address(_deswap_r['tx'].get('allowanceTarget', _deswap_r['tx'].get('to')))
            token_contract = evm_apis[BATCH_BALANCES[_chain]['id']].get_contract(token_from_contract[0], config.ABIs['token'])
            if "0x0000000000000000000" not in token_from_contract[0] and _deswap_r.get('tx', {}):

                _allowance = token_contract.functions.allowance(_address, _allowance_addr).call()
                print(f"Address Allowance is {_allowance/ (10**_token_decimals)}")
                if _allowance < amount:
                    txn = token_contract.encodeABI(
                        fn_name="approve",
                        args=[_allowance_addr, amount]
                    )
                    return return_frame_tx(
                        chain_id=BATCH_BALANCES[_chain]['id'],
                        method="eth_sendTransaction",
                        params={
                            "abi": ["function approve(address spender, uint256 amount)"],
                            "to": token_from_contract[0],
                            "data": txn,
                            "value": "0",
                        },
                    )

            abi_method = "function swap(address inputToken, address outputToken, uint256 inputAmount, uint256 outputAmount, uint256 goodUntil, address destinationAddress, Signature calldata theSignature, bytes calldata auxiliaryData)" if str(BATCH_BALANCES[_chain]['id']) == default_blockchain else "function createSaltedOrder(DlnOrderLib.OrderCreation calldata _orderCreation, uint64 _salt, bytes calldata _affiliateFee, uint32 _referralCode, bytes calldata _permitEnvelope, bytes memory _metadata) payable"

            return return_frame_tx(
                BATCH_BALANCES[_chain]['id'],
                "eth_sendTransaction",
                params={
                    "abi": [abi_method],
                    "to": _allowance_addr,
                    "data": _deswap_r['tx']['data'],
                    "value": str(value),
                },
            )

        return {}
    except Exception as exc:
        traceback.print_exc()

def return_frame_tx(chain_id, method, params):
    return {
          "chainId": f"eip155:{chain_id}",
          "method": method,
          "params": params,
        }

def return_frame(_frame, userFid=0, add_args=""):
    return render_template(
        "main_frame.html",
        title=_frame['title'],
        image=f"{_frame['_id']}?fid={userFid}{add_args}",
        text_placeholder=_frame['text_placeholder'],
        buttons=_frame['buttons'],
        post_url=_frame['next_url']
    )


# #################################### BUY $DEGEN CROSS-CHAIN Frame #################################### #

@app.route('/buy_degen', methods=['POST'])
@app.route('/buy_degen/<string:_action>', methods=['POST'])
def buy_degen_frame(_action=None):
    _json = request.json
    print(request.json)
    _args = request.args

    userFid = _json['untrustedData']['fid']
    tx_hash = _json['untrustedData'].get('transactionId')
    input_text = _json['untrustedData'].get("inputText", "").strip()
    _frame = db.db.frames.find_one({"_id": _action})
    threading.Thread(target=pinata.send_analytics, args=(userFid, _json, _frame['event_type'],)).start()

    if not _frame:
        return

    if tx_hash:
        return return_frame({"title": _frame['title'], "_id": f"buy_degen_success.png", "buttons": [["🏆Rewards", "post", f"https://frame.theoldcastle.xyz/mystake?fid={userFid}"]], "next_url": f"https://frame.theoldcastle.xyz/mystake?fid={userFid}", "text_placeholder": ""}, userFid)

    try:

        if _action == "buy_degen_balances":
            try:
                address = evm_api.w3.to_checksum_address(input_text)
            except Exception as exc:
                print(exc)
                address = get_verified_address(userFid)
            _frame['next_url'] += f"?fid={userFid}&address={address}"
            return return_frame(_frame, userFid, f"&type=balances&address={input_text}")
        if _action == "buy_degen_address":
            return return_frame(_frame, userFid)
        elif _action == "buy_degen_confirm":
            if " " in input_text:
                _split = input_text.split(" ")
            elif ";" in input_text:
                _split = input_text.split(";" )
            else:
                return 404

            _token_chain = _split[1]
            amount = float(_split[0])
            address = _args['address']
            print("RETURN CUSTOM")

            return return_frame({"title": "Buy $DEGEN Cross-Chain From Any Token Any Chain", "_id": f"buy_degen_confirm", "buttons": [["🏆Swap", "tx", f"https://frame.theoldcastle.xyz/tx/deswap?fid={userFid}&tc={_token_chain}&amount={amount}&address={address}"]], "next_url": f"https://frame.theoldcastle.xyz/buy_degen?fid={userFid}&tc={_token_chain}&amount={amount}", "text_placeholder": ""}, userFid, f"&tc={_token_chain}&amount={amount}&type=swap_confirm&address={address}")

    except Exception as exc:
        traceback.print_exc()
        return None


@app.route('/image/<string:name>', methods=['GET'])
def image(name):
    try:
        args = request.args
        fid = args.get("fid")
        siege_id = args.get("siege_id")
        _frame = db.db.frames.find_one({"_id": name})
        if not _frame:
            return send_from_directory("static/images/", name)
        elif args.get("type", "") == "balances" or args.get("type", "") == "swap_confirm":
            image_bytes = create_balances_image(_frame, fid, args=args)
            return send_file(image_bytes, mimetype='image/png')
        else:
            if len(_frame['image']) == 1:
                return send_from_directory("static/images/", _frame['image'][0][0].split("?")[0])
            return
    except Exception as exc:
        traceback.print_exc()
        return None

def create_balances_image(frame, fid=None, width=800, height=418, args=None):
    text_array = frame['image']
    # Create an image with white background
    image = Image.new('RGB', (width, height), 'white')
    _image_name = frame['image'][0][0].split("?")[0]
    if len(text_array[0]) == 1 and os.path.exists(f'static/images/{_image_name}'):
        overlay_image = Image.open(f'static/images/{_image_name}')
        # Optionally resize or manipulate overlay_image here
        image_position = (0, 0)
        image.paste(overlay_image, image_position)

    draw = ImageDraw.Draw(image)
    # Load a font
    point_to_pixels = 1.33
    font_path = "../telegram_bot/fonts/Montserrat-Bold.ttf"
    bold = ImageFont.truetype(font=font_path, size=int(38 * point_to_pixels))

    if frame['_id'] == "buy_degen_balances":
        _address = args.get("address")
        _balances = get_user_balances(fid, address=_address)
        diff_height = 62
        diff_width = 150

        start_x, start_y = 50, 198

        count = 0

        for _k, _v in _balances.items():

            # Calculate x, y position
            x = start_x + (count % 3) * diff_width
            y = start_y + (count // 3) * diff_height

            # Draw the currency key
            draw.text(
                (x, y),
                str(_k),
                fill="#9191B0",
                font=ImageFont.truetype(font_path, int(int(14) * point_to_pixels))
            )

            # Draw the balance value
            draw.text(
                (x, y + 25),  # 25 is the difference in y for the value to be below the key
                "{:,.2f}".format(_v),
                fill="#FFFFFF",
                font=ImageFont.truetype(font_path, int(int(14) * point_to_pixels))
            )

            count += 1
    elif frame['_id'] == "buy_degen_confirm":
        print(args)
        _balances = get_user_balances(fid)
        _token_chain = args['tc']
        _token, _chain = _token_chain.split(':')
        token_from_contract = [[evm_api.w3.to_checksum_address(_x['address']), 10**int(_x['decimals'])] for _x in TOKENS_LIST[BATCH_BALANCES[_chain]['id']].values() if _x['symbol'] == _token][0]
        amount = int(float(args['amount']) * token_from_contract[1])
        print(_token_chain, _token, _chain, amount)
        _address = get_verified_address(fid)
        default_blockchain = "8453"

        _balances = get_user_balances(fid)
        if str(BATCH_BALANCES[_chain]['id']) == default_blockchain:
            URI = f"https://api.dln.trade/v1.0/chain/transaction?chainId={default_blockchain}&tokenIn={token_from_contract[0]}&tokenInAmount={amount}&slippage=1&tokenOut={DEGEN_TOKEN}&tokenOutRecipient={_address}"
        else:
            URI = f"https://deswap.debridge.finance/v1.0/dln/order/quote?srcChainId={BATCH_BALANCES[_chain]['id']}&srcChainTokenIn={token_from_contract[0]}&srcChainTokenInAmount={amount}&dstChainTokenOutAmount=auto&dstChainId={default_blockchain}&dstChainTokenOut={DEGEN_TOKEN}&prependOperatingExpenses=false&additionalTakerRewardBps=0"
        print(URI)
        _deswap_r = requests.get(URI).json()
        if "Internal error" in str(_deswap_r):
            _deswap_r = requests.get(URI).json()
        print(_deswap_r)
        if _deswap_r.get('estimation'):
            _deswap_r = _deswap_r['estimation']
            _from_token = _deswap_r['srcChainTokenIn']['symbol']
            _to_token = _deswap_r['dstChainTokenOut']['symbol']
            _from_amount = int(_deswap_r['srcChainTokenIn']['amount']) / (10**_deswap_r['srcChainTokenIn']['decimals'])
            _to_amount = int(_deswap_r['dstChainTokenOut']['amount']) / (10**_deswap_r['dstChainTokenOut']['decimals'])
            _from_chain = [_k for _k, _x in BATCH_BALANCES.items() if int(_x['id']) == _deswap_r['srcChainTokenIn']['chainId']][0]
            _to_chain = [_k for _k, _x in BATCH_BALANCES.items() if int(_x['id']) == _deswap_r['dstChainTokenOut']['chainId']][0]
        else:
            _from_token = _deswap_r['tokenIn']['symbol']
            _to_token = _deswap_r['tokenOut']['symbol']
            _from_amount = int(_deswap_r['tokenIn']['amount']) / (10**_deswap_r['tokenIn']['decimals'])
            _to_amount = int(_deswap_r['tokenOut']['amount']) / (10**_deswap_r['tokenOut']['decimals'])
            _from_chain = [_k for _k, _x in BATCH_BALANCES.items() if str(_x['id']) == default_blockchain][0]
            _to_chain = [_k for _k, _x in BATCH_BALANCES.items() if str(_x['id']) == default_blockchain][0]


        draw.text(
            (80, 269),  # 25 is the difference in y for the value to be below the key
            f"{_from_token}({_from_chain})",
            fill="#FFFFFF",
            font=ImageFont.truetype(font_path, int(int(14) * point_to_pixels))
        )

        draw.text(
            (435, 269),
            f"{_to_token}({_to_chain})",
            fill="#FFFFFF",
            font=ImageFont.truetype(font_path, int(int(14) * point_to_pixels))
        )

        draw.text(
            (80, 296),
            "{:,.2f}".format(_from_amount),
            fill="#FFFFFF",
            font=ImageFont.truetype(font_path, int(int(22) * point_to_pixels))
        )
        draw.text(
            (435, 296),
            "{:,.2f}".format(_to_amount),
            fill="#FFFFFF",
            font=ImageFont.truetype(font_path, int(int(22) * point_to_pixels))
        )



    # Save image to a bytes buffer
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr

def get_user_balances(fid, address=None):
    _address = get_verified_address(fid) if not address else address
    balances = {}

    for _chain, _chain_data in BATCH_BALANCES.items():
        try:
            _tokens = [evm_api.w3.to_checksum_address(_x) for _x in list(TOKENS_LIST[_chain_data['id']].keys())[1:20]]
            _balances = BATCH_CONTRACTS[_chain_data['id']].functions.balanceFor(_tokens, _address).call()
            count = 0
            for _tc, _td in list(TOKENS_LIST[_chain_data['id']].items())[:20]: # tc - token contract; td - token data
                if _tc == "0x0000000000000000000000000000000000000000":
                    eth_balance = evm_apis[_chain_data['id']].getaddressbalance(_address)
                    balances[f"{_td['symbol']}:{_chain}"] = eth_balance
                    continue
                if _balances[0][count] > 100000:
                    balances[f"{_td['symbol']}:{_chain}"] = float(_balances[0][count]/(10**_balances[1][count]))
                count += 1
        except Exception as exc:
            print(exc)
            traceback.print_exc()
    balances = sorted(balances.items(), key=lambda item: item[1], reverse=True)
    print(balances)
    return balances


@app.route('/frame/<string:event_type>', methods=['GET', 'POST'])
def frame(event_type):
    try:
        _frame = db.db.frames.find_one({"event_type": event_type})
        return render_template(
            "main_frame.html",
            title=_frame['title'],
            image=f"{_frame['_id']}",
            buttons=_frame['buttons'],
            post_url=_frame['next_url']
        )
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
    port = 15000
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config["CACHE_TYPE"] = "null"
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()
