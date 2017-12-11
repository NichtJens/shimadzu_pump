import requests
from xml.etree import ElementTree

headers = {'Content-Type': 'text'}

request_data = {
    "login": "<Login><Mode>0</Mode><Certification><UserID>%s</UserID><Password>%s</Password>"
             "<SessionID/><Result/></Certification></Login>",
    "logout": "<Login><Mode>-1</Mode></Login>",
    "start": "<Event><Method><PumpBT>1</PumpBT></Method></Event>",
    "stop": "<Event><Method><PumpBT>0</PumpBT></Method></Event>",
    "get": "<Method><No>0</No><Pumps></Pumps></Method>",
    "set": "<Method><No>0</No><Pumps><Pump><UnitID>A</UnitID><Usual><%(name)s>%(value).4f</%(name)s></Usual>"
           "</Pump></Pumps></Method>"}

parameters = {"Flow": "Pumps/Pump/Usual/Flow"}


def extract_element(name, response):
    tree = ElementTree.fromstring(response)
    return tree.find(name).text


class ShimadzuCbm20(object):
    def __init__(self, host):
        self.host = host

        self.endpoints = {"login": "http://%s/cgi-bin/Login.cgi" % self.host,
                          "event": "http://%s/cgi-bin/Event.cgi" % self.host,
                          "method": "http://%s/cgi-bin/Method.cgi" % self.host}

    def login(self, user="Admin", password="Admin"):
        login_data = request_data["login"] % (user, password)

        response_text = requests.get(self.endpoints["login"], data=login_data, headers=headers).text

        session_id = extract_element("Certification/SessionID", response_text)

        if not session_id:
            raise ValueError("You are already logged in. Please logout first.")

        return session_id

    def logout(self):
        logout_data = request_data["logout"]
        response_text = requests.get(self.endpoints["login"], data=logout_data, headers=headers).text

    def start(self):
        start_data = request_data["start"]
        response_text = requests.get(self.endpoints["event"], data=start_data, headers=headers).text

    def stop(self):
        stop_data = request_data["stop"]
        response_text = requests.get(self.endpoints["event"], data=stop_data, headers=headers).text

    def set(self, name, value):
        if name not in parameters:
            raise ValueError(
                "Parameter name '%s' not recognized. Available parameters: %s" % (name, list(parameters.keys())))

        set_flow_data = request_data["set"] % {"name": name, "value": value}
        response_text = requests.get(self.endpoints["method"], data=set_flow_data, headers=headers).text

        return extract_element(parameters[name], response_text)

    def get(self, name):
        if name not in parameters:
            raise ValueError(
                "Parameter name '%s' not recognized. Available parameters: %s" % (name, list(parameters.keys())))

        get_data = request_data["get"]
        response_text = requests.get(self.endpoints['method'], data=get_data, headers=headers).text

        return extract_element(parameters[name], response_text)