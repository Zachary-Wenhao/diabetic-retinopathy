"""
HTML and PDF generation utilities for creating patient reports and handbooks
"""

import os
from datetime import datetime
import matplotlib.pyplot as plt
import re


def format_explanation_text_to_html(explanation_text):
    """
    Convert plain text explanation to properly formatted HTML
    
    Args:
        explanation_text (str): Plain text explanation with sections and formatting
        
    Returns:
        str: HTML formatted explanation
    """
    html = ""
    lines = explanation_text.split('\n')
    current_section = None
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
            
        # Main title
        if line == "EYE SCREENING REPORT":
            continue  # Skip this as we already have a header
            
        # Section headers (lines with all caps followed by dashes)
        if line.isupper() and len(line) > 3 and not line.startswith('•'):
            if in_list:
                html += "</ul>\n"
                in_list = False
                
            if line.startswith('=') or line.startswith('-'):
                continue  # Skip separator lines
                
            html += f'<div class="explanation-section"><h3 class="section-header">{line}</h3>\n'
            current_section = line
            
        # Bullet points
        elif line.startswith('•') or line.startswith('✓') or line.startswith('⚠'):
            if not in_list:
                html += '<ul class="explanation-list">\n'
                in_list = True
            icon = line[0]
            content = line[1:].strip()
            html += f'<li><span class="list-icon">{icon}</span> {content}</li>\n'
            
        # Regular paragraphs
        elif line and not line.startswith('=') and not line.startswith('-'):
            if in_list:
                html += "</ul>\n"
                in_list = False
                
            # Check for special formatting
            if '✓' in line or 'Good News' in line:
                html += f'<p class="positive-result">{line}</p>\n'
            elif '⚠' in line or 'Warning' in line or 'Detected' in line:
                html += f'<p class="warning-result">{line}</p>\n'
            elif 'confident' in line.lower():
                html += f'<p class="confidence-text">{line}</p>\n'
            else:
                html += f'<p class="explanation-paragraph">{line}</p>\n'
    
    if in_list:
        html += "</ul>\n"
        
    if current_section:
        html += "</div>\n"
        
    return html
import re


def format_explanation_text_to_html(explanation_text):
    """
    Convert plain text explanation to properly formatted HTML
    
    Args:
        explanation_text (str): Plain text explanation with sections and formatting
        
    Returns:
        str: HTML formatted explanation
    """
    html = ""
    lines = explanation_text.split('\n')
    current_section = None
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
            
        # Main title
        if line == "EYE SCREENING REPORT":
            continue  # Skip this as we already have a header
            
        # Section headers (lines with all caps followed by dashes)
        if line.isupper() and len(line) > 3 and not line.startswith('•'):
            if in_list:
                html += "</ul>\n"
                in_list = False
                
            if line.startswith('=') or line.startswith('-'):
                continue  # Skip separator lines
                
            html += f'<div class="explanation-section"><h3 class="section-header">{line}</h3>\n'
            current_section = line
            
        # Bullet points
        elif line.startswith('•') or line.startswith('✓') or line.startswith('⚠'):
            if not in_list:
                html += '<ul class="explanation-list">\n'
                in_list = True
            icon = line[0]
            content = line[1:].strip()
            html += f'<li><span class="list-icon">{icon}</span> {content}</li>\n'
            
        # Regular paragraphs
        elif line and not line.startswith('=') and not line.startswith('-'):
            if in_list:
                html += "</ul>\n"
                in_list = False
                
            # Check for special formatting
            if '✓' in line or 'Good News' in line:
                html += f'<p class="positive-result">{line}</p>\n'
            elif '⚠' in line or 'Warning' in line or 'Detected' in line:
                html += f'<p class="warning-result">{line}</p>\n'
            elif 'confident' in line.lower():
                html += f'<p class="confidence-text">{line}</p>\n'
            else:
                html += f'<p class="explanation-paragraph">{line}</p>\n'
    
    if in_list:
        html += "</ul>\n"
        
    if current_section:
        html += "</div>\n"
        
    return html


def generate_patient_html(patient_info, prediction, image_path, heatmap_path, 
                          confidence_chart_path, template_path='templates/patient_report.html',
                          output_path=None):
    """
    Generate HTML report for a patient using template
    
    Args:
        patient_info: Dictionary with patient information
        prediction: Prediction dictionary from model_utils
        image_path: Path to original eye image
        heatmap_path: Path to Grad-CAM heatmap overlay
        confidence_chart_path: Path to confidence chart
        template_path: Path to HTML template
        output_path: Where to save generated HTML
        
    Returns:
        html_content: Generated HTML string
    """
    # Read template
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            html = f.read()
    else:
        # Use default template if file doesn't exist
        html = get_default_patient_template()
    
    # Replace placeholders
    replacements = {
        '{{PATIENT_ID}}': patient_info.get('id', 'Unknown'),
        '{{PATIENT_AGE}}': str(patient_info.get('age', 'N/A')),
        '{{PATIENT_GENDER}}': patient_info.get('gender', 'N/A'),
        '{{SCREENING_DATE}}': datetime.now().strftime('%B %d, %Y'),
        '{{DIAGNOSIS}}': prediction['predicted_label'],
        '{{CONFIDENCE}}': f"{int(prediction['confidence'] * 100)}%",
        '{{IMAGE_PATH}}': image_path,
        '{{HEATMAP_PATH}}': heatmap_path,
        '{{CONFIDENCE_CHART_PATH}}': confidence_chart_path,
        '{{EXPLANATION}}': get_patient_explanation(prediction, patient_info),
        '{{NEXT_STEPS}}': get_next_steps(prediction['predicted_class'], prediction['confidence'])
    }
    
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    # Save if output path provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html)
        print(f"Saved patient report to {output_path}")
    
    return html


def get_default_patient_template():
    """
    Return default HTML template for patient reports
    """
    template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Eye Screening Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px;
        }
        .result-box {
            background-color: #f0f0f0;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 5px solid #4CAF50;
        }
        .result-positive {
            border-left-color: #ff9800;
        }
        .section {
            margin: 30px 0;
        }
        .section-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 5px;
        }
        .image-container {
            text-align: center;
            margin: 20px 0;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .info-grid {
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 10px;
            margin: 15px 0;
        }
        .info-label {
            font-weight: bold;
        }
        .important-note {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        ul {
            line-height: 2;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Eye Disease Screening Report</h1>
        <p>Diabetic Retinopathy Screening</p>
    </div>
    
    <div class="section">
        <div class="info-grid">
            <div class="info-label">Patient ID:</div>
            <div>{{PATIENT_ID}}</div>
            <div class="info-label">Age:</div>
            <div>{{PATIENT_AGE}}</div>
            <div class="info-label">Gender:</div>
            <div>{{PATIENT_GENDER}}</div>
            <div class="info-label">Screening Date:</div>
            <div>{{SCREENING_DATE}}</div>
        </div>
    </div>
    
    <div class="result-box">
        <h2 style="margin-top: 0;">YOUR RESULT</h2>
        <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{{DIAGNOSIS}}</p>
        <p>Confidence: The computer is {{CONFIDENCE}} sure about this result.</p>
    </div>
    
    <div class="section">
        <div class="section-title">YOUR EYE PHOTO</div>
        <div class="image-container">
            <img src="{{IMAGE_PATH}}" alt="Eye Photo">
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">WHAT THE COMPUTER SAW</div>
        <div class="image-container">
            <img src="{{HEATMAP_PATH}}" alt="Analysis">
        </div>
        <p style="text-align: center; color: #666;">
            <strong>Colored areas show where the computer looked most closely:</strong><br>
            Red/Yellow = Areas checked carefully | Blue/Green = Normal areas
        </p>
    </div>
    
    <div class="section">
        <div class="section-title">HOW SURE IS THE RESULT?</div>
        <div class="image-container">
            <img src="{{CONFIDENCE_CHART_PATH}}" alt="Confidence">
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">WHAT THIS MEANS FOR YOU</div>
        {{EXPLANATION}}
    </div>
    
    <div class="section">
        <div class="section-title">WHAT TO DO NEXT</div>
        {{NEXT_STEPS}}
    </div>
    
    <div class="important-note">
        <strong>⚠️ IMPORTANT NOTES:</strong>
        <ul>
            <li>This is a screening tool, not a final diagnosis</li>
            <li>An eye doctor needs to confirm these results</li>
            <li>Keep taking care of your diabetes with your regular doctor</li>
            <li>Questions? Ask the nurse or volunteer who did your screening</li>
        </ul>
    </div>
</body>
</html>
    """
    return template


def get_patient_explanation(prediction, patient_info):
    """
    Generate patient-friendly explanation based on prediction
    """
    predicted_class = prediction['predicted_class']
    confidence = prediction['confidence']
    confidence_pct = int(confidence * 100)
    
    explanations = {
        0: f"""
        <p>✓ <strong>Good news!</strong> Your eyes look healthy right now.</p>
        <p>The screening tool looked at your eye photo. It checked the blood vessels and other 
        parts of your eye. Everything looks normal and healthy.</p>
        <p>The computer is {confidence_pct}% confident about this result.</p>
        """,
        1: f"""
        <p>⚠️ The screening found some <strong>early changes</strong> in your eye.</p>
        <p>This means there are small signs of diabetic eye disease. These are very early signs 
        and can be managed with good diabetes care.</p>
        <p>The computer is {confidence_pct}% confident about this result.</p>
        """,
        2: f"""
        <p>⚠️ The screening found <strong>changes in your eye</strong> that need attention.</p>
        <p>There are signs that diabetes is affecting the blood vessels in your eye. This does 
        NOT mean you will go blind. Treatment can prevent vision loss.</p>
        <p>The computer is {confidence_pct}% confident about this result.</p>
        """,
        3: f"""
        <p>⚠️ The screening found <strong>serious changes</strong> in your eye.</p>
        <p>There are significant signs that diabetes has damaged the blood vessels in your eye. 
        It's important to see an eye doctor soon. Treatment can protect your vision.</p>
        <p>The computer is {confidence_pct}% confident about this result.</p>
        """,
        4: f"""
        <p>⚠️ The screening found <strong>advanced changes</strong> in your eye.</p>
        <p>There are serious signs that diabetes has caused significant damage to your eye. 
        You need to see an eye doctor right away. Early treatment is very important to prevent vision loss.</p>
        <p>The computer is {confidence_pct}% confident about this result.</p>
        """
    }
    
    explanation = explanations.get(predicted_class, explanations[0])
    
    # Add low confidence warning if needed
    if confidence < 0.7:
        explanation += """
        <p><strong>Note:</strong> Because the computer is less sure about this result, 
        a nurse or doctor should review it carefully.</p>
        """
    
    return explanation


def get_next_steps(predicted_class, confidence):
    """
    Generate next steps recommendations based on prediction
    """
    next_steps = {
        0: """
        <ul>
            <li><strong>Keep managing your diabetes</strong> with your regular doctor</li>
            <li><strong>Come back for another screening in 1 year</strong></li>
            <li><strong>Tell your doctor if your vision changes</strong> (blurry vision, spots, etc.)</li>
            <li><strong>Control your blood sugar, blood pressure, and cholesterol</strong></li>
        </ul>
        """,
        1: """
        <ul>
            <li><strong>See an eye doctor within 6-12 months</strong> to check your eyes</li>
            <li><strong>Keep your blood sugar under control</strong> - this is very important</li>
            <li><strong>Monitor your vision</strong> - tell your doctor about any changes</li>
            <li><strong>Don't worry</strong> - early detection means you can prevent problems</li>
        </ul>
        """,
        2: """
        <ul>
            <li><strong>See an eye doctor within 3-6 months</strong> for a detailed eye exam</li>
            <li><strong>Work closely with your diabetes doctor</strong> to control blood sugar</li>
            <li><strong>The eye doctor may recommend treatment</strong> to prevent vision loss</li>
            <li><strong>Don't panic</strong> - treatment at this stage is very effective</li>
        </ul>
        """,
        3: """
        <ul>
            <li><strong>See an eye doctor within 1-2 months</strong> - this is important</li>
            <li><strong>Treatment will likely be needed</strong> to protect your vision</li>
            <li><strong>Keep your blood sugar as controlled as possible</strong></li>
            <li><strong>Follow your eye doctor's advice closely</strong></li>
        </ul>
        """,
        4: """
        <ul>
            <li><strong>See an eye doctor within 2 weeks</strong> - this is urgent</li>
            <li><strong>Treatment is needed soon</strong> to prevent serious vision loss</li>
            <li><strong>Don't delay</strong> - early treatment makes a big difference</li>
            <li><strong>Bring this report</strong> when you see the eye doctor</li>
        </ul>
        """
    }
    
    steps = next_steps.get(predicted_class, next_steps[0])
    
    return steps


def generate_patient_report_html(patient_info, prediction, explanation_text, 
                                  image_paths, output_path):
    """
    Generate HTML report for a patient with SHAP explanations
    
    Args:
        patient_info: Pandas Series or dict with patient information (id_code, age, gender, diagnosis)
        prediction: Prediction dictionary with predicted_class, confidence, probabilities
        explanation_text: Plain text explanation generated for the patient
        image_paths: Dictionary with keys 'original', 'confidence' for image filenames
        output_path: Path where HTML file should be saved
        
    Returns:
        output_path: Path to saved HTML file
    """
    from src.model_utils import CLASS_NAMES
    
    # Extract patient data
    patient_id = patient_info.get('id_code', patient_info.get('id', 'Unknown'))
    patient_age = patient_info.get('age', 'N/A')
    patient_gender = patient_info.get('gender', 'N/A')
    true_diagnosis = patient_info.get('diagnosis', None)
    
    # Extract prediction data
    predicted_class = prediction['predicted_class']
    confidence = prediction['confidence']
    probabilities = prediction['probabilities']
    
    # Build HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Eye Screening Report - Patient {patient_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.8;
            font-size: 14px;
        }}
        .header {{
            background-color: #2196F3;
            color: white;
            padding: 25px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .patient-info {{
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 12px;
            margin: 10px 0;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
        }}
        .result-box {{
            background-color: {"#e8f5e9" if predicted_class == 0 else "#fff3e0"};
            border-left: 5px solid {"#4caf50" if predicted_class == 0 else "#ff9800"};
            padding: 20px;
            margin: 25px 0;
            border-radius: 5px;
        }}
        .result-box h2 {{
            margin: 0 0 10px 0;
            color: {"#2e7d32" if predicted_class == 0 else "#e65100"};
        }}
        .diagnosis {{
            font-size: 24px;
            font-weight: bold;
            color: {"#2e7d32" if predicted_class == 0 else "#e65100"};
            margin: 10px 0;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 3px solid #2196F3;
        }}
        .image-container {{
            text-align: center;
            margin: 25px 0;
        }}
        .image-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        }}
        .image-caption {{
            color: #666;
            font-size: 13px;
            margin-top: 10px;
            font-style: italic;
        }}
        .explanation-box {{
            background-color: #fafafa;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin: 20px 0;
            font-family: Georgia, serif;
            line-height: 1.8;
        }}
        .explanation-section {{
            margin: 20px 0;
        }}
        .section-header {{
            color: #1976d2;
            font-size: 18px;
            font-weight: bold;
            margin: 15px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #e3f2fd;
        }}
        .explanation-paragraph {{
            margin: 12px 0;
            line-height: 1.7;
            color: #333;
        }}
        .explanation-list {{
            margin: 15px 0;
            padding-left: 0;
            list-style: none;
        }}
        .explanation-list li {{
            margin: 8px 0;
            padding: 8px 0;
            line-height: 1.6;
        }}
        .list-icon {{
            font-weight: bold;
            margin-right: 8px;
            font-size: 16px;
        }}
        .positive-result {{
            color: #2e7d32;
            font-weight: bold;
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .warning-result {{
            color: #d84315;
            font-weight: bold;
            background-color: #fff3e0;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .confidence-text {{
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            color: #1976d2;
        }}
        .important-note {{
            background-color: #fff8e1;
            border: 2px solid #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .important-note strong {{
            color: #f57c00;
        }}
        ul {{
            line-height: 2;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #777;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Diabetic Retinopathy Screening Report</h1>
        <p style="margin: 5px 0; font-size: 16px;">Computer-Assisted Eye Disease Detection</p>
        <p style="margin: 5px 0;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="patient-info">
        <h3 style="margin-top: 0; color: #333;">PATIENT INFORMATION</h3>
        <div class="info-grid">
            <div class="info-label">Patient ID:</div>
            <div>{patient_id}</div>
            <div class="info-label">Age:</div>
            <div>{patient_age} years</div>
            <div class="info-label">Gender:</div>
            <div>{patient_gender}</div>
            <div class="info-label">Screening Date:</div>
            <div>{datetime.now().strftime('%B %d, %Y')}</div>
"""
    
    if true_diagnosis is not None:
        html += f"""
            <div class="info-label">True Diagnosis:</div>
            <div>Class {true_diagnosis} ({CLASS_NAMES[true_diagnosis]})</div>
"""
    
    html += """
        </div>
    </div>
    
    <div class="result-box">
        <h2>SCREENING RESULT</h2>
"""
    
    html += f"""
        <div class="diagnosis">{CLASS_NAMES[predicted_class]}</div>
        <p style="font-size: 16px; margin: 10px 0;">
            <strong>Confidence Level:</strong> {int(confidence * 100)}%<br>
            <span style="color: #666;">The computer is {int(confidence * 100)}% confident about this result.</span>
        </p>
"""
    
    if true_diagnosis is not None and predicted_class == true_diagnosis:
        html += '<p style="color: green; font-weight: bold;">✓ Prediction matches actual diagnosis</p>'
    elif true_diagnosis is not None:
        html += '<p style="color: orange; font-weight: bold;">⚠ Prediction differs from actual diagnosis</p>'
    
    html += """
    </div>
    
    <div class="section">
        <div class="section-title">VISUAL EXPLANATION</div>
"""
    
    if 'original' in image_paths:
        html += f"""
        <div class="image-container">
            <img src="{image_paths['original']}" alt="Eye Analysis">
            <p class="image-caption">Areas highlighted show where the computer focused its attention during analysis</p>
        </div>
"""
    
    html += """
    </div>
    
    <div class="section">
        <div class="section-title">CONFIDENCE BREAKDOWN</div>
"""
    
    if 'confidence' in image_paths:
        html += f"""
        <div class="image-container">
            <img src="{image_paths['confidence']}" alt="Confidence Chart">
            <p class="image-caption">How confident the computer is for each disease level</p>
        </div>
"""
    
    html += """
    </div>
    
    <div class="section">
        <div class="section-title">DETAILED EXPLANATION</div>
        <div class="explanation-box">
"""
    
    # Format the explanation text as HTML
    formatted_explanation = format_explanation_text_to_html(explanation_text)
    html += formatted_explanation
    
    html += """
        </div>
    </div>
    
    <div class="important-note">
        <strong>⚠️ IMPORTANT REMINDERS</strong>
        <ul>
            <li><strong>This is a screening tool, not a final diagnosis.</strong> Only a trained eye doctor can give you a complete diagnosis.</li>
            <li><strong>See an eye doctor</strong> for a thorough examination, especially if the screening shows any signs of disease.</li>
            <li><strong>Keep managing your diabetes</strong> with your regular doctor. Good blood sugar control is the best way to protect your eyes.</li>
            <li><strong>Regular screenings are important.</strong> Even if results are good, come back for regular check-ups.</li>
            <li><strong>Questions?</strong> Ask the nurse or healthcare worker who performed your screening.</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>This report was generated by an AI-assisted diabetic retinopathy screening system.</p>
        <p>For medical advice and treatment, please consult a qualified ophthalmologist.</p>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def html_to_pdf(html_path, pdf_path):
    """
    Convert HTML file to PDF
    
    Args:
        html_path: Path to HTML file
        pdf_path: Path for output PDF
    """
    try:
        import pdfkit
        pdfkit.from_file(html_path, pdf_path)
        print(f"Successfully created PDF: {pdf_path}")
    except ImportError:
        print("pdfkit not installed. Trying weasyprint...")
        try:
            from weasyprint import HTML
            HTML(html_path).write_pdf(pdf_path)
            print(f"Successfully created PDF: {pdf_path}")
        except ImportError:
            print("Neither pdfkit nor weasyprint installed.")
            print("Install with: pip install pdfkit weasyprint")
            print(f"HTML file saved at: {html_path}")
            print("You can manually print to PDF from your browser.")


def concatenate_pdfs(pdf_paths, output_path):
    """
    Concatenate multiple PDFs into one
    
    Args:
        pdf_paths: List of PDF file paths to concatenate
        output_path: Path for combined PDF
    """
    try:
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        for pdf in pdf_paths:
            if os.path.exists(pdf):
                merger.append(pdf)
        
        merger.write(output_path)
        merger.close()
        print(f"Successfully created combined PDF: {output_path}")
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
