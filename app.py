import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
import random
import string
import datetime
import re

# Firebase initialization
cred_dict = {
    "type": "service_account",
    "project_id": "ejene-d8ff7",
    "private_key_id": "a2ce7b7cf5ae878769eb6fb2308c2f2c5952d023",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCZT/b14ET8+Z93
ler9lyPPNw8yq119Q7Q3SSs/AseMrozsiW+KEqIR3KI7IbMdcUDSDMVP8FnJnb8v
sc1h4KBfOX/E7KfPyx7bLtXZmlPcE2VMkKEYv8LSkXLmXcXSutMYlpt29V5eWlEG
Al+AuJewbDRTbZsKF0QjMNNyrkV9kVgddejVlanGSghZkDfn1wq3E9nZio/E1NPO
U65lKWrMz+ue9ftjH//ZQTC8GanqaelCcTG9SKu2+TY7WAqGj2QHsaQNzTU292Lk
MevzYgxbPH94fg1Xl1zvkficQ6IsRbPwTbdobBX+9bl0MmNdq0zyTWdkvdRMc3DI
t/vtUQ2/AgMBAAECggEAK/CGKDwJqbNlZ+G4wstxgO8X1P7WQZOI8BtxYJLMXF6e
lyBgrmLevl3MxUPIURTnbgwo9Ns+8JDcfa/o3DeD3ybcnrTw95YQluMaeU5I4JdS
fhopga1cCfuTwcB4dQgEflST5Ak47bPW6vD9LCg7mV25tXuBZuf6KFfTElguJGl1
E02OTLK4y8jQPLoTm0ZhSVAaE5AD67EBX28Xs4JXBQxGSfqcWKN9DurkzQdj32zq
i5HjdSA+gJSTyFSvC6394r5CwD7/hNi+X5M+6PRIRU3Brdjuknz8MLPb3DHrte+x
ovF777eAtpswI1q/haeZZ/rlxEuIOdchebfWpO+bgQKBgQDJd03PHjbLw0t3H3IG
6HngANaZEDCHv8Ns5gkvtPRisha0zrsPn7Db3yPr3RlpSTXyJbDzbutVH2PWLOoe
pnKrtS0XwZgLNe/dmNyjDKtG5egdwXK5HdMdgl3+o507lxSM7mGJz5RrSRnwvaB1
t5+wZeakVRqS6Y8H/ULj1Y0zfwKBgQDCz9OamwVwOG1AO+0mAemtgNWOQqNSx9+L
goOrCys5llZwCiEFUKZpYr9aYRcqK8n/XXWJSaqipXGGbJoPzCUKMoqUQBS6vHTh
KlP7viaAau4X/FPYVESgf8B8wfxVxCA+gmscHxlhtcquxOVh6kIyO017pAQuIvc6
KD3gbwRFwQKBgCpqieE/dT31QiA0aKd3rqEwy/2x4OXTw+tbizeWG5Xj9M/gbpXd
gzjnhAKWrFD0bv0qXjoPclCbqUNgdXI6jQ4FuRa1VbOWiYfYNSvG8RCeOv54yhSb
aOVfmzaPb/0p09PQJI0FPTRRUbrT0cK3BFH5QlP67vtbXRfLhJe/UFk1AoGBAITz
/29Zcym2aOFYxK2Wypst/RFc60gYvrjgtump8rMXpiBK2WReOWRdD0koT/3o6rAM
YaXzj6/3B3Z9cdtsMK839RnebgdPjNkK4UxC5tXnpFzcSYCvajK7XWwHnCYQdw0S
RvVnSBRGVHBYUlAz5z+O9391XaD7Hg0j367nNVxBAoGBAMFIOR5c+0UWHoobxKXX
uCGxzIpZOjfhrLogE7+7a9jj8PNI4NqPHfs4G7MCRKFv+Garknv/26woBep1Oejy
PD4bjV5hHUnBS9cXAdvKp874Kzm/qGPRyVdhzM0WlWGosJcf9piF6iOvlOtE8pAX
DrKyCdpdVa35qdREjA8Th5A+
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@ejene-d8ff7.iam.gserviceaccount.com",
    "client_id": "101320601096418971113",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40ejene-d8ff7.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Initialize Firebase
try:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
except:
    # If already initialized, use existing app
    pass

db = firestore.client()

app = Flask(__name__)

def generate_cnic():
    """Generate random CNIC with special characters"""
    numbers = ''.join(random.choices(string.digits, k=12))
    special_chars = ['£', '@', ':']
    
    # Insert special characters at random positions
    cnic = list(numbers)
    cnic[4] = special_chars[0]  # £ at position 4
    cnic[7] = special_chars[1]  # @ at position 7
    cnic[9] = special_chars[2]  # : at position 9
    
    return ''.join(cnic)

def generate_redeem_code():
    """Generate redeem code in format H9K920-0V82M-S9kHO-91HW"""
    parts = []
    for _ in range(4):
        part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        parts.append(part)
    return '-'.join(parts)

def format_money(amount):
    """Format money to $00.00.00 format"""
    return f"${amount:,.2f}".replace(',', '.')

def add_history(user_ref, transaction_type, amount, from_user=None, to_user=None, description=""):
    """Add transaction to user history"""
    history_ref = user_ref.collection('history').document()
    
    history_data = {
        'type': transaction_type,
        'amount': amount,
        'timestamp': datetime.datetime.now().isoformat(),
        'description': description
    }
    
    if from_user:
        history_data['from'] = from_user
    if to_user:
        history_data['to'] = to_user
    
    history_ref.set(history_data)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to EjeNe Banking API", "status": "live"})

@app.route('/status')
def status():
    return jsonify({"status": "live", "message": "API is working perfectly"})

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('u')
    password = request.args.get('p')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Check if user exists
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', username).where('password', '==', password).limit(1)
    docs = query.stream()
    
    user_data = None
    user_id = None
    
    for doc in docs:
        user_data = doc.to_dict()
        user_id = doc.id
    
    if not user_data:
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Get user's history
    history_ref = db.collection('users').document(user_id).collection('history')
    history_docs = history_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
    
    history_list = []
    for doc in history_docs:
        hist_data = doc.to_dict()
        history_list.append(hist_data)
    
    response = {
        "name": user_data.get('username'),
        "money": format_money(user_data.get('balance', 0)),
        "cnic": user_data.get('cnic', ''),
        "history": history_list,
        "currency": user_data.get('currency', 'USD')
    }
    
    return jsonify(response)

@app.route('/register', methods=['GET'])
def register():
    username = request.args.get('username')
    password = request.args.get('password')
    currency = request.args.get('cc', 'USD')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Check if username already exists
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', username).limit(1)
    docs = query.stream()
    
    if any(docs):
        return jsonify({"error": "Username already exists"}), 400
    
    # Generate CNIC
    cnic = generate_cnic()
    
    # Create user document
    user_data = {
        'username': username,
        'password': password,
        'cnic': cnic,
        'balance': 0.0,
        'currency': currency,
        'created_at': datetime.datetime.now().isoformat()
    }
    
    # Save to Firebase
    user_ref = users_ref.document()
    user_ref.set(user_data)
    
    # Add initial history entry
    add_history(user_ref, 'account_created', 0, description="Account created successfully")
    
    return jsonify({
        "message": "Account created successfully",
        "cnic": cnic,
        "username": username,
        "currency": currency
    })

@app.route('/send', methods=['GET'])
def send_money():
    username = request.args.get('u')
    password = request.args.get('p')
    sendu = request.args.get('sendu')  # Sender's username
    sendt = request.args.get('sendt')  # Receiver's username or CNIC
    amount_str = request.args.get('much')
    
    if not all([username, password, sendu, sendt, amount_str]):
        return jsonify({"error": "All parameters required"}), 400
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except:
        return jsonify({"error": "Invalid amount"}), 400
    
    # Verify sender credentials
    users_ref = db.collection('users')
    sender_query = users_ref.where('username', '==', sendu).where('password', '==', password).limit(1)
    sender_docs = sender_query.stream()
    
    sender_data = None
    sender_id = None
    for doc in sender_docs:
        sender_data = doc.to_dict()
        sender_id = doc.id
    
    if not sender_data:
        return jsonify({"error": "Invalid sender credentials"}), 401
    
    # Check if sender has enough balance
    if sender_data.get('balance', 0) < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    # Find receiver by username or CNIC
    receiver_query = users_ref.where('username', '==', sendt).limit(1)
    receiver_docs = receiver_query.stream()
    
    receiver_data = None
    receiver_id = None
    
    for doc in receiver_docs:
        receiver_data = doc.to_dict()
        receiver_id = doc.id
    
    # If not found by username, try by CNIC
    if not receiver_data:
        cnic_query = users_ref.where('cnic', '==', sendt).limit(1)
        cnic_docs = cnic_query.stream()
        
        for doc in cnic_docs:
            receiver_data = doc.to_dict()
            receiver_id = doc.id
    
    if not receiver_data:
        return jsonify({"error": "Receiver not found"}), 404
    
    # Perform transaction
    batch = db.batch()
    
    # Update sender balance
    sender_ref = users_ref.document(sender_id)
    new_sender_balance = sender_data['balance'] - amount
    batch.update(sender_ref, {'balance': new_sender_balance})
    
    # Update receiver balance
    receiver_ref = users_ref.document(receiver_id)
    new_receiver_balance = receiver_data['balance'] + amount
    batch.update(receiver_ref, {'balance': new_receiver_balance})
    
    # Commit batch
    batch.commit()
    
    # Add history for sender
    add_history(sender_ref, 'send', amount, 
                from_user=sender_data['username'], 
                to_user=receiver_data['username'],
                description=f"Sent ${amount} to {receiver_data['username']}")
    
    # Add history for receiver
    add_history(receiver_ref, 'receive', amount,
                from_user=sender_data['username'],
                to_user=receiver_data['username'],
                description=f"Received ${amount} from {sender_data['username']}")
    
    return jsonify({
        "message": "Transaction successful",
        "amount_sent": format_money(amount),
        "sender": sender_data['username'],
        "receiver": receiver_data['username'],
        "sender_balance": format_money(new_sender_balance)
    })

@app.route('/create', methods=['GET'])
def create_redeem():
    value_str = request.args.get('value')
    max_uses_str = request.args.get('u', '1')  # Default 1 use
    
    if not value_str:
        return jsonify({"error": "Value parameter required"}), 400
    
    try:
        value = float(value_str)
        max_uses = int(max_uses_str)
        if value <= 0:
            return jsonify({"error": "Value must be positive"}), 400
    except:
        return jsonify({"error": "Invalid value or uses parameter"}), 400
    
    # Generate redeem code
    code = generate_redeem_code()
    
    # Save to Firebase
    redeem_ref = db.collection('redeems').document()
    redeem_data = {
        'code': code,
        'value': value,
        'max_uses': max_uses,
        'used_count': 0,
        'created_at': datetime.datetime.now().isoformat(),
        'is_active': True
    }
    
    redeem_ref.set(redeem_data)
    
    return jsonify({
        "message": "Redeem code created",
        "code": code,
        "value": format_money(value),
        "max_uses": max_uses
    })

@app.route('/redeem', methods=['GET'])
def redeem_code():
    username = request.args.get('u')
    password = request.args.get('p')
    code = request.args.get('redeem')
    
    if not all([username, password, code]):
        return jsonify({"error": "All parameters required"}), 400
    
    # Verify user credentials
    users_ref = db.collection('users')
    user_query = users_ref.where('username', '==', username).where('password', '==', password).limit(1)
    user_docs = user_query.stream()
    
    user_data = None
    user_id = None
    for doc in user_docs:
        user_data = doc.to_dict()
        user_id = doc.id
    
    if not user_data:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Find redeem code
    redeem_ref = db.collection('redeems')
    redeem_query = redeem_ref.where('code', '==', code).where('is_active', '==', True).limit(1)
    redeem_docs = redeem_query.stream()
    
    redeem_data = None
    redeem_id = None
    for doc in redeem_docs:
        redeem_data = doc.to_dict()
        redeem_id = doc.id
    
    if not redeem_data:
        return jsonify({"error": "Invalid or expired redeem code"}), 400
    
    # Check if code has reached max uses
    if redeem_data['used_count'] >= redeem_data['max_uses']:
        # Deactivate code
        redeem_ref.document(redeem_id).update({'is_active': False})
        return jsonify({"error": "Redeem code has been fully used"}), 400
    
    # Update user balance
    user_ref = users_ref.document(user_id)
    new_balance = user_data['balance'] + redeem_data['value']
    
    # Update redeem usage
    new_used_count = redeem_data['used_count'] + 1
    redeem_ref.document(redeem_id).update({
        'used_count': new_used_count,
        'is_active': new_used_count < redeem_data['max_uses']
    })
    
    # Update user balance
    user_ref.update({'balance': new_balance})
    
    # Add history
    add_history(user_ref, 'redeem', redeem_data['value'],
                description=f"Redeemed code: {code}")
    
    return jsonify({
        "message": "Redeem successful",
        "amount_added": format_money(redeem_data['value']),
        "new_balance": format_money(new_balance),
        "code": code,
        "remaining_uses": redeem_data['max_uses'] - new_used_count
    })

@app.route('/setting', methods=['GET'])
def settings():
    old_username = request.args.get('u')
    old_password = request.args.get('p')
    new_username = request.args.get('nu')
    new_password = request.args.get('np')
    
    if not all([old_username, old_password, new_username, new_password]):
        return jsonify({"error": "All parameters required"}), 400
    
    # Find user with old credentials
    users_ref = db.collection('users')
    user_query = users_ref.where('username', '==', old_username).where('password', '==', old_password).limit(1)
    user_docs = user_query.stream()
    
    user_data = None
    user_id = None
    for doc in user_docs:
        user_data = doc.to_dict()
        user_id = doc.id
    
    if not user_data:
        return jsonify({"error": "Invalid current credentials"}), 401
    
    # Check if new username already exists (if changing username)
    if new_username != old_username:
        check_query = users_ref.where('username', '==', new_username).limit(1)
        if any(check_query.stream()):
            return jsonify({"error": "New username already exists"}), 400
    
    # Update user
    user_ref = users_ref.document(user_id)
    update_data = {}
    
    if new_username != old_username:
        update_data['username'] = new_username
    
    if new_password != old_password:
        update_data['password'] = new_password
    
    if update_data:
        user_ref.update(update_data)
        
        # Add history
        add_history(user_ref, 'settings_updated', 0,
                    description="Account settings updated")
    
    return jsonify({
        "message": "Settings updated successfully",
        "username": new_username,
        "status": "updated"
    })

@app.route('/balance', methods=['GET'])
def check_balance():
    username = request.args.get('u')
    password = request.args.get('p')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Check if user exists
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', username).where('password', '==', password).limit(1)
    docs = query.stream()
    
    user_data = None
    for doc in docs:
        user_data = doc.to_dict()
    
    if not user_data:
        return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({
        "username": user_data['username'],
        "balance": format_money(user_data['balance']),
        "cnic": user_data['cnic'],
        "currency": user_data['currency']
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)