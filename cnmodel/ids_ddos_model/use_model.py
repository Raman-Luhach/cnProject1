# use_model.py - DDoS/DoS Detection Model
import numpy as np
import pandas as pd
import pickle
import json
import warnings
from tensorflow import keras
import tensorflow as tf
import os

# Suppress sklearn version warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='X has feature names')

class IDSModel:
    def __init__(self, model_dir='.'):
        """Initialize IDS model with all components"""
        print("Loading DDoS/DoS Detection Model...")
        
        # Try loading model in order of preference
        keras_path = os.path.join(model_dir, 'ids_model.keras')
        savedmodel_path = os.path.join(model_dir, 'ids_model_savedmodel')
        h5_path = os.path.join(model_dir, 'ids_model.h5')
        
        model_loaded = False
        
        # Try .keras format first (Keras 3 native)
        if os.path.exists(keras_path):
            try:
                self.model = keras.models.load_model(keras_path)
                print(f"✅ Model loaded (.keras format)")
                model_loaded = True
            except Exception as e:
                print(f"⚠️  .keras load failed: {str(e)[:100]}")
        
        # Try SavedModel format
        if os.path.exists(savedmodel_path) and not model_loaded:
            try:
                saved_model = tf.saved_model.load(savedmodel_path)
                self.model = saved_model.signatures['serve']
                print(f"✅ Model loaded (SavedModel format)")
                model_loaded = True
                self.model_type = 'savedmodel'
            except Exception as e:
                print(f"⚠️  SavedModel load failed: {str(e)[:100]}")
        
        # Try .h5 format
        if os.path.exists(h5_path) and not model_loaded:
            try:
                self.model = keras.models.load_model(h5_path, compile=False)
                self.model.compile(
                    optimizer=keras.optimizers.Adam(learning_rate=1e-4),
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                print(f"✅ Model loaded (.h5 format)")
                model_loaded = True
            except Exception as e:
                print(f"⚠️  .h5 load failed: {str(e)[:100]}")
        
        if not model_loaded:
            raise Exception("Could not load model in any format!")
        
        if not hasattr(self, 'model_type'):
            self.model_type = 'keras_model'
        
        # Load preprocessing objects
        with open(os.path.join(model_dir, 'scaler.pkl'), 'rb') as f:
            self.scaler = pickle.load(f)
        print("✅ Scaler loaded")
        
        with open(os.path.join(model_dir, 'encoder.pkl'), 'rb') as f:
            self.encoder = pickle.load(f)
        print("✅ Encoder loaded")
        
        with open(os.path.join(model_dir, 'selector.pkl'), 'rb') as f:
            self.selector = pickle.load(f)
        print("✅ Selector loaded")
        
        # Load metadata
        with open(os.path.join(model_dir, 'model_metadata.json'), 'r') as f:
            self.metadata = json.load(f)
        
        self.class_names = self.metadata['class_names']
        print(f"✅ Model ready! Detects {len(self.class_names)} attack types")
    
    def predict(self, features_df):
        """Make predictions on new data"""
        # Remove Label column if present
        if 'Label' in features_df.columns:
            X = features_df.drop('Label', axis=1)
        else:
            X = features_df
        
        # Convert DataFrame to numpy array to avoid feature name warnings
        # Selector expects array, not DataFrame with column names
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # Suppress warnings for this operation
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
            warnings.filterwarnings('ignore', message='X has feature names')
            # Apply preprocessing
            X_selected = self.selector.transform(X)
        
        X_scaled = self.scaler.transform(X_selected)
        X_cnn = X_scaled[..., np.newaxis]
        
        # Predict
        if self.model_type == 'savedmodel':
            probabilities = self.model(tf.constant(X_cnn, dtype=tf.float32)).numpy()
        else:
            probabilities = self.model.predict(X_cnn, verbose=0)
        
        # Get predicted classes
        predicted_indices = np.argmax(probabilities, axis=1)
        predictions = [self.class_names[idx] for idx in predicted_indices]
        
        return predictions, probabilities

# Example usage
if __name__ == "__main__":
    # Load model
    ids = IDSModel('.')
    
    # Example: Make predictions (replace with your data)
    # test_data = pd.read_csv('test_data.csv')
    # predictions, probabilities = ids.predict(test_data)
    # print(f"Predictions: {predictions}")
