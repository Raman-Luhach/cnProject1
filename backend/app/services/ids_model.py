"""IDS Model service - loads trained model and performs inference"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

# Add model directory to path
from app.config import MODEL_DIR
sys.path.insert(0, str(MODEL_DIR))

from use_model import IDSModel

logger = logging.getLogger(__name__)


class IDSModelService:
    """Service for IDS model inference"""
    
    def __init__(self, model_dir: Path = MODEL_DIR):
        self.model_dir = model_dir
        self.model = None
        self.is_loaded = False
        
    def load_model(self):
        """Load the trained IDS model"""
        try:
            logger.info(f"Loading IDS model from {self.model_dir}")
            self.model = IDSModel(str(self.model_dir))
            self.is_loaded = True
            logger.info("IDS model loaded successfully")
            logger.info(f"Model detects {len(self.model.class_names)} attack types")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False
            return False
    
    def predict(self, features_df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
        """
        Make predictions on features
        
        Args:
            features_df: DataFrame with 82 features (will be reduced to 68 by selector)
        
        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if features_df.empty:
            return [], np.array([])
        
        try:
            predictions, probabilities = self.model.predict(features_df)
            return predictions, probabilities
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    def predict_single(self, features_dict: Dict[str, float]) -> Tuple[str, float, np.ndarray]:
        """
        Make prediction for single flow
        
        Returns:
            Tuple of (prediction, confidence, probabilities)
        """
        # Convert dict to DataFrame
        df = pd.DataFrame([features_dict])
        
        predictions, probabilities = self.predict(df)
        
        if len(predictions) > 0:
            prediction = predictions[0]
            confidence = float(np.max(probabilities[0]))
            probs = probabilities[0]
            return prediction, confidence, probs
        else:
            return "Unknown", 0.0, np.array([])
    
    def get_class_names(self) -> List[str]:
        """Get list of attack class names"""
        if not self.is_loaded:
            return []
        return self.model.class_names
    
    def is_attack(self, prediction: str) -> bool:
        """Check if prediction is an attack (not Benign)"""
        return prediction != "Benign"
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        if not self.is_loaded:
            return {
                'loaded': False,
                'error': 'Model not loaded'
            }
        
        return {
            'loaded': True,
            'model_type': self.model.metadata.get('model_type', 'Unknown'),
            'num_classes': len(self.model.class_names),
            'class_names': self.model.class_names,
            'feature_count': self.model.metadata.get('feature_count', 0),
            'accuracy': self.model.metadata.get('metrics', {}).get('accuracy', 0),
            'training_date': self.model.metadata.get('training_date', 'Unknown')
        }


# Global model service instance
_model_service = None


def get_model_service() -> IDSModelService:
    """Get or create global model service instance"""
    global _model_service
    if _model_service is None:
        _model_service = IDSModelService()
        _model_service.load_model()
    return _model_service

