"""
Data utilities for loading and processing diabetic retinopathy data
"""

import os
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt


# Diagnosis mapping
DIAGNOSIS_LABELS = {
    0: 'No DR',
    1: 'Mild',
    2: 'Moderate', 
    3: 'Severe',
    4: 'Proliferative DR'
}

DIAGNOSIS_DESCRIPTIONS = {
    0: 'No signs of eye disease',
    1: 'Mild eye disease detected',
    2: 'Moderate eye disease detected',
    3: 'Severe eye disease detected', 
    4: 'Advanced eye disease detected'
}


def load_data(data_dir='data'):
    """
    Load train and test CSV files
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        train_df, test_df: DataFrames with patient information
    """
    train_df = pd.read_csv(os.path.join(data_dir, 'train.csv'))
    test_df = pd.read_csv(os.path.join(data_dir, 'test.csv'))
    
    return train_df, test_df


def load_image(image_id, image_dir, target_size=(320, 320), add_png=True):
    """
    Load and preprocess a single retinal image
    
    Args:
        image_id: ID of the image (without .png extension)
        image_dir: Directory containing images
        target_size: Tuple of (height, width) to resize image
        add_png: Whether to add .png extension to image_id
        
    Returns:
        image: Preprocessed image as numpy array (normalized 0-1)
    """
    if add_png and not image_id.endswith('.png'):
        image_id = f"{image_id}.png"
    
    image_path = os.path.join(image_dir, image_id)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image
    image = Image.open(image_path).convert('RGB')
    
    # Resize
    image = image.resize(target_size)
    
    # Convert to numpy array and normalize
    image = np.array(image) / 255.0
    
    return image


# Alias for consistency with notebook code
load_single_image = load_image


def load_batch_images(image_ids, image_dir, target_size=(320, 320)):
    """
    Load multiple images as a batch
    
    Args:
        image_ids: List of image IDs
        image_dir: Directory containing images
        target_size: Tuple of (height, width)
        
    Returns:
        images: Numpy array of shape (batch_size, height, width, 3)
    """
    images = []
    for image_id in image_ids:
        try:
            img = load_image(image_id, image_dir, target_size)
            images.append(img)
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            continue
    
    return np.array(images)


def get_class_distribution(df):
    """
    Get distribution of diagnosis classes
    
    Args:
        df: DataFrame with 'diagnosis' column
        
    Returns:
        distribution: Dictionary with counts per class
    """
    distribution = df['diagnosis'].value_counts().sort_index().to_dict()
    return distribution


def get_demographic_stats(df):
    """
    Get demographic statistics from the dataset
    
    Args:
        df: DataFrame with patient information
        
    Returns:
        stats: Dictionary with demographic statistics
    """
    stats = {
        'total_patients': len(df),
        'age_mean': df['age'].mean(),
        'age_std': df['age'].std(),
        'age_min': df['age'].min(),
        'age_max': df['age'].max(),
        'gender_distribution': df['gender'].value_counts().to_dict(),
        'diagnosis_distribution': get_class_distribution(df)
    }
    
    return stats


def visualize_sample_images(df, image_dir, samples_per_class=2, target_size=(320, 320), save_path=None):
    """
    Visualize sample images from each diagnosis class
    
    Args:
        df: DataFrame with patient data
        image_dir: Directory containing images
        samples_per_class: Number of samples to show per class
        target_size: Size to resize images
        save_path: Path to save figure (optional)
    """
    n_classes = df['diagnosis'].nunique()
    
    fig, axes = plt.subplots(n_classes, samples_per_class, 
                            figsize=(4*samples_per_class, 4*n_classes))
    
    if samples_per_class == 1:
        axes = axes.reshape(-1, 1)
    
    for class_idx in range(n_classes):
        # Get samples from this class
        class_samples = df[df['diagnosis'] == class_idx].sample(n=min(samples_per_class, len(df[df['diagnosis'] == class_idx])))
        
        for sample_idx, (_, row) in enumerate(class_samples.iterrows()):
            if sample_idx >= samples_per_class:
                break
                
            try:
                img = load_image(row['id_code'], image_dir, target_size, add_png=True)
                
                ax = axes[class_idx, sample_idx]
                ax.imshow(img)
                ax.axis('off')
                
                if sample_idx == 0:
                    ax.set_title(f"Class {class_idx}: {DIAGNOSIS_LABELS[class_idx]}\n" + 
                               f"Age: {row['age']}, Gender: {row['gender']}", 
                               fontsize=10)
                else:
                    ax.set_title(f"Age: {row['age']}, Gender: {row['gender']}", fontsize=10)
                    
            except Exception as e:
                print(f"Error loading image {row['id_code']}: {e}")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved sample images to {save_path}")
    
    plt.show()


def get_patient_info(patient_id, df):
    """
    Get information for a specific patient
    
    Args:
        patient_id: Patient ID (without .png)
        df: DataFrame with patient data
        
    Returns:
        patient_info: Dictionary with patient information
    """
    # Remove .png if present
    patient_id = patient_id.replace('.png', '')
    
    patient_row = df[df['id_code'] == patient_id]
    
    if len(patient_row) == 0:
        return None
    
    patient_row = patient_row.iloc[0]
    
    patient_info = {
        'id': patient_row['id_code'],
        'age': int(patient_row['age']),
        'gender': patient_row['gender'],
        'diagnosis': int(patient_row['diagnosis']),
        'diagnosis_label': DIAGNOSIS_LABELS[int(patient_row['diagnosis'])],
        'diagnosis_description': DIAGNOSIS_DESCRIPTIONS[int(patient_row['diagnosis'])]
    }
    
    return patient_info
