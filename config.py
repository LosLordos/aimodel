import os

class Config:
    # App settings
    DEBUG = True
    PORT = 5001
    HOST = '127.0.0.1'
    
    # Data paths
    DATA_DIR = 'data'
    MODELS_DIR = 'models'
    
    MATCHES_FILE = os.path.join(DATA_DIR, 'matches1.csv')
    
    # Model filenames
    MODEL_FILE = os.path.join(MODELS_DIR, 'hockey_model.pkl')
    ENCODER_FILE = os.path.join(MODELS_DIR, 'team_encoder.pkl')
    FEATURES_FILE = os.path.join(MODELS_DIR, 'feature_names.pkl')
