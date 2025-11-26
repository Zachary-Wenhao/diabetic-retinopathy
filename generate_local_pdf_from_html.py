#!/usr/bin/env python3
"""
Generate explanation_local.pdf from existing HTML patient reports.
This script converts HTML patient reports to PDF format for the assignment deliverable.
"""

import os
import sys
from pathlib import Path
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def create_combined_html(patient_reports_dir, output_html_path):
    """
    Combine multiple patient HTML reports into a single HTML document.
    
    Args:
        patient_reports_dir (str): Directory containing patient HTML reports
        output_html_path (str): Path where combined HTML will be saved
    """
    
    # Find patient HTML reports
    patient_htmls = []
    for file in sorted(os.listdir(patient_reports_dir)):
        if file.endswith('_report.html'):
            patient_htmls.append(os.path.join(patient_reports_dir, file))
    
    if len(patient_htmls) < 2:
        print(f"Error: Need at least 2 patient HTML reports. Found {len(patient_htmls)}")
        sys.exit(1)
    
    # Take first two patients for the assignment
    patient1_html = patient_htmls[0]
    patient2_html = patient_htmls[1]
    
    print(f"Combining reports from:")
    print(f"  - {patient1_html}")
    print(f"  - {patient2_html}")
    
    # Read HTML content and fix image paths
    with open(patient1_html, 'r', encoding='utf-8') as f:
        patient1_content = f.read()
    
    with open(patient2_html, 'r', encoding='utf-8') as f:
        patient2_content = f.read()
    
    # Fix image paths to be absolute
    patient_reports_abs = os.path.abspath(patient_reports_dir)
    patient1_content = patient1_content.replace('src="patient1_', f'src="{patient_reports_abs}/patient1_')
    patient1_content = patient1_content.replace('src="patient2_', f'src="{patient_reports_abs}/patient2_')
    patient2_content = patient2_content.replace('src="patient1_', f'src="{patient_reports_abs}/patient1_')
    patient2_content = patient2_content.replace('src="patient2_', f'src="{patient_reports_abs}/patient2_')
    
    # Extract body content from each HTML (remove html, head tags)
    def extract_body_content(html_content):
        """Extract content between <body> tags"""
        start_tag = '<body'
        end_tag = '</body>'
        
        start_idx = html_content.find(start_tag)
        if start_idx == -1:
            return html_content
        
        # Find end of opening body tag
        start_idx = html_content.find('>', start_idx) + 1
        end_idx = html_content.rfind(end_tag)
        
        if end_idx == -1:
            return html_content[start_idx:]
        
        return html_content[start_idx:end_idx]
    
    patient1_body = extract_body_content(patient1_content)
    patient2_body = extract_body_content(patient2_content)
    
    # Create combined HTML document
    combined_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diabetic Retinopathy Patient Explanations</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.8;
            color: #333;
            background: white;
            font-size: 13px;
            margin: 0;
            padding: 20px;
        }}
        
        .page-header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
            border-bottom: 2px solid #e1e5e9;
        }}
        
        .page-header h1 {{
            font-size: 24px;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 8px;
        }}
        
        .page-header .subtitle {{
            font-size: 16px;
            color: #718096;
            font-weight: 500;
        }}
        
        .patient-report {{
            margin-bottom: 40px;
            page-break-inside: avoid;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        /* Enhanced styles for patient content */
        .patient-info {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #4299e1;
            line-height: 1.6;
        }}
        
        .result-box {{
            padding: 25px;
            border-radius: 8px;
            margin: 25px 0;
            text-align: center;
            font-weight: 600;
            line-height: 1.8;
        }}
        
        .result-positive {{
            background: #f0fff4;
            border: 2px solid #68d391;
            color: #22543d;
        }}
        
        .result-negative {{
            background: #fff5f5;
            border: 2px solid #fc8181;
            color: #742a2a;
        }}
        
        .explanation-images {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            gap: 20px;
        }}
        
        .image-container {{
            flex: 1;
            text-align: center;
        }}
        
        .image-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        
        .image-caption {{
            margin-top: 8px;
            font-size: 12px;
            color: #718096;
            font-style: italic;
        }}
        
        .explanation-text {{
            background: #fffaf0;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ed8936;
            line-height: 1.8;
        }}
        
        .next-steps {{
            background: #fff5f5;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #e53e3e;
            line-height: 1.8;
        }}
        
        .disclaimer {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 12px;
            color: #4a5568;
            font-style: italic;
            margin-top: 30px;
            line-height: 1.6;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 25px;
            line-height: 1.8;
        }}
        
        li {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        
        h1, h2, h3 {{
            margin: 25px 0 15px 0;
            color: #2d3748;
            line-height: 1.4;
        }}
        
        p {{
            margin: 12px 0;
            line-height: 1.7;
        }}
        
        /* Instructions section */
        .instructions {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #e1e5e9;
        }}
        
        .instructions h2 {{
            color: #1a365d;
            font-size: 18px;
            margin-bottom: 15px;
        }}
        
        .code-block {{
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #2d3748;
            margin: 10px 0;
            overflow-x: auto;
        }}
        
        .step-list {{
            counter-reset: step-counter;
            list-style: none;
            padding-left: 0;
        }}
        
        .step-list li {{
            counter-increment: step-counter;
            margin: 15px 0;
            padding-left: 30px;
            position: relative;
        }}
        
        .step-list li::before {{
            content: counter(step-counter);
            position: absolute;
            left: 0;
            top: 0;
            background: #4299e1;
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}
        
        /* Print-specific styles */
        @media print {{
            .page-break {{
                page-break-before: always;
            }}
            
            .patient-report {{
                page-break-inside: avoid;
            }}
            
            body {{
                font-size: 12px;
                line-height: 1.6;
            }}
            
            .page-header h1 {{
                font-size: 18px;
                margin-bottom: 15px;
            }}
            
            .patient-info, .result-box, .explanation-text, .next-steps {{
                margin: 15px 0;
                padding: 15px;
            }}
            
            ul, ol {{
                margin: 12px 0;
            }}
            
            li {{
                margin: 6px 0;
            }}
        }}
        
        /* Ensure images fit properly */
        img {{
            max-width: 100% !important;
            height: auto !important;
        }}
        
        # WeasyPrint specific adjustments
        .explanation-images {{
            display: block;
            margin: 20px 0;
        }}
        
        .image-container {{
            display: inline-block;
            width: 48%;
            vertical-align: top;
            margin: 1%;
        }}
        
        .image-caption {{
            margin-top: 10px;
            font-size: 11px;
            color: #718096;
            font-style: italic;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="page-header">
        <h1>Diabetic Retinopathy Patient Explanations</h1>
        <div class="subtitle">AI-Generated Screening Reports for Individual Patients</div>
        <div class="subtitle">Generated on {Path().cwd().name} - Assignment 4 Deliverable</div>
    </div>
    
    <div class="patient-report">
        <h2 style="color: #1a365d; border-bottom: 2px solid #e1e5e9; padding-bottom: 10px;">Patient 1 Report</h2>
        {patient1_body}
    </div>
    
    <div class="patient-report page-break">
        <h2 style="color: #1a365d; border-bottom: 2px solid #e1e5e9; padding-bottom: 10px;">Patient 2 Report</h2>
        {patient2_body}
    </div>
    
    <div class="instructions page-break">
        <h2>How to Generate Reports for Additional Patients</h2>
        
        <p>This document shows two example patient reports generated by our AI explainability system. To create reports for new patients, follow these steps:</p>
        
        <h3>Method 1: Using the Command Line Tool (Recommended)</h3>
        <p>The easiest way to generate a new patient report:</p>
        <div class="code-block">python generate_patient_cli.py --patient_id NEW_ID --image_path path/to/retinal_image.jpg</div>
        
        <h3>Method 2: Using the Jupyter Notebook</h3>
        <ol class="step-list">
            <li>Open the patient explanation notebook: <code>notebooks/04_local_explanations.ipynb</code></li>
            <li>Navigate to the "Generate Complete Explanation for Each Patient" section (cell 8)</li>
            <li>Update the patient selection in the earlier cells or modify the generation function</li>
            <li>Run the <code>generate_patient_explanation()</code> function with new patient data</li>
            <li>Check the <code>outputs/patient_reports/</code> folder for generated files</li>
        </ol>
        
        <h3>Method 3: Converting HTML Reports to PDF</h3>
        <p>To convert the HTML reports to a combined PDF (like this document):</p>
        <div class="code-block">python generate_local_pdf_from_html.py</div>
        <p>This script automatically finds patient HTML reports and combines them into <code>explanation_local.pdf</code></p>
        
        <h3>Required Files</h3>
        <ul>
            <li><strong>model.h5</strong> - The trained ResNet50 model</li>
            <li><strong>src/</strong> folder - All utility modules for data processing and explanation generation</li>
            <li><strong>Patient retinal images</strong> - JPG or PNG format, minimum 224×224 pixels</li>
            <li><strong>requirements.txt</strong> - Python dependencies</li>
        </ul>
        
        <h3>Generated Output Files</h3>
        <p>For each patient, the system generates:</p>
        <ul>
            <li><code>patient_X_report.html</code> - Interactive HTML report</li>
            <li><code>patient_X_explanation_viz.png</code> - Visual explanation overlay</li>
            <li><code>patient_X_simple_overlay.png</code> - Simplified heatmap</li>
            <li><code>patient_X_confidence.png</code> - Confidence distribution</li>
            <li><code>patient_X_multiclass_gradcam.png</code> - Multi-class analysis</li>
        </ul>
        
        <h3>Troubleshooting</h3>
        <ul>
            <li><strong>Image loading issues:</strong> Ensure images are in supported formats and accessible paths</li>
            <li><strong>Missing dependencies:</strong> Run <code>pip install -r requirements.txt</code></li>
            <li><strong>Model not found:</strong> Verify <code>model.h5</code> is in the project root directory</li>
            <li><strong>Permission errors:</strong> Check write permissions for <code>outputs/</code> folder</li>
        </ul>
        
        <div class="disclaimer">
            <strong>Important:</strong> These AI-generated reports are for screening purposes only. All results should be validated by qualified medical professionals before making clinical decisions.
        </div>
    </div>
</body>
</html>
"""
    
    # Write combined HTML
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(combined_html)
    
    print(f"Combined HTML created: {output_html_path}")
    return output_html_path

def html_to_pdf(html_path, pdf_path):
    """
    Convert HTML to PDF using WeasyPrint.
    
    Args:
        html_path (str): Path to HTML file
        pdf_path (str): Path where PDF will be saved
    """
    try:
        # Font configuration for better text rendering
        font_config = FontConfiguration()
        
        # Custom CSS for PDF optimization
        pdf_css = CSS(string='''
            @page {
                size: Letter;
                margin: 1in;
                @top-center {
                    content: "Diabetic Retinopathy Patient Explanations";
                    font-family: Inter, sans-serif;
                    font-size: 10px;
                    color: #666;
                    margin-bottom: 20px;
                }
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: Inter, sans-serif;
                    font-size: 10px;
                    color: #666;
                    margin-top: 20px;
                }
            }
            
            body {
                font-size: 12px;
                line-height: 1.7;
                margin: 0;
                padding: 0;
            }
            
            .page-header {
                margin-bottom: 30px;
                padding-bottom: 20px;
            }
            
            .page-header h1 {
                font-size: 18px;
                line-height: 1.3;
                margin-bottom: 10px;
            }
            
            .patient-report {
                margin-bottom: 40px;
                page-break-inside: avoid;
            }
            
            .patient-info, .result-box, .explanation-text, .next-steps {
                margin: 20px 0;
                padding: 18px;
                page-break-inside: avoid;
            }
            
            .explanation-images {
                display: block;
                margin: 25px 0;
                page-break-inside: avoid;
            }
            
            .image-container {
                display: inline-block;
                width: 48%;
                vertical-align: top;
                margin: 1%;
            }
            
            .image-container img {
                max-width: 100% !important;
                height: auto !important;
                display: block;
            }
            
            .image-caption {
                margin-top: 8px;
                font-size: 10px;
                line-height: 1.3;
                text-align: center;
            }
            
            ul, ol {
                margin: 15px 0;
                padding-left: 25px;
            }
            
            li {
                margin: 6px 0;
                line-height: 1.6;
            }
            
            h1, h2, h3 {
                margin-top: 25px;
                margin-bottom: 15px;
                line-height: 1.3;
                page-break-after: avoid;
            }
            
            p {
                margin: 10px 0;
                line-height: 1.7;
            }
            
            .disclaimer {
                margin-top: 30px;
                padding: 15px;
                line-height: 1.5;
            }
            
            .instructions {
                margin-top: 30px;
                page-break-before: always;
            }
            
            .code-block {
                margin: 15px 0;
                padding: 12px;
                font-size: 10px;
                line-height: 1.4;
                page-break-inside: avoid;
            }
            
            .step-list li {
                margin: 12px 0;
                line-height: 1.6;
            }
        ''', font_config=font_config)
        
        print("Converting HTML to PDF...")
        
        # Convert to PDF
        html_doc = HTML(filename=html_path)
        html_doc.write_pdf(pdf_path, stylesheets=[pdf_css], font_config=font_config)
        
        print(f"PDF successfully created: {pdf_path}")
        return True
        
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        print("Make sure WeasyPrint is installed: pip install weasyprint")
        return False

def main():
    """Main function to generate explanation_local.pdf from HTML reports."""
    
    # Setup paths
    project_root = Path(__file__).parent
    patient_reports_dir = project_root / "outputs" / "patient_reports"
    output_html = project_root / "temp_combined_report.html"
    output_pdf = project_root / "explanation_local.pdf"
    
    # Check if patient reports directory exists
    if not patient_reports_dir.exists():
        print(f"Error: Patient reports directory not found: {patient_reports_dir}")
        print("Please run the patient report generation first.")
        print("Use: jupyter notebook template_code_for_explanation_and_html.ipynb")
        sys.exit(1)
    
    print("=== Generating explanation_local.pdf from HTML Reports ===")
    print(f"Source directory: {patient_reports_dir}")
    print(f"Output PDF: {output_pdf}")
    
    try:
        # Step 1: Create combined HTML
        combined_html_path = create_combined_html(
            str(patient_reports_dir), 
            str(output_html)
        )
        
        # Step 2: Convert HTML to PDF
        success = html_to_pdf(str(output_html), str(output_pdf))
        
        if success:
            # Clean up temporary HTML file
            if output_html.exists():
                output_html.unlink()
                print("Temporary HTML file cleaned up.")
            
            print("\n✅ SUCCESS!")
            print(f"📄 explanation_local.pdf has been generated successfully!")
            print(f"📍 Location: {output_pdf.absolute()}")
            print(f"📊 File size: {output_pdf.stat().st_size / 1024:.1f} KB")
            
            print("\n📋 Contents:")
            print("   • Patient 1 explanation with visual analysis")
            print("   • Patient 2 explanation with visual analysis") 
            print("   • Instructions for generating additional reports")
            print("   • Troubleshooting guide")
            
        else:
            print("\n❌ Failed to generate PDF")
            print("Please check the error messages above and try again.")
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        
        # Clean up on error
        if output_html.exists():
            output_html.unlink()
            
        sys.exit(1)

if __name__ == "__main__":
    main()