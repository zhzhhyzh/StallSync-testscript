import requests
import random
import json

# --- Config ---
DOMAIN = "http://localhost:5040"
USERNAME = "member1"
PASSWORD = "123456"
API_KEY = "c871651f-bdf3-4795-b826-cc3cfb80075a"
LIMIT = 10000  # orders per page

# --- Step 1: Login ---
login_res = requests.post(
    f"{DOMAIN}/api/psusrprf/login/",
    json={"username": USERNAME, "password": PASSWORD},
    headers={"Content-Type": "application/json", "api-key": API_KEY}
)

try:
    login_data = login_res.json()
    token = login_data['message']['token']
    print("✅ Logged in")
except Exception as e:
    print("❌ Login error:", str(e))
    exit(1)

auth_token = token if token.lower().startswith("bearer ") else f"Bearer {token}"
headers = {
    "Authorization": auth_token,
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

# --- Step 2: Paginated order list & review ---
offset = 0
total_reviews = 0
total_orders = 0

while True:
    params = {
        "psordsts": "D",
        "from": offset,
        "limit": LIMIT,
    }

    order_list_res = requests.get(
        f"{DOMAIN}/api/psordpar/list",
        params=params,
        headers=headers
    )

    try:
        data = order_list_res.json()
        orders = data.get("message", {}).get("data", [])
    except Exception as e:
        print(f"❌ Failed to parse order list response at offset {offset}:", order_list_res.text)
        break

    if not orders:
        print("✅ No more orders to process.")
        break

    print(f"\n📄 Processing {len(orders)} orders from offset {offset}")
    total_orders += len(orders)

    for order in orders:
        psorduid = order.get("psorduid")
        if not psorduid:
            continue

        # 90% chance to give rating above 3
        if random.random() <= 0.7:
            rating = round(random.uniform(4.1, 5.0), 1)
        elif random.random() <= 0.9:
            rating = round(random.uniform(3.0, 4.0), 1)
        else:
            rating = round(random.uniform(1.0,2.9), 1)

        review_payload = {
            "psorduid": psorduid,
            "psrvwdsc": f"Auto-review for order {psorduid}",
            "psrvwrtg": rating
        }

        review_res = requests.post(
            f"{DOMAIN}/api/psordrvw/create",
            json=review_payload,
            headers=headers
        )

        try:
            review_data = review_res.json()
            result = review_data.get("result", "unknown")
            print(f"📝 Review submitted for {psorduid} (Rating: {rating}) → {result}")
            total_reviews += 1
        except Exception as e:
            print(f"❌ Failed to submit review for {psorduid}:", review_res.text)

    offset += LIMIT

print(f"\n✅ Done: {total_reviews} reviews submitted out of {total_orders} total orders.")
