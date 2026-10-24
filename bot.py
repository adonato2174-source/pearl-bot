import requests
import json
import time
import sys

# =====================================================================
#                        USER CONFIGURATION
# =====================================================================
# 1. YOUR VAST KEY: Paste your key from the Vast.ai settings console
VAST_API_KEY = "YOUR_ACTUAL_VAST_API_KEY_HERE" 

# 2. HIGH SPEED CONTAINER BLUEPRINT (Optimized for instant caching on Vast nodes)
DOCKER_IMAGE = "cniweb/srbminer-multi-cuda:latest" 

# 3. KRYPTEX POOL CREDENTIALS (Auto-routes and converts all Pearl rewards to BTC)
KRYPTEX_ID = "krxXPVZW2N"
KRYPTEX_POOL = "prl.kryptex.network:7048"

# 4. INFRASTRUCTURE ARBITRAGE TARGET
TARGET_GPU = "RTX 5090"
# =====================================================================

def get_live_5090_profitability():
    """Queries WhatToMine API to determine live hourly gross revenue for an RTX 5090."""
    wtm_url = "https://whattomine.com"
    
    try:
        response = requests.get(wtm_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract live Pearl hashing parameters
            coins = data.get("coins", {})
            pearl_key = "Pearl" if "Pearl" in coins else "PearlHash"
            pearl_data = coins.get(pearl_key, {})
            
            daily_revenue = float(pearl_data.get("revenue", 0.0))
            if daily_revenue > 0:
                return daily_revenue / 24.0
                
    except Exception as error:
        print(f"[{time.strftime('%X')}] Warning: WhatToMine connection dropped ({error}). Using baseline fallback.")
    
    # Secure baseline fallback value if API drops frames
    return 0.57

def check_and_snipe():
    # 1. Check current market math dynamically
    hourly_earnings = get_live_5090_profitability()
    
    # Protect capital by applying a mandatory 15% margin buffer for setup/stale share friction
    max_allowed_rental = hourly_earnings * 0.85
    
    print("=" * 60)
    print(f"[{time.strftime('%X')}] ENGINE STRATEGY STATUS:")
    print(f"-> Live 5090 Pool Revenue:    ${hourly_earnings:.3f}/hr")
    print(f"-> Maximum Purchase Ceiling:  ${max_allowed_rental:.3f}/hr (15% Net Margin Enforced)")
    print("=" * 60)

    # 2. Interrogate the Vast.ai REST API for low-cost, single machine offers
    url = "https://vast.ai"
    headers = {"Authorization": f"Bearer {VAST_API_KEY}"}
    
    query_payload = {
        "q": json.dumps({
            "gpu_name": {"eq": TARGET_GPU},
            "num_gpus": {"eq": 1},
            "rentable": {"eq": True},
            "verified": {"eq": False} # targets lowest priced unverified spots
        }),
        "order_by": "dph_total",
        "order_direction": "asc"
    }
    
    try:
        response = requests.get(url, headers=headers, params=query_payload, timeout=10)
        
        if response.status_code == 401:
            print("CRITICAL LOGICAL FAULT: Invalid VAST_API_KEY payload. Execution aborted.")
            sys.exit(1)
            
        offers = response.json().get("offers", [])
        if not offers:
            print("-> Match parameters yielded 0 live machines. Sweeping on next interval...")
            return
            
        # Target the lowest market quote matching our query structure
        target_machine = offers
        market_rate = float(target_machine.get("dph_total", 999.0))
        machine_id = target_machine.get("id")
        
        print(f"-> Lowest Spot Price Found: Machine ID {machine_id} listing at ${market_rate:.3f}/hr")
        
        # 3. Arbitrage Execution Check
        if market_rate <= max_allowed_rental:
            print(f"!!! ARBITRAGE EQUATION VALIDATED !!! Sniping Server ID {machine_id}...")
            
            rent_url = f"https://vast.ai{machine_id}/"
            rent_payload = {
                "image": DOCKER_IMAGE,
                "disk": 25.0, # Reserve 25GB high-speed workspace NVMe footprint
                "env": {
                    "POOL": KRYPTEX_POOL,
                    "WALLET": KRYPTEX_ID
                }
            }
            
            rent_response = requests.put(rent_url, headers=headers, json=rent_payload, timeout=10)
            if rent_response.status_code == 200:
                print("SUCCESS: Compute lease confirmed. Sleeping for 5 mins to lock configuration...")
                time.sleep(300)
            else:
                print(f"Lease drop or deployment collision: {rent_response.text}")
        else:
            print("-> Current spread is negative or too narrow. Sitting idle to protect capital.")
            
    except Exception as general_fault:
        print(f"System orchestration fault encountered: {general_fault}")

if __name__ == "__main__":
    if VAST_API_KEY == "YOUR_ACTUAL_VAST_API_KEY_HERE":
        print("ABORT: Paste your secure Vast.ai API Token into line 8 of this script.")
        sys.exit(1)
        
    print("=======================================================")
    print("        DYNAMIC COMPUTE ARBITRAGE DAEMON v2.0")
    print(f"Target Model:  {TARGET_GPU}")
    print(f"Payout Destination Account ID: {KRYPTEX_ID}")
    print("=======================================================")
    
    # Scan loop interval ticks every 15 seconds
    while True:
        check_and_snipe()
        time.sleep(15)
