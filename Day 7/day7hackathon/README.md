# Persona-Driven Content Optimizer

A multi-agent system that optimizes website content for different audience segments using LangChain and OpenAI's GPT models.

## Features

- 🎯 Automatic persona detection (Gen Z vs Professional)
- ✨ Content style adaptation using RAG (Retrieval Augmented Generation)
- 🔄 Smart content refinement based on audience preferences
- 📢 CTA (Call-to-Action) optimization
- 🎨 Beautiful Gradio web interface

## System Architecture

The system consists of four specialized agents:

1. **Persona Detection Agent**: Identifies the target audience segment
2. **Style Retriever Agent**: Uses RAG to find relevant style examples
3. **Content Refinement Agent**: Rewrites content to match persona preferences
4. **CTA Optimization Agent**: Suggests optimized call-to-actions

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd persona-driven-content-optimizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Open the provided URL in your browser

3. Paste your HTML content into the input box

4. Choose your target persona (or let the system auto-detect)

5. Click "Optimize Content" to get your persona-optimized content

## Example Input

```html
<div>
    <h1>Welcome to Our Platform</h1>
    <p>Our advanced software solution helps businesses streamline their operations and increase productivity.</p>
    <button>Get Started Now</button>
</div>
```

## Sample Output

The system will:
- Detect the current audience (Professional in this case)
- Optimize the content for the target persona
- Provide alternative CTAs
- Generate a detailed optimization report

## Requirements

- Python 3.8+
- OpenAI API key
- Required packages listed in `requirements.txt`

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License - feel free to use this project for your own purposes. 