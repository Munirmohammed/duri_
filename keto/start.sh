#!/bin/bash

set -euo pipefail

keto migrate up -y
sleep 10

keto serve

