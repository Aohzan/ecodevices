import requests


class ECODEVICE:
    """Class representing the ECODEVICE and its API"""

    def __init__(self, host, port=80):
        self._host = host
        self._port = port
        self._api_url = f"http://{host}:{port}/api/xdevices.json"

    @property
    def host(self):
        return self._host

    def _request(self, params):
        r = requests.get(self._api_url, params=params, timeout=2)
        r.raise_for_status()
        content = r.json()
        product = content.get("product", None)
        if product == "Eco-devices":
            return content
        else:
            raise Exception(
                "Eco-Devices api request error, url: %s`r%s", r.request.url, content,
            )

    def ping(self) -> bool:
        try:
            self._request({"cmd": 10})
            return True
        except:
            pass
        return False

    def get(self, key) -> int:
        """Get value from keys: current_t1, current_t2, daily_c1, daily_c2, total_c1, total_c2"""

        if key == "current_t1":
            return self._request({"cmd": 10}).get("T1_PAPP")
        elif key == "current_t2":
            return self._request({"cmd": 10}).get("T2_PAPP")
        elif key == "daily_c1":
            return self._request({"cmd": 20}).get("Day_C1")
        elif key == "daily_c2":
            return self._request({"cmd": 20}).get("Day_C2")
        elif key == "total_c1":
            return self._request({"cmd": 10}).get("INDEX_C1")
        elif key == "total_c2":
            return self._request({"cmd": 10}).get("INDEX_C2")
        else:
            raise Exception("key not found.")
