#!/usr/bin/env python3
"""
Regenerate patient reports with improved HTML formatting
"""

import sys
import os
sys.path.append('.')

import numpy as np
import pandas as pd
from src.data_utils import load_data, load_image
from src.model_utils import load_trained_model, predict_single, CLASS_NAMES
from src.explanation_utils import get_gradcam_heatmap, overlay_heatmap, generate_confidence_chart, create_simple_heatmap_overlay
from src.html_generator import generate_patient_report_html
import matplotlib.pyplot as plt

def generate_patient_explanation_text(patient_info, predicted_class, confidence, probabilities):
    """Generate plain language explanation (8th grade level)"""
    
    diagnosis_name = CLASS_NAMES[predicted_class]
    confidence_pct = int(confidence * 100)
    patient_age = patient_info['age']
    patient_gender = "male" if patient_info['gender'] == 'M' else "female"
    
    # Intro
    text = f"EYE SCREENING REPORT\n"
    text += f"{'='*60}\n\n"
    text += f"Patient Information:\n"
    text += f"• Age: {patient_age} years old\n"
    text += f"• Gender: {patient_gender.capitalize()}\n"
    text += f"• Screening Date: Today\n\n"
    
    # Main finding
    text += f"WHAT WE FOUND\n"
    text += f"{'-'*60}\n\n"
    
    if predicted_class == 0:
        text += f"✓ Good News: No Signs of Eye Disease Found\n\n"
        text += f"The computer screening tool looked at your eye photo carefully. "
        text += f"It checked your blood vessels and other parts of your eye. "
        text += f"Everything looks healthy and normal.\n\n"
    elif predicted_class == 1:
        text += f"⚠ Early Signs Detected: Mild Changes\n\n"
        text += f"The computer found some early changes in your eye. "
        text += f"These are small signs that your eye doctor should check. "
        text += f"Finding these early is good because treatment works best when started early.\n\n"
    elif predicted_class == 2:
        text += f"⚠ Moderate Changes Detected\n\n"
        text += f"The computer found changes in your eye that need attention from an eye doctor. "
        text += f"There are signs of blood vessel damage. "
        text += f"This doesn't mean you're going blind, but you should see a specialist soon.\n\n"
    elif predicted_class == 3:
        text += f"⚠️ Severe Changes Detected\n\n"
        text += f"The computer found serious changes in your eye. "
        text += f"Your blood vessels show significant damage that needs treatment. "
        text += f"Please see an eye doctor as soon as possible.\n\n"
    else:  # Class 4
        text += f"⚠️ Advanced Changes Detected\n\n"
        text += f"The computer found advanced changes in your eye. "
        text += f"There is serious blood vessel damage that needs immediate medical attention. "
        text += f"Please contact an eye doctor right away.\n\n"
    
    # Confidence
    text += f"HOW SURE IS THE COMPUTER?\n"
    text += f"{'-'*60}\n\n"
    text += f"The computer is {confidence_pct}% confident about this result.\n\n"
    
    if confidence >= 0.9:
        text += f"This is a high confidence score. The computer is very sure about what it saw.\n\n"
    elif confidence >= 0.7:
        text += f"This is a medium confidence score. The computer is fairly sure, but not certain.\n\n"
    else:
        text += f"This is a lower confidence score. The computer is less sure about this result. "
        text += f"An eye doctor should definitely review your case.\n\n"
    
    # What the computer looked at
    text += f"HOW THE COMPUTER ANALYZES YOUR EYE\n"
    text += f"{'-'*60}\n\n"
    text += f"The computer uses a technique called 'Grad-CAM' to highlight areas that help it make decisions. "
    text += f"This shows which parts of your eye it focused on:\n\n"
    text += f"• Blood vessels and their patterns\n"
    text += f"• Areas that might show bleeding or fluid leakage\n"
    text += f"• Changes in the retina structure\n"
    text += f"• Overall eye health indicators\n\n"
    text += f"The colored highlight areas in your report show where the computer 'looked' most carefully.\n\n"
    
    # What to do next
    text += f"WHAT TO DO NEXT\n"
    text += f"{'-'*60}\n\n"
    
    if predicted_class == 0:
        text += f"✓ Come back for another screening in 1 year\n"
        text += f"✓ Keep managing your diabetes with your regular doctor\n"
        text += f"✓ Tell your doctor right away if your vision changes\n"
        text += f"✓ Control your blood sugar, blood pressure, and cholesterol\n\n"
    else:
        text += f"⚠ See an eye specialist (ophthalmologist) for a complete exam\n"
        if predicted_class >= 3:
            text += f"⚠ Do this as soon as possible - within the next few days\n"
        else:
            text += f"⚠ Do this within the next few weeks\n"
        text += f"✓ Keep managing your diabetes with your regular doctor\n"
        text += f"✓ Control your blood sugar - this is very important!\n"
        text += f"✓ Tell your doctor if you notice any vision changes\n\n"
    
    # Important reminders
    text += f"IMPORTANT REMINDERS\n"
    text += f"{'-'*60}\n\n"
    text += f"• This is a SCREENING tool, not a final diagnosis\n"
    text += f"• Only a real eye doctor can give you a complete diagnosis\n"
    text += f"• This tool helps find people who need to see a specialist\n"
    text += f"• Even if the result is good, see an eye doctor regularly\n"
    text += f"• Managing your diabetes is the best way to protect your eyes\n\n"
    
    # Confidence breakdown
    text += f"DETAILED CONFIDENCE SCORES\n"
    text += f"{'-'*60}\n\n"
    text += f"How confident the computer is for each possibility:\n\n"
    
    for i, class_name in enumerate(CLASS_NAMES):
        prob = probabilities[i] * 100
        text += f"  {class_name:.<40} {prob:>5.1f}%\n"
    
    text += f"\n{'='*60}\n"
    
    return text

def regenerate_patient_reports():
    """Regenerate both patient reports with improved formatting."""
    
    print("🔄 Regenerating Patient Reports with Improved Formatting")
    print("=" * 60)
    
    # Load data and model
    print("📥 Loading model and data...")
    model = load_trained_model('model/model.h5')
    train_df, test_df = load_data('data')
    
    # Select the same patients as before
    print("👥 Selecting patients...")
    np.random.seed(42)
    
    # Patient 1: No DR (healthy)
    patient1_candidates = test_df[test_df['diagnosis'] == 0]
    patient1_info = patient1_candidates.sample(1, random_state=42).iloc[0]
    
    # Patient 2: Disease detected
    patient2_candidates = test_df[test_df['diagnosis'].isin([2, 3, 4])]
    patient2_info = patient2_candidates.sample(1, random_state=42).iloc[0]
    
    output_dir = 'outputs/patient_reports'
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, patient_info in enumerate([patient1_info, patient2_info], 1):
        print(f"\n🏥 Generating Report for Patient {idx}")
        print("-" * 40)
        
        patient_id = patient_info['id_code']
        print(f"Patient ID: {patient_id}")
        
        # Load image and predict
        image = load_image(patient_id, 'data/test_images')
        prediction = predict_single(model, image)
        
        predicted_class = prediction['predicted_class']
        confidence = prediction['confidence']
        all_probabilities = prediction['probabilities']
        
        print(f"Prediction: {CLASS_NAMES[predicted_class]} ({confidence:.1%} confidence)")
        
        # Generate visualizations
        print("🎨 Creating visualizations...")
        
        # Confidence chart
        conf_fig = generate_confidence_chart(
            all_probabilities,
            CLASS_NAMES,
            save_path=f'{output_dir}/patient{idx}_confidence.png'
        )
        plt.close(conf_fig)
        
        # Simple overlay
        simple_fig = create_simple_heatmap_overlay(
            model, 
            image,
            title="What the Computer Saw in Your Eye Photo",
            save_path=f'{output_dir}/patient{idx}_simple_overlay.png'
        )
        plt.close(simple_fig)
        
        # Generate explanation text
        print("📝 Creating explanation...")
        explanation_text = generate_patient_explanation_text(
            patient_info, predicted_class, confidence, all_probabilities
        )
        
        # Generate HTML report with improved formatting
        print("📄 Generating HTML report...")
        html_path = generate_patient_report_html(
            patient_info=patient_info,
            prediction=prediction,
            explanation_text=explanation_text,
            image_paths={
                'original': f'patient{idx}_simple_overlay.png',
                'confidence': f'patient{idx}_confidence.png'
            },
            output_path=f'{output_dir}/patient{idx}_report.html'
        )
        
        print(f"✅ Report saved: {html_path}")
    
    print(f"\n🎉 All reports regenerated successfully!")
    print(f"📍 Location: {output_dir}/")

if __name__ == "__main__":
    regenerate_patient_reports()