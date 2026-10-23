import requests
import time
import sys

# =====================================================================
#                        USER CONFIGURATION
# =====================================================================
# Paste your secure API Key from your Vast.ai console account settings page
VAST_API_KEY = "put api key here" 

# Target Asset and Infrastructure thresholds
TARGET_GPU = "RTX 5090"
MAX_RENTAL_PRICE = 0.42  # Your target spread threshold
DOCKER_IMAGE = "yourusername/pearl-miner-5090:latest" # Your blueprint path

# Kryptex Payout Architecture
KRYPTEX_ID = "put id here"
KRYPTEX_POOL = "stratum+tcp://prl.kryptex.network:7048"
# =====================================================================

def search_and_snipe_rigs():
    print(f"[{time.strftime('%X')}] Scanning Vast.ai database for underpriced {TARGET_GPU}s...")
    
    url = "https://vast.ai"
    headers = {
        "Authorization": f"Bearer {VAST_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Structure database query to fetch rentable, active, single cards sorted by price
    payload = {
        "q": f"gpu_name == {TARGET_GPU} num_gpus == 1 rentable == True",
        "order": [["dph_total", "asc"]]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 401:
            print("CRITICAL ACTION REQUIRED: Your Vast API Key is invalid or copied incorrectly.")
            sys.exit(1)
            
        data = response.json()
        offers = data.get("offers", [])
        
        if not offers:
            print("-> Marketplace is currently empty of this GPU class. Retrying on next loop...")
            return
            
        # Inspect the lowest priced item sitting at the top of our queue
        best_deal = offers[0]
        hourly_rate = best_deal.get("dph_total", 999.0)
        machine_id = best_deal.get("id")
        
        print(f"-> Market Floor Found: Machine ID {machine_id} listing at ${hourly_rate:.3f}/hr")
        
        # Guard clause tracking mathematical arbitrage spread limits
        if hourly_rate <= MAX_RENTAL_PRICE:
            print(f"!!! ARBITRAGE SIGNAL MATCHED !!! Deploying payload to Machine {machine_id}...")
            
            rent_url = f"https://vast.ai{machine_id}/"
            rent_payload = {
                "image": DOCKER_IMAGE,
                "disk": 30.0, # Reserves 30GB high-speed disk footprint
                "env": {
                    "POOL": KRYPTEX_POOL,
                    "WALLET": KRYPTEX_ID
                }
            }
            
            rent_response = requests.put(rent_url, headers=headers, json=rent_payload, timeout=10)
            
            if rent_response.status_code == 200:
                print(f"SUCCESS: Server lease initiated. Hashing routing parameters into pool.")
                print("Pausing engine execution for 5 minutes to prevent double-spending balance reserves...")
                time.sleep(300)
            else:
                print(f"Lease order dropped by host engine or outbid: {rent_response.text}")
        else:
            print(f"-> Spread margin check failed (${hourly_rate:.2f}/hr is above ceiling limit of ${MAX_RENTAL_PRICE:.2f}/hr).")
            
    except requests.exceptions.RequestException as error:
        print(f"Network transport anomaly encountered: {error}")
    except Exception as general_err:
        print(f"Execution handling error: {general_err}")

if __name__ == "__main__":
    if VAST_API_KEY == "YOUR_ACTUAL_VAST_API_KEY_HERE":
        print("ABORTING: You must replace 'YOUR_ACTUAL_VAST_API_KEY_HERE' on Line 8 with your real token.")
        sys.exit(1)
        
    print("=======================================================")
    print("        PEARL COMPUTE ARBITRAGE POOL MONITOR")
    print(f"Targeting: {TARGET_GPU} at under ${MAX_RENTAL_PRICE}/hr")
    print(f"Routing to User ID: {KRYPTEX_ID}")
    print("=======================================================")
    
    # Executes the loop indefinitely every 15 seconds
    while True:
        search_and_snipe_rigs()
        time.sleep(15)
