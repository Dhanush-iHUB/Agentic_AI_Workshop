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

    try:
        # Use file content if provided, otherwise use text input
        final_html = process_html_file(html_file) if html_file else html_input
        
        if not final_html:
            return "No HTML content provided", "Error: Please provide HTML content", None
            
        # Validate HTML
        is_valid, message = validate_html(final_html)
        if not is_valid:
            return message, "Error: Invalid HTML", None
            
        # Optimize the content
        optimized_html, report = optimizer.optimize_content(final_html, target_persona)
        
        # Format the report for display
        report_str = json.dumps(report, indent=2)
        
        # Create a success notification
        notification = "✅ Content optimized successfully!"
        
        return optimized_html, report_str, notification
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[App] Exception: {tb}")
        return "", f"Error occurred during optimization:\n{str(e)}\n\nTraceback:\n{tb}", "❌ An error occurred"

# Custom CSS for better styling
custom_css = """
.container {
    max-width: 1200px;
    margin: auto;
    padding: 20px;
}
.main-title {
    text-align: center;
    margin-bottom: 2em;
}
.persona-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f7f7f7;
    margin: 10px 0;
}
.output-container {
    border-left: 3px solid #2196F3;
    padding-left: 20px;
}
"""

# Create the Gradio interface
with gr.Blocks(title="Persona-Driven Content Optimizer", css=custom_css) as iface:
    gr.Markdown("""
    <div class="main-title">
        # 🎯 Persona-Driven Content Optimizer
        
        Transform your content to resonate with your target audience using AI-powered optimization
    </div>
    """)
    
    with gr.Tabs():
        with gr.TabItem("✨ Optimize Content"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### 📝 Input Options
                    Choose one of the following methods to provide your content:
                    """)
                    
                    input_html = gr.TextArea(
                        label="Option 1: Paste HTML Content",
                        placeholder="Enter your HTML content here...",
                        lines=10
                    )
                    
                    file_input = gr.File(
                        label="Option 2: Upload HTML File",
                        file_types=[".html", ".htm"],
                        type="binary"
                    )
                    
                    with gr.Box(elem_classes="persona-box"):
                        gr.Markdown("### 👥 Target Audience")
                        persona_choice = gr.Radio(
                            choices=["Auto-detect", "Generation Z", "Professional"],
                            label="Select your target persona",
                            value="Auto-detect",
                            interactive=True
                        )
                    
                    submit_btn = gr.Button("🚀 Optimize Content", variant="primary", size="lg")
                
                with gr.Column(scale=1, elem_classes="output-container"):
                    notification = gr.Textbox(label="Status", interactive=False)
                    output_html = gr.TextArea(
                        label="✨ Optimized HTML",
                        lines=10,
                        show_copy_button=True
                    )
                    with gr.Accordion("📊 Detailed Report", open=False):
                        optimization_report = gr.JSON(
                            label="Optimization Analysis"
                        )
        
        with gr.TabItem("ℹ️ Help & Information"):
            gr.Markdown("""
            ### 🎯 How It Works
            
            1. **Input Your Content**
               - Paste your HTML directly into the text area, or
               - Upload an HTML file using the file uploader
            
            2. **Choose Your Audience**
               - Let AI detect your target audience automatically, or
               - Manually select your preferred persona
            
            3. **Get Optimized Content**
               - Click "Optimize Content" to transform your content
               - Review the optimized HTML and detailed analysis
               - Copy the results with one click
            
            ### 👥 Available Personas
            
            <div class="persona-box">
            
            **Generation Z**
            - Casual and engaging tone
            - Modern language patterns
            - Emoji-rich content
            - Short, impactful messages
            
            **Professional**
            - Formal business tone
            - Industry-standard terminology
            - Clear and concise language
            - Professional formatting
            
            </div>
            """)
    
    submit_btn.click(
        fn=lambda html, file, persona: optimize_content(
            html,
            file,
            None if persona == "Auto-detect" else persona.lower().replace(" ", "")
        ),
        inputs=[input_html, file_input, persona_choice],
        outputs=[output_html, optimization_report, notification]
    )

if __name__ == "__main__":
    # Check if GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable is not set!")
        print("Please set it in your .env file or environment variables.")
    
    # Launch the interface
    iface.launch(share=True) 