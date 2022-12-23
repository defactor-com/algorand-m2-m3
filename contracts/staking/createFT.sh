#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# create FT
goal asset create \
    --creator "$CREATOR_ACCOUNT" \
    --total 10000000000000000000 \
    --decimals 10