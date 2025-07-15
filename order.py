import requests
import random
import json

# Available member
# member1, member2, member3, member5 "KR","MM"
#pujin, zhzhhyzh, Gandy "4F","JW","PR"
# kenny, lwk, lwk2 "MM","4F"
#mbrtest "MM" //4f or kr
# cold //the cold start no record
# --- Config ---
DOMAIN = "http://localhost:5040"
USERNAME = "member1"
PASSWORD = "123456"
API_KEY = "c871651f-bdf3-4795-b826-cc3cfb80075a"

for run in range(1, 145):
    print(f"\n🔁 ===== RUN {run} =====")

    # --- Step 1: Login ---
    login_headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }

    login_payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    login_res = requests.post(
        f"{DOMAIN}/api/psusrprf/login/",
        json=login_payload,
        headers=login_headers
    )

    try:
        login_data = login_res.json()
        token = login_data['message']['token']
        print("✅ Token acquired")
    except Exception as e:
        print("❌ Login failed:", str(e))
        print("Response text:", login_res.text)
        continue  # skip to next iteration

    auth_token = token if token.lower().startswith("bearer ") else f"Bearer {token}"
    headers = {
        "Authorization": auth_token,
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # --- Step 2: Create cart 5 times ---
    # psmrcuid = random.choice(["KR", "MM", "4F", "JW", "PR"])
    psmrcuid = random.choice(["MM"])
    print(f"📦 Using psmrcuid: {psmrcuid}")

    for i in range(5):
        product_num = random.randint(1, 7)
        psprduid = f"{psmrcuid}{str(product_num).zfill(6)}"
        qty = random.randint(1, 3)

        cart_payload = {
            "psmrcuid": psmrcuid,
            "psprduid": psprduid,
            "psitmqty": qty,
            "psitmrmk": ""
        }

        cart_res = requests.post(
            f"{DOMAIN}/api/psmbrcrt/create",
            json=cart_payload,
            headers=headers
        )

        try:
            cart_json = cart_res.json()
            print(f"🛒 Cart #{i+1} Response:", cart_json)
        except Exception as e:
            print(f"❌ Failed to parse cart #{i+1} response:", cart_res.text)

    # --- Step 3: Create order ---
    order_payload = {
        "psordpap": "Y",
        "psrwduid": "",
        "psordrap": "N",
        "psmrcuid": psmrcuid
    }

    order_res = requests.post(
        f"{DOMAIN}/api/psordpar/create",
        json=order_payload,
        headers=headers
    )

    try:
        order_data = order_res.json()
        print("📄 Order Response:", order_data)

        ord_id = order_data["message"]["ordId"]
        amt = round(order_data["message"]["amt"], 1)
    except Exception as e:
        print("❌ Failed to parse order response:", str(e))
        print("Order raw response:", order_res.text)
        continue

    # --- Step 4: Create transaction offline ---
    trx_payload = {
        "psorduid": ord_id,
        "pstrxamt": amt
    }

    trx_res = requests.post(
        f"{DOMAIN}/api/pstrxpar/createOffline",
        json=trx_payload,
        headers=headers
    )

    try:
        trx_data = trx_res.json()
        print("💰 Transaction Response:", trx_data)
    except Exception as e:
        print("❌ Failed to parse transaction response:", str(e))
        print("Transaction raw response:", trx_res.text)
