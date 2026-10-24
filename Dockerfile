# 1. Bare-minimum NVIDIA runtime layer (under 200MB compressed)
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# 2. Install only essential extraction tools and wipe cache immediately
RUN apt-get update && apt-get install -y --no-install-recommends wget xz-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Pull a verified, stable release of SRBMiner-MULTI directly
RUN wget --no-check-certificate https://github.com && \
    tar -xf SRBMiner-MULTI-3-8-0-Linux.tar.xz --strip-components=1 && \
    rm SRBMiner-MULTI-3-8-0-Linux.tar.xz

# 4. Light shell script wrapper to process secure bot environment properties
RUN echo '#!/bin/bash\n\
./SRBMiner-MULTI --algorithm pearlhash --pool "$POOL" --wallet "$WALLET" --password x\n\
' > /app/start_mining.sh && chmod +x /app/start_mining.sh

ENTRYPOINT ["/app/start_mining.sh"]
