import json
import logging
import logstash
import urllib

from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from datetime import datetime
from logging.config import dictConfig
from uuid import uuid4

dictConfig({
    'version': 1,
    'root': {
        'handlers': ['console', 'logstash'],
        'level': 'INFO',
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'localhost',
            'port': 49160,
            'version': 1,
            'message_type': 'logstash',
            'fqdn': False,
            'tags': [
                'panacea_mock',
            ],
        },
    },
})

logger = logging.getLogger(__name__)

messages = [
    {
        "id": 11290358,
        "created": datetime.now().isoformat(),
        "from": "+27761421248",
        "to": "53193334",
        "data": "Test",
        "charset": "UTF-8",
    },
]

messages_get_response = {
    "status": 0,
    "message": "OK",
    "details": messages,
}

messages_send_response = {
    "status": 1,
    "message": "Sent",
    "details": str(uuid4()),
}

no_such_action_response = {
    "status": -2,
    "message": "No such action",
}


class SimpleHandler(BaseHTTPRequestHandler):
    def get_data(self):
        request_string = self.path.split("/")[-1].strip("?")
        get_vars = [var.split("=") for var in request_string.split("&")]
        data = dict(get_vars)
        return data

    def do_GET(self):
        data = self.get_data()

        self.send_response(200, "OK")
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if data['action'] == 'messages_get':
            self.wfile.write(json.dumps(messages_get_response))
        elif data['action'] == 'message_send':
            text = urllib.unquote(data['text'])
            text = text.replace('+', ' ')
            logger.info('Fake sending message: \n\n%s', text)
            self.wfile.write(json.dumps(messages_send_response))
        else:
            self.wfile.write(json.dumps(no_such_action_response))

        self.wfile.close()


server_address = ('', 49170)

httpd = HTTPServer(server_address, SimpleHandler)
httpd.serve_forever()
