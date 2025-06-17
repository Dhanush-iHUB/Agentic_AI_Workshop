import gradio as gr
import json
from content_optimizer import ContentOptimizer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the optimizer
optimizer = ContentOptimizer()

def optimize_content(html_input, target_persona=None):
    """
    Process the input HTML and return optimized content
    """
    try:
        # Optimize the content
        optimized_html, report = optimizer.optimize_content(html_input, target_persona)
        
        # Format the report for display
        report_str = json.dumps(report, indent=2)
        
        return optimized_html, report_str
    
    except Exception as e:
        return str(e), "Error occurred during optimization"

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
        fn=lambda html, persona: optimize_content(
            html,
            None if persona == "Auto-detect" else persona.lower().replace(" ", "")
        ),
        inputs=[input_html, persona_choice],
        outputs=[output_html, optimization_report]
    )
    
    gr.Markdown("""
    ### 📝 Instructions
    1. Paste your HTML content in the input box
    2. Choose your target audience (or let the system detect it)
    3. Click "Optimize Content" to get your persona-optimized content
    4. Review the optimized HTML and detailed report
    
    ### 🎯 Supported Personas
    - **Generation Z**: Casual, trendy, emoji-rich content
    - **Professional**: Formal, business-focused content
    """)

if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set!")
        print("Please set it in your .env file or environment variables.")
    
    # Launch the interface
    iface.launch(share=True) 