import joblib
import pandas as pd
import numpy as np
import os

class HockeyPredictor:
    def __init__(self):
        try:
            self.model = joblib.load('models/hockey_model.pkl')
            self.encoder = joblib.load('models/team_encoder.pkl')
            self.feature_names = joblib.load('models/feature_names.pkl')
            self.df_featured = pd.read_csv('data/matches1.csv')
        except FileNotFoundError:
            print("Error: Model or Data files not found. Please run training first.")
            exit(1)

    def get_latest_stats(self, team_name):
        
        team_matches = self.df_featured[
            (self.df_featured['team_a'] == team_name) | 
            (self.df_featured['team_b'] == team_name)
        ].sort_values('date', ascending=False)
        
        if team_matches.empty:
            return None
        
        latest = team_matches.iloc[0]
        if latest['team_a'] == team_name:
            return {
                'form': latest['form_a'],
                'avg_scored': latest['avg_goals_scored_a'],
                'avg_conceded': latest['avg_goals_conceded_a'],
                'gd_form': latest['gd_form_a']
            }
        else:
            return {
                'form': latest['form_b'],
                'avg_scored': latest['avg_goals_scored_b'],
                'avg_conceded': latest['avg_goals_conceded_b'],
                'gd_form': latest['gd_form_b']
            }

    def get_h2h_stat(self, team_a, team_b):
      
        h2h = self.df_featured[
            ((self.df_featured['team_a'] == team_a) & (self.df_featured['team_b'] == team_b)) |
            ((self.df_featured['team_a'] == team_b) & (self.df_featured['team_b'] == team_a))
        ]
        if h2h.empty:
            return 0.5
        
        results = []
        h2h_list = []
        for _, match in h2h.iterrows():
            
            if match['team_a'] == team_a:
                res = 1 if match['goals_a'] > match['goals_b'] else (0.5 if match['goals_a'] == match['goals_b'] else 0)
            else:
                res = 1 if match['goals_b'] > match['goals_a'] else (0.5 if match['goals_b'] == match['goals_a'] else 0)
            
            results.append(res)
            h2h_list.append({
                "date": match['date'].strftime('%Y-%m-%d') if hasattr(match['date'], 'strftime') else str(match['date']),
                "team_a": match['team_a'],
                "team_b": match['team_b'],
                "score": f"{match['goals_a']}:{match['goals_b']}"
            })
            
        return np.mean(results), len(h2h), h2h_list

    def predict_score(self, stats_a, stats_b):
       
        score_a = (stats_a['avg_scored'] + stats_b['avg_conceded']) / 2
        score_b = (stats_b['avg_scored'] + stats_a['avg_conceded']) / 2
        

        score_a *= (stats_a['form'] + 0.5)
        score_b *= (stats_b['form'] + 0.5)
        
        return round(score_a), round(score_b)

    def predict_winner(self, team_a, team_b):
       
        try:
            team_a_enc = self.encoder.transform([team_a])[0]
            team_b_enc = self.encoder.transform([team_b])[0]
        except ValueError:
            return f"Error: One of the teams ({team_a} or {team_b}) is not in the dataset."

        
        stats_a = self.get_latest_stats(team_a)
        stats_b = self.get_latest_stats(team_b)
        h2h_a, h2h_count, h2h_matches = self.get_h2h_stat(team_a, team_b)
        
        if not stats_a or not stats_b:
            return "Error: Could not find stats for these teams."

        
        input_data = pd.DataFrame([{
            'team_a_encoded': team_a_enc,
            'team_b_encoded': team_b_enc,
            'form_a': stats_a['form'],
            'form_b': stats_b['form'],
            'avg_goals_scored_a': stats_a['avg_scored'],
            'avg_goals_conceded_a': stats_a['avg_conceded'],
            'avg_goals_scored_b': stats_b['avg_scored'],
            'avg_goals_conceded_b': stats_b['avg_conceded'],
            'gd_form_a': stats_a['gd_form'],
            'gd_form_b': stats_b['gd_form'],
            'h2h_winner_a': h2h_a
        }])

      
        input_data = input_data[self.feature_names]
        
        prob = self.model.predict_proba(input_data)[0]
        prediction = self.model.predict(input_data)[0]
        
        winner = team_a if prediction == 1 else team_b
        confidence = prob[1] if prediction == 1 else prob[0]
        
       
        pred_goals_a, pred_goals_b = self.predict_score(stats_a, stats_b)
        
        return {
            "winner": winner,
            "confidence": f"{confidence*100:.2f}%",
            "team_a": team_a,
            "team_b": team_b,
            "stats_a": stats_a,
            "stats_b": stats_b,
            "h2h_win_rate": f"{h2h_a*100:.1f}%",
            "h2h_count": h2h_count,
            "h2h_matches": h2h_matches[:10], 
            "predicted_score": f"{pred_goals_a}:{pred_goals_b}"
        }

if __name__ == "__main__":
    predictor = HockeyPredictor()
    
    print("\n--- HockeyMatch AI Prediction ---")
    t1 = "HC Sparta Praha"
    t2 = "HC Oceláři Třinec"
    
    result = predictor.predict_winner(t1, t2)
    
    if isinstance(result, dict):
        print(f"\nZápas: {result['team_a']} vs {result['team_b']}")
        print(f"Predikovaný vítěz: {result['winner']}")
        print(f"Pravděpodobnost: {result['confidence']}")
        print(f"\nDetailní statistiky:")
        print(f"{t1}: Form {result['stats_a']['form']:.2f}, Avg Goals {result['stats_a']['avg_scored']:.2f}")
        print(f"{t2}: Form {result['stats_b']['form']:.2f}, Avg Goals {result['stats_b']['avg_scored']:.2f}")
    else:
        print(result)
