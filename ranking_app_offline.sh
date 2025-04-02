#!/bin/bash

INPUT_FILE="$1"

# 🛑 Check if input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
  echo "❌ Input file not found: $INPUT_FILE"
  exit 1
fi

# ✅ List of API keys (add or remove as needed)
API_KEYS=(
  "AIzaSyAn8g2wYgTrjfW52LrlhR6V37tDewRsO9g"
  "AIzaSyCqhPd6wk9WsphB3iAH5C1DlZ21ExKkKFY"
  "AIzaSyAMyzQFM2tqgD2irOvlFy0yCXznitBzx3Q"
  "AIzaSyADBstQ9m7ZX-JOCSJBKy82S_24FIy0StQ"
)

NUM_KEYS=${#API_KEYS[@]}
COUNTER=0

# 📦 Process each line
while IFS= read -r line || [[ -n "$line" ]]; do
  jd_path=$(echo "$line" | awk '{print $1}')
  resume_path=$(echo "$line" | awk '{print $2}')

  current_key=${API_KEYS[$((COUNTER % NUM_KEYS))]}

  echo "▶️ [$COUNTER] Processing JD: $jd_path | Resume: $resume_path | Using Key: ${current_key:0:10}..."

  python app_offline.py --jd "$jd_path" --resume "$resume_path" --api_key "$current_key"

  ((COUNTER++))

done < "$INPUT_FILE"
