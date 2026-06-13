import base64

import cv2
import numpy as np
import obsws_python as obs


class OBSCapture:
    def __init__(self, host: str, port: int, password: str, source_name: str):
        self.source_name = source_name
        self.client = obs.ReqClient(host=host, port=port, password=password)

    def grab_frame(self) -> np.ndarray | None:
        resp = self.client.get_source_screenshot(
            self.source_name, "png", 1920, 1080, 80
        )
        if not resp or not resp.image_data:
            return None
        header, encoded = resp.image_data.split(",", 1)
        data = base64.b64decode(encoded)
        arr = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    def close(self):
        self.client.disconnect()
