"""
Model utilities for loading model and making predictions
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model


# Diagnosis class names
CLASS_NAMES = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']


def load_trained_model(model_path='model/model.h5'):
    """
    Load the pre-trained diabetic retinopathy model
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        model: Loaded Keras model
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    print(f"Loading model from {model_path}...")
    model = load_model(model_path)
    print("Model loaded successfully!")
    
    return model


def predict_single(model, image):
    """
    Make prediction for a single image
    
    Args:
        model: Trained Keras model
        image: Preprocessed image (normalized, shape: (height, width, 3))
        
    Returns:
        prediction: Dictionary with prediction results
    """
    # Add batch dimension if needed
    if len(image.shape) == 3:
        image = np.expand_dims(image, axis=0)
    
    # Get predictions
    probabilities = model.predict(image, verbose=0)[0]
    predicted_class = np.argmax(probabilities)
    confidence = probabilities[predicted_class]
    
    prediction = {
        'predicted_class': int(predicted_class),
        'predicted_label': CLASS_NAMES[predicted_class],
        'confidence': float(confidence),
        'probabilities': probabilities  # Return as numpy array for compatibility with visualization functions
    }
    
    return prediction


def predict_batch(model, images):
    """
    Make predictions for multiple images
    
    Args:
        model: Trained Keras model
        images: Batch of preprocessed images (shape: (batch_size, height, width, 3))
        
    Returns:
        predictions: List of prediction dictionaries
    """
    # Get predictions
    probabilities = model.predict(images, verbose=0)
    
    predictions = []
    for i in range(len(images)):
        predicted_class = np.argmax(probabilities[i])
        confidence = probabilities[i][predicted_class]
        
        prediction = {
            'predicted_class': int(predicted_class),
            'predicted_label': CLASS_NAMES[predicted_class],
            'confidence': float(confidence),
            'probabilities': {CLASS_NAMES[j]: float(probabilities[i][j]) for j in range(len(CLASS_NAMES))}
        }
        predictions.append(prediction)
    
    return predictions


def get_confidence_level(confidence):
    """
    Convert confidence score to human-readable level
    
    Args:
        confidence: Confidence score (0-1)
        
    Returns:
        level: String describing confidence level
    """
    if confidence >= 0.9:
        return "Very High"
    elif confidence >= 0.75:
        return "High"
    elif confidence >= 0.6:
        return "Medium"
    else:
        return "Low"


def get_recommendation(predicted_class, confidence):
    """
    Get recommendation based on prediction and confidence
    
    Args:
        predicted_class: Predicted class (0-4)
        confidence: Confidence score (0-1)
        
    Returns:
        recommendation: Dictionary with recommendations for nurses and patients
    """
    recommendations = {
        0: {  # No DR
            'nurse': 'Result indicates no diabetic retinopathy. Routine follow-up recommended.',
            'patient': 'Your eyes look healthy. Come back for another screening in 1 year.',
            'urgency': 'routine'
        },
        1: {  # Mild
            'nurse': 'Mild diabetic retinopathy detected. Recommend follow-up in 6-12 months.',
            'patient': 'Early signs detected. See an eye doctor within 6-12 months to monitor your eyes.',
            'urgency': 'monitor'
        },
        2: {  # Moderate
            'nurse': 'Moderate diabetic retinopathy. Refer to eye specialist within 3-6 months.',
            'patient': 'Your eyes need attention. See an eye doctor within 3-6 months for treatment.',
            'urgency': 'refer'
        },
        3: {  # Severe
            'nurse': 'Severe diabetic retinopathy. Urgent referral to eye specialist within 1-2 months.',
            'patient': 'Your eyes need urgent care. See an eye doctor within 1-2 months. Treatment can protect your vision.',
            'urgency': 'urgent'
        },
        4: {  # Proliferative DR
            'nurse': 'Proliferative diabetic retinopathy. Immediate referral to eye specialist (within 2 weeks).',
            'patient': 'Your eyes need immediate attention. See an eye doctor within 2 weeks. Early treatment is very important.',
            'urgency': 'immediate'
        }
    }
    
    recommendation = recommendations.get(predicted_class, recommendations[0])
    
    # Add confidence note
    if confidence < 0.7:
        recommendation['note'] = 'Low confidence - recommend manual review by specialist'
    elif confidence < 0.85:
        recommendation['note'] = 'Medium confidence - consider additional screening'
    else:
        recommendation['note'] = 'High confidence result'
    
    return recommendation


def interpret_prediction_simple(prediction):
    """
    Convert prediction to simple, plain language explanation
    
    Args:
        prediction: Prediction dictionary from predict_single()
        
    Returns:
        explanation: Simple text explanation (8th grade reading level)
    """
    predicted_class = prediction['predicted_class']
    confidence = prediction['confidence']
    
    # Convert confidence to percentage
    confidence_pct = int(confidence * 100)
    
    explanations = {
        0: f"Good news! The screening tool did not find signs of eye disease. The computer is {confidence_pct}% sure about this result.",
        1: f"The screening found early signs of eye disease. The computer is {confidence_pct}% sure. This means your eyes need to be checked again soon.",
        2: f"The screening found signs of eye disease that need attention. The computer is {confidence_pct}% sure. An eye doctor should examine your eyes within a few months.",
        3: f"The screening found serious signs of eye disease. The computer is {confidence_pct}% sure. You need to see an eye doctor soon for treatment.",
        4: f"The screening found advanced eye disease. The computer is {confidence_pct}% sure. It's very important to see an eye doctor right away for treatment."
    }
    
    explanation = explanations.get(predicted_class, explanations[0])
    
    # Add confidence warning if needed
    if confidence < 0.7:
        explanation += " Because the computer is less sure about this result, a nurse or doctor should double-check it."
    
    return explanation
