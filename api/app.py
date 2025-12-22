import os, json, random, string, datetime
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# ---------- FIREBASE ----------
if not firebase_admin._apps:
    cred = credentials.Certificate(
        json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

# ---------- HELPERS ----------

def generate_cnic():
    n = list(''.join(random.choices(string.digits, k=12)))
    n[4], n[7], n[9] = '£', '@', ':'
    return ''.join(n)

def generate_redeem_code():
    return '-'.join(
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        for _ in range(4)
    )

def money(v):
    return f"${v:,.2f}".replace(',', '.')

def add_history(ref, t, amt, desc="", f=None, to=None):
    h = {
        "type": t,
        "amount": amt,
        "time": datetime.datetime.utcnow().isoformat(),
        "desc": desc
    }
    if f: h["from"] = f
    if to: h["to"] = to
    ref.collection("history").add(h)

def auth_user(u, p):
    q = db.collection("users").where("username","==",u).where("password","==",p).limit(1)
    docs = list(q.stream())
    return (docs[0].id, docs[0].to_dict()) if docs else (None, None)

# ---------- ROUTES ----------

@app.route("/")
def home():
    return jsonify({"api":"EjeNe Banking","status":"live"})

@app.route("/status")
def status():
    return jsonify({"server":"online"})

# ---------- AUTH ----------

@app.route("/register")
def register():
    u,p = request.args.get("username"), request.args.get("password")
    cc = request.args.get("cc","USD")

    if not u or not p:
        return jsonify({"error":"missing"}),400

    users = db.collection("users")
    if any(users.where("username","==",u).stream()):
        return jsonify({"error":"exists"}),400

    data = {
        "username":u,"password":p,"balance":0,
        "currency":cc,"cnic":generate_cnic(),
        "created":datetime.datetime.utcnow().isoformat()
    }

    ref = users.document()
    ref.set(data)
    add_history(ref,"create",0,"Account created")

    return jsonify({"username":u,"cnic":data["cnic"],"currency":cc})

@app.route("/login")
def login():
    u,p = request.args.get("u"),request.args.get("p")
    uid,data = auth_user(u,p)
    if not data:
        return jsonify({"error":"invalid"}),401

    hist = [
        h.to_dict()
        for h in db.collection("users").document(uid)
        .collection("history").order_by("time",direction=firestore.Query.DESCENDING)
        .limit(10).stream()
    ]

    return jsonify({
        "username":u,
        "balance":money(data["balance"]),
        "cnic":data["cnic"],
        "currency":data["currency"],
        "history":hist
    })

@app.route("/balance")
def balance():
    u,p = request.args.get("u"),request.args.get("p")
    _,d = auth_user(u,p)
    return jsonify({"balance":money(d["balance"])}) if d else (jsonify({"error":"invalid"}),401)

# ---------- SEND MONEY ----------

@app.route("/send")
def send():
    u,p,sendt = request.args.get("u"),request.args.get("p"),request.args.get("sendt")
    amt = float(request.args.get("much",0))

    sid,sd = auth_user(u,p)
    if not sd or amt<=0 or sd["balance"]<amt:
        return jsonify({"error":"failed"}),400

    users = db.collection("users")
    rdocs = list(users.where("username","==",sendt).stream()) or \
            list(users.where("cnic","==",sendt).stream())

    if not rdocs:
        return jsonify({"error":"receiver not found"}),404

    rid,rd = rdocs[0].id, rdocs[0].to_dict()

    batch = db.batch()
    batch.update(users.document(sid),{"balance":sd["balance"]-amt})
    batch.update(users.document(rid),{"balance":rd["balance"]+amt})
    batch.commit()

    add_history(users.document(sid),"send",amt,"Money sent",u,rd["username"])
    add_history(users.document(rid),"receive",amt,"Money received",u,rd["username"])

    return jsonify({"sent":money(amt),"to":rd["username"]})

# ---------- REDEEM ----------

@app.route("/create")
def create():
    v = float(request.args.get("value",0))
    u = int(request.args.get("u",1))
    if v<=0: return jsonify({"error":"invalid"}),400

    code = generate_redeem_code()
    db.collection("redeems").add({
        "code":code,"value":v,"max":u,"used":0,"active":True
    })
    return jsonify({"code":code,"value":money(v)})

@app.route("/redeem")
def redeem():
    u,p,code = request.args.get("u"),request.args.get("p"),request.args.get("redeem")
    uid,ud = auth_user(u,p)
    if not ud: return jsonify({"error":"invalid"}),401

    rdocs = list(db.collection("redeems")
        .where("code","==",code).where("active","==",True).limit(1).stream())

    if not rdocs: return jsonify({"error":"invalid code"}),400

    rid,rd = rdocs[0].id, rdocs[0].to_dict()
    if rd["used"]>=rd["max"]:
        db.collection("redeems").document(rid).update({"active":False})
        return jsonify({"error":"expired"}),400

    db.collection("users").document(uid).update({
        "balance":ud["balance"]+rd["value"]
    })

    db.collection("redeems").document(rid).update({
        "used":rd["used"]+1,"active":rd["used"]+1<rd["max"]
    })

    add_history(db.collection("users").document(uid),"redeem",rd["value"],code)

    return jsonify({"added":money(rd["value"])})

# ---------- SETTINGS ----------

@app.route("/setting")
def setting():
    u,p,nu,np = request.args.get("u"),request.args.get("p"),request.args.get("nu"),request.args.get("np")
    uid,ud = auth_user(u,p)
    if not ud: return jsonify({"error":"invalid"}),401

    db.collection("users").document(uid).update({"username":nu,"password":np})
    add_history(db.collection("users").document(uid),"settings",0,"Updated")

    return jsonify({"status":"updated"})

# ---------- ERRORS ----------

@app.errorhandler(404)
def nf(e): return jsonify({"error":"not found"}),404
