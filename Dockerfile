FROM nvidia/cuda:12.4.1-devel-ubuntu22.04
RUN apt-get update && apt-get install -y wget curl git build-essential
WORKDIR /app
RUN git clone https://github.com . && \
    make CUDA=1

# We no longer hardcode values here. We use variables ($POOL and $WALLET)
RUN echo '#!/bin/bash\n\
./pearl-miner --pool "$POOL" --wallet "$WALLET" --rig-name vast-sniper\n\
' > /app/start_mining.sh && chmod +x /app/start_mining.sh

ENTRYPOINT ["/app/start_mining.sh"]
