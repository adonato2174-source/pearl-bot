# Pearl Bot

This project is a simple automation bot for renting GPU instances on Vast.ai and using them to mine Pearl (PearlHash). It monitors market profitability, checks the Vast.ai marketplace for low-cost machines, and if the deal is profitable enough it automatically launches a mining container on the selected GPU.

This is intended to be a lightweight, self-hosted mining automation script for personal use. It is not a full production control system and is best treated as a basic proof-of-concept or helper script.

## What it does

- Queries live Pearl profitability from WhatToMine
- Compares that revenue against the cost of renting a GPU on Vast.ai
- Finds the cheapest matching single-GPU machine offering
- Validates that the rental price is below the configured profit threshold
- Automatically configures and starts a mining container using SRBMiner-MULTI
- Sends mined rewards to the configured Kryptex wallet

## Files

- `bot.py` — main automation script
- `Dockerfile` — container used to run the miner on the rented GPU

## Prerequisites

Before using this tool, you need:

- A Vast.ai account
- A Vast.ai API token
- A Kryptex wallet / pool configuration for Pearl rewards
- A Linux environment or container runtime to run the script locally
- Docker installed if you want to build/modify the mining container locally

## Setup

### 1. Configure the bot

Open `bot.py` and edit the user configuration section near the top:

```python
VAST_API_KEY = "YOUR_ACTUAL_VAST_API_KEY_HERE"
DOCKER_IMAGE = "cniweb/srbminer-multi-cuda:latest"
KRYPTEX_ID = "krxXPVZW2N"
KRYPTEX_POOL = "prl.kryptex.network:7048"
TARGET_GPU = "RTX 5090"
```

Update the values as needed:

- `VAST_API_KEY`: Your actual Vast.ai API token
- `DOCKER_IMAGE`: Docker image to run on the rented server
- `KRYPTEX_ID`: Your Kryptex wallet ID or payout address
- `KRYPTEX_POOL`: The pool endpoint used for mining
- `TARGET_GPU`: The GPU model you want to target on Vast.ai

### 2. Put in your real Vast API key

The script will refuse to run until you replace this placeholder:

```python
VAST_API_KEY = "YOUR_ACTUAL_VAST_API_KEY_HERE"
```

with your real token from the Vast.ai dashboard.

### 3. Verify the mining pool wallet settings

The script sends the following environment variables into the container:

```python
"POOL": KRYPTEX_POOL,
"WALLET": KRYPTEX_ID
```

This is used by the Docker startup script to mine into the configured pool account.

## How the script works

The bot runs in a loop and performs the following checks:

1. Reads the current Pearl revenue from WhatToMine
2. Calculates a target rental ceiling based on expected earnings
3. Requests the Vast.ai marketplace for single-GPU rentable instances
4. Finds the cheapest matching machine
5. If the price is low enough, it launches the miner container on that machine
6. Repeats the process every 15 seconds while the script is running

The current logic includes a safety margin and only rents when it believes the deal is favorable.

## Running the bot

From the project directory:

```bash
python3 bot.py
```

If the API key is still set to the placeholder value, the script exits immediately.

## Docker details

The `Dockerfile` builds a CUDA-based Ubuntu environment and installs SRBMiner-MULTI for PearlHash mining.

The container entry point runs:

```bash
./SRBMiner-MULTI --algorithm pearlhash --pool "$POOL" --wallet "$WALLET" --password x
```

This means the host machine must provide these environment variables when the container is launched:

- `POOL`
- `WALLET`

## Notes

- This script is designed around Vast.ai rental pricing and GPU availability.
- It assumes a single-GPU target and a specific pool configuration.
- Mining profitability changes constantly; this script is only as good as the live market assumptions.
- You should review the code before using it to ensure the parameters match your intended setup.
- Use with caution, and only on infrastructure you are authorized to operate.

## Example flow

1. Paste your Vast.ai API key into `bot.py`
2. Set the target GPU and pool credentials
3. Run `python3 bot.py`
4. The script scans Vast.ai for cheap GPU offers
5. If the offer passes the profit threshold, it deploys the mining container
6. Mining starts and rewards are sent to the configured Kryptex wallet

## Disclaimer

This project is provided as-is for experimentation and personal infrastructure automation. Always verify pricing, pool settings, and rental costs before buying or deploying compute resources.
