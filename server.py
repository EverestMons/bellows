"""Flask callback server for CEO escalation responses."""

import queue
import threading
from typing import Optional

from flask import Flask, request, jsonify


class ResponseServer:
    def __init__(self, port: int):
        self.port = port
        self.app = Flask(__name__)
        self._response_queue: queue.Queue = queue.Queue()
        self._thread = None

        @self.app.route("/respond", methods=["POST"])
        def respond():
            data = request.get_json(force=True) or {}
            self._response_queue.put({
                "decision": data.get("decision", ""),
                "instruction": data.get("instruction", ""),
            })
            return jsonify({"status": "ok"}), 200

    def start(self):
        self._thread = threading.Thread(
            target=lambda: self.app.run(
                host="0.0.0.0", port=self.port, use_reloader=False
            ),
            daemon=True,
        )
        self._thread.start()

    def wait_for_response(self, timeout: int = 3600) -> Optional[dict]:
        try:
            return self._response_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        pass  # Daemon thread dies with the process
