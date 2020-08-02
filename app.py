import os
from flask import Flask, redirect
from flask import request
from flask import jsonify
import hashlib

app = Flask(__name__)

c = 0
clients = []
chat = []

#[from, to, status[0sent, 1accepted, 2rejected]]
requests = {}
requests_sent = {}

version = 5

additive = 0
def getUID(ip):
    return hashlib.sha256(str(ip).encode("utf8")).hexdigest()
def getUN(ip):
    return int(str(ip).replace(".", ""))
def addChat(toAdd, limit = True):
    global chat, additive
    if limit:
        additive = additive + 1
    print("new chat: " + toAdd)
    toAdd = toAdd.replace("<script>", "").replace("</script>", "")
    if(additive > 50):
        chat.pop(0)
    chat.append(toAdd)

def addClient(uID):
    if uID not in clients:
        clients.append(uID)
        addChat("--- " + uID + " Joined the Chat ---")
        print("connection from " + str(request.remote_addr))
def removeClient(uID):
    if uID in clients:
        clients.remove(uID)
        addChat("--- " + uID + " Left the Chat ---")
@app.route('/')
def hello():
    global chat, version
    uIp = request.access_route[0]
    uID = getUID(uIp)
    addClient(uID)
    view = "<title>A+</title>"
    global c
    c = c + 1
    view = view + "<h3> Public Chat </h3>"
    view = view + "Connected as: " + uID + " (" + uIp + ")<br \\>"
    view = view + "Refresh the page to access the latest messages."
    view = view + "<br \\>-----------------------------------------------------------------------<br \\>"
    for i in chat:
        view = view + i.replace("<", "").replace(">", "") + "<br \\>"
    view = view + "<br \\>-----------------------------------------------------------------------<br \\>"
    view = view + "note that only the latest 50 messages are stored and displayed. <br \\><br \\>"
    view = view + "<form action=\" " + "/post" + "\" method=\"post\">"
    view = view + "<input type=\"text\" name=\"msg\">"
    view = view + "<input type=\"submit\">"
    view = view + "</form>"
    view = view + "<br \\><hr \\>"
    view = view + "A+ v. " + str(version) + " | <a href=\"https://raw.githubusercontent.com/jonnelafin/A-/master/LICENSE\">LICENSE</a>"
    return(view)
@app.route('/post', methods=['POST'])
def handle_data():
    uIp = request.access_route[0]
    uID = getUID(uIp)
    msg = request.form['msg']
    addChat(uID + ": " + msg)
    return redirect("/", code=302)
@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.access_route[0], 'id' : getUID(request.access_route[0])}), 200
@app.route("/announce", methods=["GET"])
def announceThem():
    global chat
    uIp = request.access_route[0]
    uID = getUID(uIp)
    addClient(uID)
    return jsonify({'you': uID}), 200
@app.route("/unannounce", methods=["GET"])
def unannounceThem():
    global chat
    uIp = request.access_route[0]
    uID = getUID(uIp)
    removeClient(uID)
    return jsonify({'you': uID}), 200
@app.route("/list", methods=["GET"])
def listAnnounced():
    return jsonify({'clients': clients}), 200
@app.route("/req", methods=['POST'])
def requestCH():
    global requests, requests_sent
    uIp = request.access_route[0]
    uID = getUID(uIp)
    if "to" in request.form:
        to = request.form['to']
#	[from, to, status[0sent, 1accepted, 2rejected]]
        req = [uID, to, 0]
        if not (to in requests):
            requests[to] = []
        requests[to].append(req)
        if not (uID in requests_sent):
            requests_sent[uID] = []
        requests_sent[uID].append(req)
        return redirect("/", code=302)
    else:
        return jsonify({'error': "400: POST Request expected"}), 400
@app.route("/status", methods=["GET"])
def sendStatus():
    global requests, requests_sent
    uIp = request.access_route[0]
    uID = getUID(uIp)
    lis = []
    if not (uID in requests_sent):
        requests_sent[uID] = []
    if not (uID in requests):
        requests[uID] = []
    return jsonify({'sent': requests_sent[uID], 'received': requests[uID]}), 200
@app.route("/send", methods=["GET"])
def sendView():
    view = ""
    view = view + "<h3> Send a Chat Request </h3>"
    view = view + "<hr \\>"
    view = view + "<form action=\" " + "/req" + "\" method=\"post\">"
    view = view + "<h4> To: </h4>"
    view = view + "<input type=\"text\" name=\"to\"><br \\>"
    view = view + "<input type=\"submit\">"
    view = view + "</form>"

    view = view + "<hr \\>"

    return view, 200
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
