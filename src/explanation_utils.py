"""
Explanation utilities using SHAP, Grad-CAM, and other explainability techniques
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import cv2
from matplotlib.colors import LinearSegmentedColormap


def get_gradcam_heatmap(model, image, pred_class=None, last_conv_layer_name=None):
    """
    Generate Grad-CAM heatmap for an image
    
    Args:
        model: Trained Keras model
        image: Preprocessed image (with batch dimension)
        pred_class: Target class for Grad-CAM (if None, uses predicted class)
        last_conv_layer_name: Name of last convolutional layer
        
    Returns:
        heatmap: Grad-CAM heatmap as numpy array
    """
    # Find last convolutional layer if not specified
    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if len(layer.output_shape) == 4:  # Convolutional layer
                last_conv_layer_name = layer.name
                break
    
    # Create model that maps input to last conv layer + predictions
    grad_model = keras.Model(
        inputs=model.input,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )
    
    # Compute gradient
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image)
        if pred_class is None:
            pred_class = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_class]
    
    # Gradient of class output with respect to feature map
    grads = tape.gradient(class_channel, conv_outputs)
    
    # Mean intensity of gradient over specific feature map channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    # Multiply each channel by "importance"
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    
    # Normalize heatmap
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    
    return heatmap.numpy()


def overlay_heatmap(image, heatmap, alpha=0.4, colormap=cv2.COLORMAP_JET):
    """
    Overlay Grad-CAM heatmap on original image
    
    Args:
        image: Original image (normalized 0-1)
        heatmap: Grad-CAM heatmap
        alpha: Transparency of overlay
        colormap: OpenCV colormap to use
        
    Returns:
        overlaid_image: Image with heatmap overlay
    """
    # Resize heatmap to match image size
    heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
    
    # Convert heatmap to RGB
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, colormap)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    heatmap = heatmap / 255.0
    
    # Convert image to 0-1 range if needed
    if image.max() > 1.0:
        image = image / 255.0
    
    # Overlay
    overlaid_image = heatmap * alpha + image * (1 - alpha)
    
    return overlaid_image


def create_gradcam_visualization(model, image, save_path=None, pred_class=None):
    """
    Create complete Grad-CAM visualization with original and overlay
    
    Args:
        model: Trained model
        image: Input image (with or without batch dimension)
        save_path: Path to save visualization
        pred_class: Target class (if None, uses predicted)
        
    Returns:
        fig: Matplotlib figure
    """
    # Ensure batch dimension
    if len(image.shape) == 3:
        image_batch = np.expand_dims(image, axis=0)
    else:
        image_batch = image
        image = image[0]
    
    # Generate heatmap
    heatmap = get_gradcam_heatmap(model, image_batch, pred_class)
    
    # Create overlay
    overlay = overlay_heatmap(image, heatmap)
    
    # Create visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original image
    axes[0].imshow(image)
    axes[0].set_title('Original Image', fontsize=14)
    axes[0].axis('off')
    
    # Heatmap
    axes[1].imshow(heatmap, cmap='jet')
    axes[1].set_title('Grad-CAM Heatmap', fontsize=14)
    axes[1].axis('off')
    
    # Overlay
    axes[2].imshow(overlay)
    axes[2].set_title('Overlay', fontsize=14)
    axes[2].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved Grad-CAM visualization to {save_path}")
    
    return fig


def create_simple_heatmap_overlay(model, image, title="What the Computer Saw", save_path=None):
    """
    Create simple heatmap overlay for patient reports (8th grade level)
    
    Args:
        model: Trained model
        image: Input image
        title: Title for the plot
        save_path: Path to save
        
    Returns:
        fig: Matplotlib figure
    """
    # Ensure batch dimension
    if len(image.shape) == 3:
        image_batch = np.expand_dims(image, axis=0)
    else:
        image_batch = image
        image = image[0]
    
    # Generate heatmap
    heatmap = get_gradcam_heatmap(model, image_batch)
    overlay = overlay_heatmap(image, heatmap, alpha=0.5)
    
    # Create simple visualization
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.imshow(overlay)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    
    # Add explanation text
    explanation_text = ("Red/yellow areas = where the computer looked most closely\n"
                       "Blue/green areas = normal areas")
    fig.text(0.5, 0.02, explanation_text, ha='center', fontsize=12, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved simple heatmap to {save_path}")
    
    return fig


def generate_confidence_chart(probabilities, class_names, save_path=None):
    """
    Generate a simple bar chart showing prediction confidence for all classes
    
    Args:
        probabilities: Dictionary or array of probabilities for each class
        class_names: List of class names
        save_path: Path to save chart
        
    Returns:
        fig: Matplotlib figure
    """
    if isinstance(probabilities, dict):
        probs = [probabilities[name] for name in class_names]
    else:
        probs = probabilities
    
    # Convert to percentages
    probs_pct = [p * 100 for p in probs]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['green' if p == max(probs_pct) else 'lightblue' for p in probs_pct]
    bars = ax.barh(class_names, probs_pct, color=colors)
    
    # Add percentage labels
    for i, (bar, pct) in enumerate(zip(bars, probs_pct)):
        ax.text(pct + 2, i, f'{pct:.1f}%', va='center', fontweight='bold')
    
    ax.set_xlabel('Confidence (%)', fontsize=12)
    ax.set_title('How Sure is the Computer?', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 110)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved confidence chart to {save_path}")
    
    return fig


def prepare_shap_background(images, max_samples=50):
    """
    Prepare background dataset for SHAP analysis
    
    Args:
        images: Array of images
        max_samples: Maximum number of samples for background
        
    Returns:
        background: Background dataset for SHAP
    """
    if len(images) > max_samples:
        indices = np.random.choice(len(images), max_samples, replace=False)
        background = images[indices]
    else:
        background = images
    
    return background


def explain_prediction_simple(predicted_class, confidence, heatmap_focus):
    """
    Generate simple text explanation based on prediction and heatmap
    
    Args:
        predicted_class: Predicted class (0-4)
        confidence: Confidence score
        heatmap_focus: Description of where heatmap focused (string)
        
    Returns:
        explanation: Simple text explanation
    """
    class_explanations = {
        0: "The computer looked at your eye photo and did not find any signs of disease. Your blood vessels look clear and healthy.",
        1: "The computer found some early changes in your eye. These are small signs that need to be watched.",
        2: "The computer found changes in your eye that need attention. There are signs of blood vessel damage.",
        3: "The computer found serious changes in your eye. The blood vessels show significant damage that needs treatment.",
        4: "The computer found advanced changes in your eye. There is serious blood vessel damage that needs immediate treatment."
    }
    
    explanation = class_explanations.get(predicted_class, class_explanations[0])
    
    # Add confidence note
    confidence_pct = int(confidence * 100)
    explanation += f"\n\nThe computer is {confidence_pct}% confident about this finding."
    
    return explanation
