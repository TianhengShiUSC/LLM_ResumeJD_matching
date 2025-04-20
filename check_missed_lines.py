import os

# Path to the input text file and output JSON directory
input_file = '/Users/tianhengshi/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro/pairs_labels_sample.txt'
output_dir = 'output'  # Adjust this to your actual output directory

# Read all lines from pairs_labels_sample.txt
with open(input_file, 'r') as f:
    lines = f.readlines()

# Get the corresponding filenames from the lines (e.g., JD790_resume1353.json)
expected_files = [
    f"{line.split()[0].split('/')[-1].replace('.txt', '')}_{line.split()[1].split('/')[-1].replace('.pdf', '')}.json"
    for line in lines
]

# Check if each expected file exists
missing_files = [file for file in expected_files if not os.path.exists(os.path.join(output_dir, file))]
missing_jsons = []

# Print the lines that are missing corresponding JSON files
count = 0
if missing_files:
    print("Missing JSON files for the following lines:")
    for file in missing_files:
        count+=1
        print(file)
        missing_jsons.append(file)
else:
    print("All JSON files are present.")

print("Number of missing jsons:", count)

# Read the lines from ranking.txt
input_file = '/Users/tianhengshi/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro/pairs_labels_sample.txt'
with open(input_file, 'r') as f:
    lines = f.readlines()

# Create a mapping of filenames to their line index in ranking.txt
line_to_filename = {
    f"{line.split()[0].split('/')[-1].replace('.txt', '')}_{line.split()[1].split('/')[-1].replace('.pdf', '')}.json": index
    for index, line in enumerate(lines)
}

# Get the indexes of the lines corresponding to the missing JSON files
missing_line_indexes = [line_to_filename[missing_json] for missing_json in missing_jsons]

# Output the missing line indexes
print("Missing line indexes in pairs_labels_sample.txt:")
for index in missing_line_indexes:
    print(index + 1)  # Adding 1 to make the line index 1-based (for human readability)
print("Copy and paste those to failed_lines.txt and run rerun_failed_lines.sh")
