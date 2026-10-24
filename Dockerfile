# Use a secure pre-configured graphics runtime environment
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# Install basic download utilities
RUN apt-get update && apt-get install -y wget xz-utils && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download the official, verified pre-compiled Linux release of SRBMiner
RUN wget https://github.com && \
    tar -xf SRBMiner-Multi-2-7-2-Linux.tar.xz --strip-components=1 && \
    rm SRBMiner-Multi-2-7-2-Linux.tar.xz

# Map structural runtime keys passed by your local python client bot
RUN echo '#!/bin/bash\n\
./SRBMiner-MULTI --algorithm pearlhash --pool "$POOL" --wallet "$WALLET" --password x\n\
' > /app/start_mining.sh && chmod +x /app/start_mining.sh

ENTRYPOINT ["/app/start_mining.sh"]
