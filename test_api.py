# test_safechat_api.py

import requests

BASE_URL = "http://127.0.0.1:5000"

# Usernames
user1 = input("Enter Sender Username: ").strip().lower()
user2 = input("Enter Receiver Username: ").strip().lower()
message_text = input(f"Enter message to send from {user1} to {user2}: ").strip()

# 1. Register both users
for user in [user1, user2]:
    res = requests.post(f"{BASE_URL}/register", json={"username": user})
    if res.status_code == 200:
        print(f"✅ Registered {user}: {res.json()['message']}")
    else:
        print(f"⚠️ {user} may already exist:", res.json())

# 2. Send message from user1 to user2
res = requests.post(f"{BASE_URL}/send", json={
    "from": user1,
    "to": user2,
    "message": message_text
})
if res.status_code == 200:
    encrypted = res.json()['encrypted']
    print(f"✅ Message sent! Encrypted content:\n{encrypted}")
else:
    print("❌ Failed to send message:", res.json())
    exit()

# 3. Get inbox of user2
res = requests.get(f"{BASE_URL}/inbox/{user2}")
if res.status_code == 200:
    inbox = res.json()['inbox']
    print(f"\n📥 {user2}'s Inbox:")
    for idx, msg in enumerate(inbox, 1):
        print(f"{idx}. From: {msg['from']} | Encrypted: {msg['encrypted_message']}")
else:
    print("❌ Failed to fetch inbox:", res.json())
    exit()

# 4. Decrypt the latest message for user2
latest_message = inbox[-1]['encrypted_message']
res = requests.post(f"{BASE_URL}/decrypt", json={
    "username": user2,
    "encrypted_message": latest_message
})
if res.status_code == 200:
    print(f"\n🔓 Decrypted Message: {res.json()['decrypted_message']}")
else:
    print("❌ Decryption Failed:", res.json())
