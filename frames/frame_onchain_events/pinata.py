import requests


class Pinata:

    def __init__(self, bearer_token):
        self.bearer = bearer_token

    def post(self, path, json=None):
        response = requests.post(
            f"https://api.pinata.cloud{path}",
            headers={"Authorization": f"Bearer {self.bearer}", "Content-Type": "application/json"},
            json=json
        )
        if response.status_code == 200:
            try:
                response = response.json()
            except Exception:
                response = response.content
        else:
            raise Exception(response.content)
        return response

    def get(self, path, params=None):
        response = requests.get(
            f"https://api.pinata.cloud{path}",
            headers={"Authorization": f"Bearer {self.bearer}", "Content-Type": "application/json"},
            params=params
        )
        if response.status_code == 200:
            try:
                response = response.json()
            except Exception:
                response = response.content
        else:
            raise Exception(response.content)
        return response


    def send_analytics(self, custom_id, frame_data, frame_id):
        try:
            r = self.post("/farcaster/frames/interactions", json={"custom_id": str(custom_id), "data": frame_data, "frame_id": frame_id})
            return r
        except Exception as exc:
            print(exc)

    def get_interactions(self, start_date, end_date, frame_id=None, button_index=None, url=None, custom_id=None):
        try:
            params = {"start_date": start_date, "end_date": end_date}
            if frame_id:
                params.update({"channel": frame_id})
            if button_index:
                params.update({"channel": button_index})
            if url:
                params.update({"channel": url})
            if custom_id:
                params.update({"channel": custom_id})

            r = self.get(f"/farcaster/frames/interactions")
            return r
        except Exception as exc:
            print(exc)

    def cast_by_hash(self, cast_hash):
        try:
            r = self.get(f"/v3/farcaster/casts/{cast_hash}")
            return r
        except Exception as exc:
            print(exc)

    def casts(self, fid, following=True, channel=None, parent_hash=None, page_size=100, page=1):
        try:
            params = {"fid": fid, "following": following, "pageSize": page_size, "pageToken": page}
            if channel:
                params.update({"channel": channel})

            if parent_hash:
                params.update({"parentHash": parent_hash})

            r = self.get(f"/v3/farcaster/casts", params=params)
            return r
        except Exception as exc:
            print(exc)

    def user_by_fid(self, fid):
        """
        Response Example:
        {
          "data": {
            "bio": "Writer. Building @pinatacloud. Tinkering with a Farcaster native alternative to GoodReads: https://readcast.xyz \\ https://polluterofminds.com",
            "custody_address": "0x7f9a6992a54dc2f23f1105921715bd61811e5b71",
            "display_name": "Justin Hunter",
            "fid": 4823,
            "follower_count": 11049,
            "following_count": 811,
            "pfp_url": "https://i.seadn.io/gae/lhGgt7yK1JiBVYz_HBxcAmYLRtP03aw5xKX4FgmFT9Ai7kLD5egzlLvb0lkuRNl28shtjr07DC8IHzLUkTqlWUMndUzC9R5_MSxH3g?w=500&auto=format",
            "recovery_address": "0x00000000fcb080a4d6c39a9354da9eb9bc104cd7",
            "username": "polluterofminds",
            "verifications": [
              "0x1612c6dff0eb5811108b709a30d8150495ce9cc5",
              "0xcdcdc174901b12e87cc82471a2a2bd6181c89392"
            ]
          }
        }
        """

        try:
            r = self.get(f"/v3/farcaster/users/{fid}")
            return r
        except Exception as exc:
            print(exc)

    def users(self):
        """
        Response Example:
            {
              "data": {
                "next_page_token": "eyJvZmZzZXQiOiIyIn0",
                "users": [
                  {
                    "bio": "Technowatermelon. Elder Millenial. Building Farcaster. \n\nnf.td/varun",
                    "custody_address": "0x4114e33eb831858649ea3702e1c9a2db3f626446",
                    "display_name": "Varun Srinivasan",
                    "fid": 2,
                    "follower_count": 150650,
                    "following_count": 1138,
                    "pfp_url": "https://i.seadn.io/gae/sYAr036bd0bRpj7OX6B-F-MqLGznVkK3--DSneL_BT5GX4NZJ3Zu91PgjpD9-xuVJtHq0qirJfPZeMKrahz8Us2Tj_X8qdNPYC-imqs?w=500&auto=format",
                    "recovery_address": "0x00000000fcb080a4d6c39a9354da9eb9bc104cd7",
                    "username": "v",
                    "verifications": [
                      "0x182327170fc284caaa5b1bc3e3878233f529d741",
                      "0x83f7335253bfaf321de49f25f6fd67fa8f1d0665b4cab33f67f7e4341bfd91d0",
                      "0x91031dcfdea024b4d51e775486111d2b2a715871",
                      "0x91701714719f1388e7f5cf8156b7bcdf001e5dcd1354151488959fdf343caff5",
                      "0xf86a7a5b7c703b1fd8d93c500ac4cc75b67477f0"
                    ]
                  }
                ]
              }
            }

        """

        try:
            r = self.get(f"/v3/farcaster/users")
            return r
        except Exception as exc:
            print(exc)

