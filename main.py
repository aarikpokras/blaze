import signal
import socket
import secrets
import json
import random
import string
import os
import sys
import time
import bcrypt
import cont
from flask import Flask, request, jsonify, render_template, send_file, make_response, redirect
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

CONT_SITE_BG = [46, 24, 0]

starttime = time.perf_counter()

blocked = 0
ret429 = 0
destd = 0
dests = 0

app = Flask(__name__, template_folder='./static') # change back to `Flask` if no work
sck = SocketIO(app, cors_allowed_origins="*")
lim = Limiter(get_remote_address, app=app)
CORS(app)

def sigint(sig, frame):
  print("Emitting disconnect message")
  sck.emit("dscon")
  time.sleep(1)
  print('---- Stats ----')
  print("Total seconds      | " + str(time.perf_counter() - starttime))
  print("Connections closed | " + str(blocked))
  print("Rate limited       | " + str(ret429))
  print("Destroyed          | " + str(destd + dests))
  print("  /d               | " + str(destd))
  print("  SIGTERM          | " + str(dests))
  print()
  print("SIGINT received, shutting down")
  sys.exit(0)

def sigterm(sig, frame):
  global dests
  print("dst rec")
  sck.emit("dst")
  dests += 1

signal.signal(signal.SIGINT, sigint)
signal.signal(signal.SIGTERM, sigterm)

@sck.on("connect")
def cnct():
  print("WS connected")

def upd(data):
  sck.emit("upd", data)

print('-----Kill code-----')
KILLCODE = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
print(KILLCODE)
print('-----Kill code-----')

##

wht = ["10.1.9.56", "185.177.72.50"]

def is_allowed(ip):
  return not ip in wht # turn to `not ip in wht` for a blacklist

print("In WHT: " + str(wht))
#print("Is allowed wht[0] = " + str(is_allowed(wht[0])))
if (is_allowed(wht[0])):
  print("Whitelist")
else:
  print("Blacklist")

@app.before_request
def gw():
  global blocked
  if (not is_allowed(request.remote_addr)):
    print('----Blocking Blacklisted IP address----')
    sock = request.environ.get('werkzeug.socket')
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    blocked += 1
    print('----Done Blocking----')

##

@app.errorhandler(429)
def rlh(_):
  global ret429
  ret429 += 1
  return "Too many requests. Try again later.", 429

@app.route('/signup', methods=['POST'])
@lim.limit('20 per minute')
def signup():
  usr = request.json["usr"]
  pw = request.json["pw"]
  d = {}
  with open('h.json', 'r') as hf:
    d = json.load(hf)

    if (usr in d):
      return "User already exists", 400

    salt = bcrypt.gensalt()
    pwhash = bcrypt.hashpw(pw.encode('utf-8'), salt)
    d[usr] = pwhash.decode('utf-8')

  with open('h.json', 'w') as hf:
    json.dump(d, hf)
  return "OK"

@app.route('/signup', methods=['GET'])
def signup_ht():
  return render_template('signup.html')

uztk = {}
uzcl = {}

@app.route('/login', methods=['POST'])
@lim.limit("3 per minute")
def login():
  usr = request.json["usr"]
  psw = request.json["pw"]
  with open('h.json', 'r') as hf:
    d = json.load(hf)
    if (usr in d and bcrypt.checkpw(psw.encode('utf-8'), d[usr].encode('utf-8'))):
      resp = make_response("OK")
      rk = secrets.token_urlsafe(32)
      resp.set_cookie(
        'stok',
        value = rk,
        httponly = True
      )
      uztk[usr] = rk
      uzcl[usr] = [random.randint(0, 255) for _ in range(3)]
      return resp
    else:
      return "Invalid login", 400

@app.route('/login', methods=['GET'])
def login_ht():
  return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout_h():
  resp = make_response("<span style='font-family: system-ui;'>Successfully logged out, goodbye</span>")
  tok = request.cookies.get('stok')
  for u_, tk_ in uztk.items():
    if (tk_ == tok):
      resp.delete_cookie('stok')
      del uztk[u_]
      del uzcl[u_]
      return resp
  return "<span style='font-family: system-ui;'>Not logged in. <a href='/login'>Log in?</a></span>", 400

@app.route('/api/loggedin', methods=['GET'])
def lgibool():
  tok = request.cookies.get('stok')
  for _, tk_ in uztk.items():
    if (tk_ == tok):
      return "1"
  return "0"

@app.route('/d', methods=['GET'])
def destroy():
  global destd
  if (request.args.get('word') == KILLCODE):
    sck.emit("dst")
    destd += 1
    print("GET /d Good")
    return "Done"
  else:
    return "403 Forbidden", 403

@app.route('/panel', methods=['GET'])
def panel():
  if (request.args.get('word') == KILLCODE):
    print("Panel access")
    return render_template('panel.html')
  else:
    return "403 Forbidden", 403

@app.route('/', methods=['GET'])
def go():
  if (is_allowed(request.remote_addr)):
    print(request.user_agent)
    return render_template('index.html')
  else:
    print("Request returning 444. Nothing is actually being returned; the socket has already been closed.")
    return "", 444

@app.route('/favicon.ico', methods=['GET'])
def favicon():
  return send_file('./favi.png')

@app.route('/jquery.min.js', methods=['GET'])
def jquery():
  return send_file('./sc/jquery.min.js')

@app.route('/sounds/<sound>', methods=['GET'])
def snds(sound):
  if (sound == "discon"):
    return send_file("./discon.wav", mimetype='audio/wav')
  elif (sound == "connect"):
    return send_file("./connect.wav", mimetype='audio/wav')
  elif (sound == "pat.gif"):
    return send_file("./pat.gif")

@app.route('/send', methods=['POST'])
@lim.limit('100 per minute')
def send():
  msg = request.json["msg"]
  tok = request.cookies.get('stok')
  for u_, tk_ in uztk.items():
    if (tk_ == tok):
      upd({ 'msg': msg, 'usr': u_, 'color': uzcl[u_], 'ip': request.remote_addr });
      return "OK", 200
  return "Login required", 403

@app.route('/.well-known/<path:_>', methods=['GET'])
def wkn(_):
  return "nothing here dumbass"

if (__name__ == "__main__"):
  sck.run(app, host="0.0.0.0", port=443) # add ssl_context tuple here for HTTPS
