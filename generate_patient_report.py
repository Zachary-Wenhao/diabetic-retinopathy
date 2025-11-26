#!/usr/bin/env python3
"""
Quick script to generate HTML patient reports and optionally convert to PDF.
Usage: python generate_patient_report.py --patient_id <ID> --image_path <PATH>
"""

import argparse
import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image
import tensorflow as tf

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent / 'src'))

from html_generator import HTMLGenerator
from explanation_utils import ExplanationGenerator
from model_utils import ModelHandler
from data_utils import DataLoader

def load_and_preprocess_image(image_path):
    """Load and preprocess a single image for model prediction."""
    try:
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to model input size
        img = img.resize((224, 224))
        
        # Convert to numpy array and normalize
        img_array = np.array(img) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array, img
    
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None, None

def generate_single_patient_report(patient_id, image_path, age=None, gender=None):
    """
    Generate a complete patient report for a single patient.
    
    Args:
        patient_id (str): Unique identifier for patient
        image_path (str): Path to retinal image
        age (int, optional): Patient age
        gender (str, optional): Patient gender
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print(f"\n=== Generating Report for Patient {patient_id} ===")
    print(f"Image: {image_path}")
    
    try:
        # Check if required files exist
        model_path = "model.h5"
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False
        
        # Load model
        print("📥 Loading model...")
        model = tf.keras.models.load_model(model_path)
        
        # Load and preprocess image
        print("🖼️  Loading and preprocessing image...")
        img_array, original_img = load_and_preprocess_image(image_path)
        if img_array is None:
            return False
        
        # Make prediction
        print("🤖 Making prediction...")
        prediction = model.predict(img_array, verbose=0)
        predicted_class = np.argmax(prediction[0])
        confidence = np.max(prediction[0]) * 100
        
        # Class mapping
        class_names = {
            0: "No DR",
            1: "Mild DR", 
            2: "Moderate DR",
            3: "Severe DR",
            4: "Proliferative DR"
        }
        
        diagnosis = class_names.get(predicted_class, "Unknown")
        
        print(f"📊 Prediction: {diagnosis} (Confidence: {confidence:.1f}%)")
        
        # Initialize generators
        model_handler = ModelHandler()
        explanation_gen = ExplanationGenerator(model, model_handler)
        html_gen = HTMLGenerator()
        
        # Generate explanations (following 04_local_explanations.ipynb workflow)
        print("🔍 Generating Grad-CAM explanations...")
        try:
            # Use Grad-CAM (more reliable with TensorFlow 2.15)
            gradcam_heatmap = explanation_gen.generate_gradcam_visualization(
                img_array, predicted_class
            )
        except Exception as e:
            print(f"Warning: Grad-CAM visualization failed: {e}")
            gradcam_heatmap = None
        
        # Note: Following the notebook approach - Grad-CAM instead of SHAP for TF compatibility
        shap_values = None  # SHAP has compatibility issues with TF 2.15
        
        # Prepare patient data
        patient_data = {
            'patient_id': patient_id,
            'age': age or 'Unknown',
            'gender': gender or 'Unknown',
            'diagnosis': diagnosis,
            'confidence': confidence,
            'predicted_class': predicted_class,
            'all_probabilities': prediction[0]
        }
        
        # Generate HTML report
        print("📄 Creating HTML report...")
        report_path = html_gen.create_patient_report(
            patient_data=patient_data,
            original_image=original_img,
            processed_image=img_array[0],
            shap_values=shap_values,
            gradcam_heatmap=gradcam_heatmap,
            output_dir="outputs/patient_reports"
        )
        
        if report_path:
            print(f"✅ Report generated successfully!")
            print(f"📍 HTML Report: {report_path}")
            print(f"📍 Visualizations saved in: outputs/patient_reports/")
            return True
        else:
            print("❌ Failed to generate HTML report")
            return False
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Generate patient explanation reports from retinal images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python generate_patient_report.py --patient_id P123 --image_path images/retinal_scan.jpg
    python generate_patient_report.py --patient_id P456 --image_path scan.png --age 65 --gender Female
    python generate_patient_report.py --patient_id P789 --image_path folder/image.jpg --pdf
        '''
    )
    
    parser.add_argument('--patient_id', required=True,
                       help='Unique identifier for the patient')
    
    parser.add_argument('--image_path', required=True,
                       help='Path to the retinal image file (JPG/PNG)')
    
    parser.add_argument('--age', type=int,
                       help='Patient age (optional)')
    
    parser.add_argument('--gender', choices=['Male', 'Female', 'Other'],
                       help='Patient gender (optional)')
    
    parser.add_argument('--pdf', action='store_true',
                       help='Also generate/update explanation_local.pdf')
    
    args = parser.parse_args()
    
    print("🏥 Diabetic Retinopathy Patient Report Generator")
    print("=" * 50)
    
    # Generate the report
    success = generate_single_patient_report(
        patient_id=args.patient_id,
        image_path=args.image_path,
        age=args.age,
        gender=args.gender
    )
    
    if success and args.pdf:
        print("\n📄 Updating explanation_local.pdf...")
        try:
            # Import and run PDF generation
            import subprocess
            result = subprocess.run([
                sys.executable, "generate_local_pdf_from_html.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PDF updated successfully!")
            else:
                print(f"❌ PDF generation failed: {result.stderr}")
        
        except Exception as e:
            print(f"❌ Error updating PDF: {e}")
    
    if success:
        print("\n🎉 Report generation completed!")
        print("\n📋 Next Steps:")
        print("   • Review the HTML report for accuracy")
        print("   • Check generated visualizations")
        print("   • Validate results with medical professionals")
        if not args.pdf:
            print("   • Run with --pdf flag to update explanation_local.pdf")
    else:
        print("\n❌ Report generation failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()