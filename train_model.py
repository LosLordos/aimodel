import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
import os
from preprocess import preprocess_data

def train():
    print("Loading and preprocessing data...")
    X, y, feature_names = preprocess_data("data/matches1.csv")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training model on {len(X_train)} samples with {len(feature_names)} features...")
    model = GradientBoostingClassifier(
        n_estimators=300, 
        learning_rate=0.03, 
        max_depth=4, 
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluation
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    cm = confusion_matrix(y_test, predictions)
    
    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {acc:.4f}")
    
   
    print("\n--- Feature Importance ---")
    importances = model.feature_importances_
    for name, importance in zip(feature_names, importances):
        print(f"{name}: {importance:.4f}")
        
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    # Save Model
    if not os.path.exists('models'): os.makedirs('models')
    joblib.dump(model, 'models/hockey_model.pkl')
    # Save feature names to ensure consistency in predict.py
    joblib.dump(feature_names, 'models/feature_names.pkl')
    print("\nModel saved to models/hockey_model.pkl")

if __name__ == "__main__":
    if os.path.exists("data/matches_1.csv"):
        train()
   
