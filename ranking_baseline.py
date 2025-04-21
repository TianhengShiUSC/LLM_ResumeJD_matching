import os
import json
import re
import numpy as np
from collections import defaultdict
from sklearn.metrics import ndcg_score

def evaluate_jd_matching(folder_path):
    # Ground truth manual rankings
    ground_truth = {
        "JD33": {
            "resume1693": 10, "resume1697": 7, "resume1698": 6, "resume1699": 8,
            "resume1700": 5, "resume1701": 9, "resume1710": 3, "resume1713": 4,
            "resume1745": 1, "resume1747": 2
        },
        "JD55": {
            "resume968": 6, "resume1000": 2, "resume1002": 8, "resume1011": 1,
            "resume1025": 4, "resume1037": 7, "resume1051": 9, "resume1073": 10,
            "resume1083": 5, "resume1101": 3
        },
        "JD57": {
            "resume1824": 1, "resume1828": 2, "resume1830": 6, "resume1838": 3,
            "resume1851": 5, "resume1865": 10, "resume1878": 4, "resume1880": 9,
            "resume1891": 8, "resume1910": 7
        },
        "JD264": {
            "resume1": 6, "resume2": 5, "resume3": 10, "resume4": 1,
            "resume5": 9, "resume6": 7, "resume7": 2, "resume8": 3,
            "resume9": 8, "resume10": 4
        },
        "JD489": {
            "resume551": 5, "resume690": 4, "resume692": 1, "resume694": 6,
            "resume695": 10, "resume696": 2, "resume698": 7, "resume699": 8,
            "resume700": 9, "resume720": 3
        }
    }

    jd_titles = {
        "JD33": "Software Engineer",
        "JD55": "Sales",
        "JD57": "Account Executive",
        "JD264": "Talent Acquisition Specialist",
        "JD489": "Nursing Assistant"
    }

    # Process LLM matching results
    llm_results = defaultdict(dict)
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            match = re.match(r'(JD\d+)_resume(\d+)', file_name)
            if match:
                jd_number, resume_num = match.groups()
                resume_id = f"resume{resume_num}"
                file_path = os.path.join(folder_path, file_name)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    response_text = data.get("response", "")
                    
                    # Debugging print to show the raw JSON response
                    print(f"Processing file: {file_name}")
                    print(f"Response Text: {response_text[:300]}...")  # Preview first 300 chars
                    
                    match_percentage = re.search(r'"JD Match":\s*"?(\d+)%?', response_text)
                    if match_percentage:
                        match_value = int(match_percentage.group(1)) / 100
                        print(f"Match percentage found: {match_value}")
                        llm_results[jd_number][resume_id] = match_value
                    else:
                        print(f"JD Match not found for {file_name}")

    # Evaluate performance for each JD
    evaluation_results = {}
    for jd in ground_truth:
        if jd not in llm_results:
            continue
            
        # Get common resumes between ground truth and LLM results
        common_resumes = set(ground_truth[jd].keys()) & set(llm_results[jd].keys())
        if not common_resumes:
            continue
        
        # Prepare data for metrics calculation
        gt_ranks = []
        llm_scores = []
        resume_list = []
        
        for resume in common_resumes:
            # Convert ground truth rank to relevance score (lower rank = better)
            gt_rank = ground_truth[jd][resume]
            gt_relevance = 11 - gt_rank  # Convert rank to relevance (1-10 scale)
            
            gt_ranks.append(gt_relevance)
            llm_scores.append(llm_results[jd][resume])
            resume_list.append(resume)
        
        # Calculate metrics
        spearman_corr = np.corrcoef(gt_ranks, llm_scores)[0, 1]
        ndcg = ndcg_score([gt_ranks], [llm_scores])
        
        # Sort resumes by both ground truth and LLM scores for comparison
        gt_sorted = sorted([(resume, gt_rank) for resume, gt_rank in ground_truth[jd].items() 
                          if resume in common_resumes], key=lambda x: x[1])
        llm_sorted = sorted([(resume, score) for resume, score in llm_results[jd].items() 
                           if resume in common_resumes], key=lambda x: -x[1])
        
        evaluation_results[jd] = {
            'title': jd_titles[jd],
            'spearman': spearman_corr,
            'ndcg': ndcg,
            'ground_truth_top3': [r[0] for r in gt_sorted[:3]],
            'llm_top3': [r[0] for r in llm_sorted[:3]],
            'agreement_top3': len(set(gt_sorted[:3][0]) & set(llm_sorted[:3][0])),
            'num_resumes': len(common_resumes)
        }

    # Print evaluation results
    print("="*80)
    print("LLM MATCHING PERFORMANCE EVALUATION".center(80))
    print("="*80)
    print(f"{'JD':<6} {'Title':<25} {'Resumes':>8} {'Spearman':>10} {'NDCG':>8} {'Top3 Agreement':>15}")
    
    for jd in sorted(evaluation_results.keys(), key=lambda x: int(x[2:])): 
        data = evaluation_results[jd]
        print(f"{jd:<6} {data['title'][:25]:<25} {data['num_resumes']:>8} "
              f"{data['spearman']:>10.2f} {data['ndcg']:>8.2f} "
              f"{data['agreement_top3']:>15}")

    # Print detailed comparison for each JD
    print("\n\nDETAILED COMPARISON BY JD:")
    for jd in sorted(evaluation_results.keys(), key=lambda x: int(x[2:])): 
        data = evaluation_results[jd]
        print(f"\n{jd} ({data['title']}) - Spearman: {data['spearman']:.2f}, NDCG: {data['ndcg']:.2f}")
        print("Ground Truth Top 3:", ", ".join(data['ground_truth_top3']))
        print("LLM Predicted Top 3:", ", ".join(data['llm_top3']))

if __name__ == "__main__":
    folder_path = r"D:\VScode\Code\CSCI544\ResumeJDProject\LLM_ResumeJD_matching\output_baseline"  # Change to your folder path
    evaluate_jd_matching(folder_path)
