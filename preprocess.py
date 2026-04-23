import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    # 1. Cleaning
    df = df.dropna()
    df['winner'] = (df['goals_a'] > df['goals_b']).astype(int)
    
   
    le = LabelEncoder()
    
    all_teams = pd.concat([df['team_a'], df['team_b']]).unique()
    le.fit(all_teams)
    
    df['team_a_encoded'] = le.transform(df['team_a'])
    df['team_b_encoded'] = le.transform(df['team_b'])
    
    if not os.path.exists('models'): os.makedirs('models')
    joblib.dump(le, 'models/team_encoder.pkl')
    
    # 4. Feature Selection
    features = [
        'team_a_encoded', 'team_b_encoded', 
        'form_a', 'form_b', 
        'avg_goals_scored_a', 'avg_goals_conceded_a',
        'avg_goals_scored_b', 'avg_goals_conceded_b',
        'h2h_winner_a', 'gd_form_a', 'gd_form_b'
    ]
    
    X = df[features]
    y = df['winner']
    
    return X, y, features

if __name__ == "__main__":
    if os.path.exists("data/matches1.csv"):
        X, y, feats = preprocess_data("data/matches1.csv")
        print(f"Preprocessing done. Features: {feats}")
        print(f"Sample X:\n{X.head()}")
    else:
        print("Error: Run dataset_builder.py first!")
