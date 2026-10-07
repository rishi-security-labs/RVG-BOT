from flask import Flask, request, jsonify, render_template_string, session
from werkzeug.serving import WSGIRequestHandler
from datetime import datetime
import json
import hashlib
import logging
import os
import re

WSGIRequestHandler.log_request = lambda *args, **kwargs: None
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = "rvg_ultra_secure_isolated_jwt_2026"

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
MENU_FILE = os.path.join(DATA_DIR, 'menu.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

DEFAULT_SETTINGS = {
    "upi_vpa": "rvgfoods@ybl",
    "payee_name": "RVG Restaurant",
    "custom_qr_image": ""
}

ADMIN_USER = "admin"
ADMIN_PASS = "rvg@123"

def hash_password(password: str) -> str:
    salt = "rvg_salt_secured_99"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def read_json(file_path, default_val):
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_val, f, indent=4)
        return default_val
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_val

def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

DEFAULT_MENU = [
    {
        "id": 1,
        "name": "Artisan Margherita Pizza",
        "category": "Pizza",
        "price": 249,
        "rating": "4.8 ★",
        "desc": "San Marzano sauce, buffalo mozzarella, hand-torn basil",
        "img": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": 2,
        "name": "Tuscan Farmhouse Pizza",
        "category": "Pizza",
        "price": 329,
        "rating": "4.7 ★",
        "desc": "Fire-roasted peppers, zucchini, black olives & mozzarella",
        "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": 3,
        "name": "Paneer Tikka Melt",
        "category": "Pizza",
        "price": 299,
        "rating": "4.6 ★",
        "desc": "Clay oven paneer, roasted onions, mint drizzle & double cheese",
        "img": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": 4,
        "name": "Crispy Herb Burger",
        "category": "Burger",
        "price": 119,
        "rating": "4.5 ★",
        "desc": "Golden herb patty, house garlic aioli & butterhead lettuce",
        "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": 5,
        "name": "Double Cheese Beast",
        "category": "Burger",
        "price": 169,
        "rating": "4.9 ★",
        "desc": "Double melted cheddar, crispy patty & chipotle relish",
        "img": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": 6,
        "name": "Cold Coffee Blast",
        "category": "Drinks",
        "price": 89,
        "rating": "4.7 ★",
        "desc": "Velvety espresso blend shaken with rich chocolate sauce",
        "img": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": 7,
        "name": "Virgin Mint Mojito",
        "category": "Drinks",
        "price": 99,
        "rating": "4.8 ★",
        "desc": "Garden mint, fresh lemon wedges, sparkling soda & cracked ice",
        "img": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=400&q=80"
    }
]

read_json(USERS_FILE, [])
read_json(MENU_FILE, DEFAULT_MENU)
read_json(ORDERS_FILE, [])
read_json(SETTINGS_FILE, DEFAULT_SETTINGS)

def is_admin_authenticated():
    return session.get('is_admin') is True

@app.route('/favicon.ico')
def favicon():
    return ('', 204)

@app.route('/')
def customer_home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/admin')
def admin_page():
    with open('admin.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

# ==================== PAYMENT & STRICT UTR VALIDATION ====================
@app.route('/api/payment/generate-upi', methods=['POST'])
def generate_upi():
    phone = session.get('user_phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Pehle Login kijiye!'}), 401

    data = request.get_json() or {}
    cart = data.get('items', {})
    if not cart:
        return jsonify({'success': False, 'message': 'Cart empty hai!'}), 400

    settings = read_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    upi_vpa = settings.get("upi_vpa", "rvgfoods@ybl")
    payee_name = settings.get("payee_name", "RVG Restaurant")
    custom_qr = settings.get("custom_qr_image", "")

    menu_list = read_json(MENU_FILE, DEFAULT_MENU)
    menu_map = {str(m['id']): m for m in menu_list}

    total = 0
    for item_id_str, qty in cart.items():
        if item_id_str in menu_map and int(qty) > 0:
            total += menu_map[item_id_str]['price'] * int(qty)

    order_ref = f"RVG{datetime.now().strftime('%M%S')}{os.urandom(2).hex().upper()}"
    upi_intent_url = f"upi://pay?pa={upi_vpa}&pn={payee_name}&am={total}&cu=INR&tn=Order_{order_ref}"

    return jsonify({
        'success': True,
        'order_ref': order_ref,
        'amount': total,
        'vpa': upi_vpa,
        'payee_name': payee_name,
        'custom_qr': custom_qr,
        'upi_url': upi_intent_url
    })

# STRICT PLACE ORDER (MANDATORY 12-DIGIT & NO DUPLICATE UTR)
@app.route('/api/place-order', methods=['POST'])
def place_order():
    phone = session.get('user_phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Pehle Login kijiye!'}), 401

    users = read_json(USERS_FILE, [])
    u = next((x for x in users if x['phone'] == phone), None)
    if not u or u.get('is_blocked') == 1:
        return jsonify({'success': False, 'message': 'Account blocked hai!'}), 403

    data = request.get_json() or {}
    customer = data.get('customer', {})
    cart = data.get('items', {})
    txn_id = str(data.get('txn_id', '')).strip()

    # 1. Strict UTR Validation: Exactly 12 numeric digits
    if not txn_id:
        return jsonify({'success': False, 'message': 'Payment UTR / Ref Number daalna anivarya (compulsory) hai!'}), 400

    if not re.fullmatch(r'^\d{12}$', txn_id):
        return jsonify({'success': False, 'message': 'Galat UTR! PhonePe/GPay me 12 anko (digits) ka UTR/Ref no hota hai. Kripya sahi 12 digits enter karein.'}), 400

    # 2. Fake / Duplicate UTR Check (Anti-Fraud)
    orders = read_json(ORDERS_FILE, [])
    for existing_order in orders:
        if existing_order.get('txn_id') == txn_id:
            return jsonify({'success': False, 'message': 'Ye UTR number pehle se use kiya ja chuka hai! Duplicate payment allow nahi hai.'}), 400

    if not cart:
        return jsonify({'success': False, 'message': 'Cart empty hai!'}), 400

    menu_list = read_json(MENU_FILE, DEFAULT_MENU)
    menu_map = {str(m['id']): m for m in menu_list}

    total = 0
    item_lines = []
    for item_id_str, qty in cart.items():
        if item_id_str in menu_map and int(qty) > 0:
            it = menu_map[item_id_str]
            sub = it['price'] * int(qty)
            total += sub
            item_lines.append(f"{it['name']} x{qty}")

    order_id = data.get('order_ref') or f"RVG-{datetime.now().strftime('%M%S')}-{os.urandom(2).hex().upper()}"
    created_at = datetime.now().strftime('%d-%m-%Y %I:%M %p')

    new_order = {
        "id": (max([o['id'] for o in orders], default=0) + 1),
        "order_id": order_id,
        "user_phone": phone,
        "customer_name": customer.get('name', u['name']),
        "phone": customer.get('phone', phone),
        "address": customer.get('address', u['address']),
        "items": ", ".join(item_lines),
        "total": total,
        "payment_status": "AWAITING_VERIFICATION",
        "payment_mode": "UPI / PhonePe",
        "txn_id": txn_id,
        "status": "Payment Pending",
        "created_at": created_at
    }
    orders.insert(0, new_order)
    write_json(ORDERS_FILE, orders)

    return jsonify({'success': True, 'order_id': order_id, 'total': total, 'time': created_at})

# ==================== ADMIN SETTINGS & AUTH ====================
@app.route('/api/admin/settings', methods=['GET'])
def get_admin_settings():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    return jsonify(read_json(SETTINGS_FILE, DEFAULT_SETTINGS))

@app.route('/api/admin/settings/update', methods=['POST'])
def update_admin_settings():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    settings = read_json(SETTINGS_FILE, DEFAULT_SETTINGS)

    if 'upi_vpa' in data and data['upi_vpa'].strip():
        settings['upi_vpa'] = data['upi_vpa'].strip()
    if 'payee_name' in data and data['payee_name'].strip():
        settings['payee_name'] = data['payee_name'].strip()
    if 'custom_qr_image' in data:
        settings['custom_qr_image'] = data['custom_qr_image']

    write_json(SETTINGS_FILE, settings)
    return jsonify({'success': True, 'settings': settings})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        session['is_admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid Admin Credentials!'}), 401

@app.route('/api/admin/status', methods=['GET'])
def admin_status():
    return jsonify({'authenticated': is_admin_authenticated()})

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return jsonify({'success': True})

# ==================== USER AUTH ====================
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    address = data.get('address', '').strip()

    if not name or not phone or not password:
        return jsonify({'success': False, 'message': 'Saari details bhariye!'}), 400

    users = read_json(USERS_FILE, [])
    if any(u['phone'] == phone for u in users):
        return jsonify({'success': False, 'message': 'Ye number pehle se registered hai!'}), 400

    new_user = {
        "id": (max([u['id'] for u in users], default=0) + 1),
        "name": name,
        "phone": phone,
        "password": hash_password(password),
        "address": address,
        "avatar": "",
        "is_blocked": 0,
        "created_at": datetime.now().strftime('%d-%m-%Y %I:%M %p')
    }
    users.append(new_user)
    write_json(USERS_FILE, users)

    session['user_phone'] = phone
    session['user_name'] = name
    return jsonify({'success': True, 'user': {'name': name, 'phone': phone, 'address': address, 'avatar': ''}})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()

    users = read_json(USERS_FILE, [])
    hashed = hash_password(password)
    user = next((u for u in users if u['phone'] == phone and u['password'] == hashed), None)

    if not user:
        return jsonify({'success': False, 'message': 'Invalid Phone ya Password!'}), 401

    if user.get('is_blocked') == 1:
        return jsonify({'success': False, 'message': 'Aapka account admin dwara blocked hai!'}), 403

    session['user_phone'] = user['phone']
    session['user_name'] = user['name']
    return jsonify({'success': True, 'user': {'name': user['name'], 'phone': user['phone'], 'address': user['address'], 'avatar': user.get('avatar', '')}})

@app.route('/api/auth/current', methods=['GET'])
def current_user():
    phone = session.get('user_phone')
    if not phone:
        return jsonify({'logged_in': False})

    users = read_json(USERS_FILE, [])
    user = next((u for u in users if u['phone'] == phone), None)
    if not user or user.get('is_blocked') == 1:
        session.clear()
        return jsonify({'logged_in': False})

    return jsonify({
        'logged_in': True,
        'user': {'name': user['name'], 'phone': user['phone'], 'address': user['address'], 'avatar': user.get('avatar', '')}
    })

@app.route('/api/user/profile-update', methods=['POST'])
def update_profile():
    phone = session.get('user_phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Pehle login karein!'}), 401

    data = request.get_json() or {}
    users = read_json(USERS_FILE, [])
    user = next((u for u in users if u['phone'] == phone), None)
    if not user:
        return jsonify({'success': False, 'message': 'User nahi mila!'}), 404

    if 'name' in data and data['name'].strip():
        user['name'] = data['name'].strip()
        session['user_name'] = user['name']
    if 'address' in data:
        user['address'] = data['address'].strip()
    if 'avatar' in data:
        user['avatar'] = data['avatar']

    write_json(USERS_FILE, users)
    return jsonify({'success': True, 'user': {'name': user['name'], 'phone': user['phone'], 'address': user['address'], 'avatar': user.get('avatar', '')}})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_phone', None)
    session.pop('user_name', None)
    return jsonify({'success': True})

@app.route('/api/menu', methods=['GET'])
def get_menu():
    return jsonify(read_json(MENU_FILE, DEFAULT_MENU))

@app.route('/api/user/orders', methods=['GET'])
def user_orders():
    phone = session.get('user_phone')
    if not phone:
        return jsonify([])
    orders = read_json(ORDERS_FILE, [])
    return jsonify([o for o in orders if o.get('user_phone') == phone])

# ==================== PROTECTED ADMIN APIS ====================
@app.route('/api/admin/orders', methods=['GET'])
def admin_orders():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    return jsonify(read_json(ORDERS_FILE, []))

@app.route('/api/admin/update-status', methods=['POST'])
def update_status():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    order_id = data.get('order_id')
    status = data.get('status')
    orders = read_json(ORDERS_FILE, [])
    for o in orders:
        if o['order_id'] == order_id:
            o['status'] = status
            if status in ['Preparing', 'Delivered']:
                o['payment_status'] = 'VERIFIED_PAID'
            elif status == 'Cancelled':
                o['payment_status'] = 'FAILED/REJECTED'
            break
    write_json(ORDERS_FILE, orders)
    return jsonify({'success': True})

@app.route('/api/admin/menu/add', methods=['POST'])
def add_menu_item():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    items = read_json(MENU_FILE, DEFAULT_MENU)
    new_item = {
        "id": (max([m['id'] for m in items], default=0) + 1),
        "name": data.get('name'),
        "category": data.get('category', 'Pizza'),
        "price": float(data.get('price', 0)),
        "rating": "4.8 ★",
        "desc": data.get('desc', ''),
        "img": data.get('img', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80')
    }
    items.insert(0, new_item)
    write_json(MENU_FILE, items)
    return jsonify({'success': True})

@app.route('/api/admin/menu/edit', methods=['POST'])
def edit_menu_item():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    items = read_json(MENU_FILE, DEFAULT_MENU)
    for m in items:
        if str(m['id']) == str(data.get('id')):
            m['name'] = data.get('name')
            m['category'] = data.get('category')
            m['price'] = float(data.get('price', 0))
            m['desc'] = data.get('desc')
            m['img'] = data.get('img')
            break
    write_json(MENU_FILE, items)
    return jsonify({'success': True})

@app.route('/api/admin/menu/delete', methods=['POST'])
def delete_menu_item():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    item_id = str(data.get('id'))
    items = read_json(MENU_FILE, DEFAULT_MENU)
    items = [m for m in items if str(m['id']) != item_id]
    write_json(MENU_FILE, items)
    return jsonify({'success': True})

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    users = read_json(USERS_FILE, [])
    return jsonify([{
        "id": u['id'],
        "name": u['name'],
        "phone": u['phone'],
        "address": u['address'],
        "avatar": u.get('avatar', ''),
        "is_blocked": u.get('is_blocked', 0),
        "created_at": u.get('created_at', '')
    } for u in users])

@app.route('/api/admin/user/toggle-block', methods=['POST'])
def toggle_block_user():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    uid = int(data.get('id'))
    is_blocked = int(data.get('is_blocked'))
    users = read_json(USERS_FILE, [])
    for u in users:
        if u['id'] == uid:
            u['is_blocked'] = is_blocked
            break
    write_json(USERS_FILE, users)
    return jsonify({'success': True})

@app.route('/api/admin/user/delete', methods=['POST'])
def delete_user():
    if not is_admin_authenticated():
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    uid = int(data.get('id'))
    users = [u for u in read_json(USERS_FILE, []) if u['id'] != uid]
    write_json(USERS_FILE, users)
    return jsonify({'success': True})

if __name__ == '__main__':
    os.system('clear')
    print("=" * 45)
    print("  🚀 RVG RESTAURANT RUNNING SILENTLY")
    print("  📱 Store Front : http://127.0.0.1:5000")
    print("  🛠️ Admin Panel : http://127.0.0.1:5000/admin")
    print("  🛡️ Strict UTR : 12-Digit & Anti-Fraud Active")
    print("=" * 45)
    app.run(host='0.0.0.0', port=5000, debug=False)
