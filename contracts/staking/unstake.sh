#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# deploy app
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $ASSET_INDEX \
    --app-arg "str:unstake" \
    --app-arg "int:0" \
    --fee 2000