#!/bin/bash

# Path to input file (first argument to script)
INPUT_FILE="$1"

# Check if file exists
if [[ ! -f "$INPUT_FILE" ]]; then
  echo "❌ Input file not found: $INPUT_FILE"
  exit 1
fi

# Loop through each line in the input file
while IFS= read -r line || [[ -n "$line" ]]; do
  # Split line into parts
  jd_path=$(echo "$line" | awk '{print $1}')
  resume_path=$(echo "$line" | awk '{print $2}')
  label=$(echo "$line" | awk '{print $3}')

  echo "▶️ Processing JD: $jd_path | Resume: $resume_path | Label: $label"

  # Run Python script
  python app_offline.py --jd "$jd_path" --resume "$resume_path"

done < "$INPUT_FILE"
