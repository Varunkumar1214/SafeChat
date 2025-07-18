from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from crypto_utils import generate_keys, encrypt_message, decrypt_message
from storage_utils import load_users, save_users, load_messages, save_messages

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this'

# ---------------------------
# Load Persistent Data
# ---------------------------
users = load_users()
messages = load_messages()

# ---------------------------
# Routes
# ---------------------------

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        if username in users:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "User not found. Please register first."
    return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html", username=session['username'])

# --------- Register Page ---------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", info="Please register a new user.")

    if request.is_json:
        data = request.get_json()
        username = data.get('username')
    else:
        username = request.form.get('username')

    if not username:
        return render_template("register.html", info="Username cannot be empty!")

    if username in users:
        return render_template("register.html", info=f"User '{username}' already exists.")

    private_key, public_key = generate_keys()
    users[username] = {
        "private_key": private_key,
        "public_key": public_key
    }
    save_users(users)

    if request.is_json:
        return jsonify({
            "message": f"{username} registered successfully!",
            "public_key": public_key
        })

    return render_template("register.html", info=f"User '{username}' registered successfully!")

# --------- Send Message Page ---------
@app.route('/send', methods=['GET', 'POST'])
def send_message():
    if 'username' not in session:
        return redirect(url_for('login'))

    encrypted = None
    error = None
    success_message = None

    if request.method == 'POST':
        sender = session.get('username')
        receiver = request.form.get('to')
        message = request.form.get('message')

        if not sender or not receiver or not message:
            error = "All fields are required!"
        elif sender not in users or receiver not in users:
            error = "Sender or Receiver is not registered!"
        else:
            encrypted = encrypt_message(users[receiver]['public_key'], message)
            messages.append({
                "from": sender,
                "to": receiver,
                "encrypted_message": encrypted
            })
            save_messages(messages)
            success_message = "Message sent successfully!"

    return render_template("send.html", encrypted=encrypted, message=success_message, error=error)

# --------- Inbox Page (Fixed for GET + POST) ---------
@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    inbox = [msg for msg in messages if msg['to'] == username]
    return render_template("inbox.html", username=username, inbox=inbox)

# --------- Decrypt Page ---------
@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    decrypted = None
    error = None

    if request.method == 'POST':
        username = session['username']
        encrypted_message = request.form.get('encrypted_message')

        if username not in users:
            error = "User not found!"
        else:
            try:
                decrypted = decrypt_message(users[username]['private_key'], encrypted_message)
            except Exception as e:
                error = f"Decryption failed: {str(e)}"

    return render_template("decrypt.html", decrypted=decrypted, error=error)

# ---------------------------
# JSON API Routes
# ---------------------------

@app.route('/send_api', methods=['POST'])
def send_message_api():
    data = request.get_json()
    sender = data.get('from')
    receiver = data.get('to')
    message = data.get('message')

    if sender not in users or receiver not in users:
        return jsonify({"error": "Sender or Receiver not found"}), 404

    encrypted = encrypt_message(users[receiver]['public_key'], message)
    messages.append({
        "from": sender,
        "to": receiver,
        "encrypted_message": encrypted
    })
    save_messages(messages)

    return jsonify({
        "message": "Encrypted message sent!",
        "encrypted": encrypted
    })

@app.route('/decrypt_api', methods=['POST'])
def decrypt_api():
    data = request.get_json()
    username = data.get('username')
    encrypted_msg = data.get('encrypted_message')

    if username not in users:
        return jsonify({"error": "User not found"}), 404

    try:
        decrypted = decrypt_message(users[username]['private_key'], encrypted_msg)
        return jsonify({"decrypted_message": decrypted})
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

@app.route('/inbox/<username>', methods=['GET'])
def inbox_api(username):
    if username not in users:
        return jsonify({"error": "User not found"}), 404

    inbox = [msg for msg in messages if msg['to'] == username]
    return jsonify({"inbox": inbox})

@app.route('/users', methods=['GET'])
def list_users():
    return jsonify(list(users.keys()))

# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
