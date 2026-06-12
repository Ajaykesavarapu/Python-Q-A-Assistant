import pandas as pd
from app.utils.logger import logger

def load_and_join_datasets(questions_path: str, answers_path: str, tags_path: str = None) -> list:
    """
    Loads Stack Overflow Python Questions and Answers CSV datasets using pandas,
    joins them, filters based on scores, and compiles clean dictionary items.
    """
    logger.info(f"Loading Questions from {questions_path}...")
    df_q = pd.read_csv(questions_path)
    
    logger.info(f"Loading Answers from {answers_path}...")
    df_a = pd.read_csv(answers_path)
    
    # Cast IDs for merge safety
    df_q["Id"] = df_q["Id"].astype(int)
    df_a["ParentId"] = df_a["ParentId"].astype(int)
    df_a["Score"] = df_a["Score"].astype(int)
    df_q["Score"] = df_q["Score"].astype(int)
    
    # Filter answers with positive scores
    df_a_filtered = df_a[df_a["Score"] >= 0]
    
    # Select top/highest score answer for each Question ParentId
    # sorts by parent and score descending, then drops duplicates keeping the first (top score)
    df_a_top = df_a_filtered.sort_values(by=["ParentId", "Score"], ascending=[True, False]).drop_duplicates(subset=["ParentId"], keep="first")
    
    logger.info(f"Merging Questions with highest-scoring answers...")
    # Inner join on q.Id = a.ParentId
    merged = pd.merge(df_q, df_a_top, left_on="Id", right_on="ParentId", suffixes=("_q", "_a"))
    
    # Filter to questions with some activity score > 0
    merged = merged[(merged["Score_q"] > 0) | (merged["Score_a"] > 0)]
    
    # Read tags if available
    tags_dict = {}
    if tags_path:
        try:
            logger.info(f"Parsing Tags from {tags_path}...")
            df_tags = pd.read_csv(tags_path)
            # Group tags by question Id
            grouped_tags = df_tags.groupby("Id")["Tag"].apply(list).to_dict()
            tags_dict = grouped_tags
        except Exception as e:
            logger.warning(f"Could not load Tags dataset: {e}. Defaulting to empty tag lists.")

    qa_list = []
    for _, row in merged.iterrows():
        question_id = int(row["Id_q"])
        qa_list.append({
            "question_id": question_id,
            "answer_id": int(row["Id_a"]),
            "title": str(row["Title"]),
            "question_body": str(row["Body_q"]),
            "answer_body": str(row["Body_a"]),
            "question_score": int(row["Score_q"]),
            "answer_score": int(row["Score_a"]),
            "tags": tags_dict.get(question_id, ["python"])
        })
        
    return qa_list
