import gradio as gr
import json
from content_optimizer import ContentOptimizer
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import traceback

# Load environment variables
load_dotenv()

# Initialize the optimizer
optimizer = ContentOptimizer()

def validate_html(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html5lib')
        return True, "HTML is valid"
    except Exception as e:
        return False, f"Invalid HTML: {str(e)}"

def process_html_file(file_obj):
    if file_obj is None:
        return None
    content = file_obj.decode('utf-8')
    is_valid, message = validate_html(content)
    if not is_valid:
        raise ValueError(message)
    return content

def optimize_content(html_input, html_file, target_persona=None):
    persona_map = {
        "generationz": "genz",
        "professional": "professional"
    }
    if target_persona:
        target_persona = persona_map.get(target_persona, target_persona)
    """
    Process the input HTML and return optimized content
    """
    try:
        # Use file content if provided, otherwise use text input
        final_html = process_html_file(html_file) if html_file else html_input
        
        if not final_html:
            return "No HTML content provided", "Error: Please provide HTML content"
            
        # Validate HTML
        is_valid, message = validate_html(final_html)
        if not is_valid:
            return message, "Error: Invalid HTML"
            
        # Optimize the content
        optimized_html, report = optimizer.optimize_content(final_html, target_persona)
        
        # Format the report for display
        report_str = json.dumps(report, indent=2)
        
        print(f"[App] Final Optimized HTML: {optimized_html[:200]}...")
        print(f"[App] Optimization Report: {report_str}")
        return optimized_html, report_str
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[App] Exception: {tb}")
        return "", f"Error occurred during optimization:\n{str(e)}\n\nTraceback:\n{tb}"

# Create the Gradio interface
with gr.Blocks(title="Persona-Driven Content Optimizer") as iface:
    gr.Markdown("""
    # 🎯 Persona-Driven Content Optimizer
    
    Upload your HTML content and get it optimized for your target audience!
    The system will automatically detect the current audience and optimize accordingly,
    or you can specify your target persona.
    """)
    
    with gr.Row():
        with gr.Column():
            input_html = gr.TextArea(
                label="Input HTML",
                placeholder="Paste your HTML content here...",
                lines=10
            )
            file_input = gr.File(
                label="Or Upload HTML File",
                file_types=[".html", ".htm"],
                type="binary"
            )
            persona_choice = gr.Radio(
                choices=["Auto-detect", "Generation Z", "Professional"],
                label="Target Persona",
                value="Auto-detect"
            )
            submit_btn = gr.Button("Optimize Content", variant="primary")
        
        with gr.Column():
            output_html = gr.TextArea(
                label="Optimized HTML",
                lines=10
            )
            optimization_report = gr.TextArea(
                label="Optimization Report",
                lines=10
            )
    
    submit_btn.click(
        fn=lambda html, file, persona: optimize_content(
            html,
            file,
            None if persona == "Auto-detect" else persona.lower().replace(" ", "")
        ),
        inputs=[input_html, file_input, persona_choice],
        outputs=[output_html, optimization_report]
    )
    
    gr.Markdown("""
    ### 📝 Instructions
    1. Either paste your HTML content in the input box OR upload an HTML file
    2. Choose your target audience (or let the system detect it)
    3. Click "Optimize Content" to get your persona-optimized content
    4. Review the optimized HTML and detailed report
    
    ### 🎯 Supported Personas
    - **Generation Z**: Casual, trendy, emoji-rich content
    - **Professional**: Formal, business-focused content
    """)

if __name__ == "__main__":
    # Check if GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable is not set!")
        print("Please set it in your .env file or environment variables.")
    
    # Launch the interface
    iface.launch(share=True) 