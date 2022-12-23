#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# optin FACTR
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $ASSET_INDEX \
    --fee 2000 \
    --app-arg "str:optinFT"

# optin USDC
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $USDC_INDEX \
    --fee 2000 \
    --app-arg "str:optinFT"

# optin 1
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $INDEX_1 \
    --fee 2000 \
    --app-arg "str:optinFT"

# optin 2
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $INDEX_2 \
    --fee 2000 \
    --app-arg "str:optinFT"

# optin 3
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $INDEX_3 \
    --fee 2000 \
    --app-arg "str:optinFT"

# optin 4
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --foreign-asset $INDEX_4 \
    --fee 2000 \
    --app-arg "str:optinFT"