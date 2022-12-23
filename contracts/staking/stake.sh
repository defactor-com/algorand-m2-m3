#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# create stake transaction
goal app call \
    --app-id "$APP_ID" \
    -f "$CREATOR_ACCOUNT" \
    --app-arg "str:stake" \
    --app-arg "int:0" \
    -o stake.tx

# create send currency transaction
goal asset send \
    -a "$STAKE_AMOUNT" \
    --assetid "$ASSET_INDEX" \
    -f "$CREATOR_ACCOUNT" \
    -t "$APP_ACCOUNT" \
    -o send-currency.tx

# group transactions
cat stake.tx send-currency.tx > stake-combined.tx
goal clerk group -i stake-combined.tx -o stake-grouped.tx
goal clerk split -i stake-grouped.tx -o stake-split.tx

# sign individual transactions
goal clerk sign -i stake-split-0.tx -o stake-signed-0.tx
goal clerk sign -i stake-split-1.tx -o stake-signed-1.tx

# re-combine individually signed transactions
cat stake-signed-0.tx stake-signed-1.tx > stake-signed-final.tx

# send transaction
goal clerk rawsend -f stake-signed-final.tx
