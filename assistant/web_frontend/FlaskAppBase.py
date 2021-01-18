from flask import Flask, Response, request
import glob


class FlaskAppBase:
    app = None

    def __init__(self, logger):
        self.logger = logger
        self.app = Flask('flaskwrapper')

    def go(self):
        self.logger.log("Flask App Start")
        self.app.run(host='0.0.0.0', port=8888)

    def add_endpoint(self, endpoint=None, end_name=None, handler=None, allowed_methods=['GET']):
        self.app.add_url_rule(endpoint, end_name, handler, methods=allowed_methods)

    def page_main(self):
        return "<html>Work In Progress!</html>"

    def page_details(self):
        out = ""
        for file in glob.glob("./assistant/web_frontend/index.html", recursive=True):
            self.logger.log(file)
            f = open(file, "r")
            data = f.read()
            f.close()
            out = data
        return out

    def prepare_flask_items(self):
        self.add_endpoint("/", "/", self.page_main, ['GET', 'POST'])
        self.add_endpoint("/details", "/details", self.page_details, ['GET'])
