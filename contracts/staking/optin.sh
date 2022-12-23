#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# opt into created asset
goal app optin \
    --app-id "$APP_ID" \
    --from $CREATOR_ACCOUNT