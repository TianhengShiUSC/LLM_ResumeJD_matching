import os
import json
import re

def extract_jd_match(folder_path):
    jd_groups = {}
    jd_titles = {
        "JD33": "Software Engineer",
        "JD55": "Sales",
        "JD57": "Account Executive",
        "JD264": "Talent Acquisition Specialist / Recruiter",
        "JD489": "Nursing Assistant"
    }
    
    # Iterate through all JSON files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            match = re.match(r'(JD\d+)_resume\d+\.json', file_name)
            if match:
                jd_number = match.group(1)
                
                # Read JSON file
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Extract JD Match percentage
                    response_text = data.get("response", "")
                    match_percentage = re.search(r'"JD Match":\s*"?(\d+)"?', response_text)
                    if match_percentage:
                        match_value = int(match_percentage.group(1)) / 100  # Convert to decimal
                        
                        # Store as dictionary with file path as key
                        if jd_number not in jd_groups:
                            jd_groups[jd_number] = {}
                        jd_groups[jd_number][file_path] = match_value
    
    # Sort dictionary values by percentage within each JD group
    for jd in jd_groups:
        jd_groups[jd] = dict(sorted(jd_groups[jd].items(), key=lambda item: item[1]))
    
    jd_match_groups = dict(sorted(jd_groups.items(), key=lambda item: int(item[0][2:])))
    
    # Print results
    for jd, matches in jd_match_groups.items():
        print(f"{jd} ({jd_titles.get(jd, 'Unknown')}): {matches}")
    
    # Print JD titles at the end
    print("\nJob Titles:")
    for jd, title in jd_titles.items():
        print(f"{jd}: {title}")

# Example usage
folder_path = "output"  # Change this to your actual folder path
extract_jd_match(folder_path)


# JD33 = software engineer
# JD55 = sales
# JD57 = account executive
# JD264 = talent acquisition specialist  recruiter
# JD489 = nursing assistant