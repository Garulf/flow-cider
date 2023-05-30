from dataclasses import dataclass
from typing import Dict, Optional
import json
import time
import websocket
import logging


from ._responses.base_response import BaseResponse

logger = logging.getLogger(__name__)

SCHEMA = "ws"


class WebSocket:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._ws = websocket.WebSocket()

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._disconnect()

    @property
    def _url(self) -> str:
        return f"{SCHEMA}://{self.host}:{self.port}"

    def _connect(self) -> None:
        logger.debug(f"Connecting to {self._url}")
        self._ws.connect(self._url)

    def _disconnect(self) -> None:
        logger.debug(f"Disconnecting from {self._url}")
        self._ws.close()

    def send(self, message: Dict, response_type: Optional[str] = None, timeout: int = 10) -> Dict:
        logger.debug(f"Sending message {message}")
        try:
            self._connect()
            self._ws.send(json.dumps(message))
            start = time.time()
            while True:
                response = json.loads(self._ws.recv())
                if response["type"] == response_type or response_type is None:
                    logger.debug(f"Received response {response}")
                    break
                if time.time() - start > timeout:
                    raise TimeoutError("Timed out waiting for response")
                time.sleep(0.1)
            self._disconnect()
            return response
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            self._disconnect()

    def action(self, action: str, status: str = "generic", **kwargs) -> Dict:
        message = {"action": action, "status": status, **kwargs}
        self._ws.send(message)
        while True:
            response = json.loads(self._ws.recv())
            if response["type"] == status:
                break
        return response
