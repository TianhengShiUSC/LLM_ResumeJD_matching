#!/bin/bash
#./rerun_failed_lines.sh pairs_labels_sample.txt
INPUT_FILE="$1"
FAILED_FILE="failed_lines.txt"

# 🛑 Check if the failed lines file exists
if [[ ! -f "$FAILED_FILE" ]]; then
  echo "❌ Failed lines file not found: $FAILED_FILE"
  exit 1
fi

# ✅ List of API keys (add or remove as needed)
API_KEYS=(
  "AIzaSyAn8g2wYgTrjfW52LrlhR6V37tDewRsO9g"
  "AIzaSyCqhPd6wk9WsphB3iAH5C1DlZ21ExKkKFY"
  "AIzaSyAMyzQFM2tqgD2irOvlFy0yCXznitBzx3Q"
  "AIzaSyADBstQ9m7ZX-JOCSJBKy82S_24FIy0StQ"
)

# 📦 Get the failed line numbers
failed_lines=$(cat "$FAILED_FILE")

# Initialize counter for API keys
key_counter=0

# Loop through each failed line
for line_number in $failed_lines; do
  # Get the content from the failed line using awk
  line=$(awk "NR==$line_number" "$INPUT_FILE")
  jd_path=$(echo "$line" | awk '{print $1}')
  resume_path=$(echo "$line" | awk '{print $2}')
  label=$(echo "$line" | awk '{print $3}')

  # Use the API key based on the counter, cycling through the keys
  current_key=${API_KEYS[$key_counter]}

  # Print which line we are processing
  echo "▶️ Rerunning Line $line_number: JD: $jd_path | Resume: $resume_path | Using Key: ${current_key:0:10}..."

  # Run the Python script again for the failed lines
  python app_offline.py --jd "$jd_path" --resume "$resume_path" --api_key "$current_key"

  # Increment and reset counter when it exceeds the number of API keys
  key_counter=$(( (key_counter + 1) % ${#API_KEYS[@]} ))
done
