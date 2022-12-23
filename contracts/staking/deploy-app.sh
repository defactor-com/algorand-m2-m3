#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# deploy app
goal app create \
  --creator $CREATOR_ACCOUNT \
  --global-byteslices 1 \
  --global-ints 0 \
  --local-byteslices 4 \
  --local-ints 0 \
  --approval-prog /data/build/approval.teal \
  --clear-prog /data/build/clear.teal