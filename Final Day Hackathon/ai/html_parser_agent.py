# ai/html_parser_agent.py
import json
import re
import logging
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from utils import get_llm, normalize_to_list

# Configure logging
logger = logging.getLogger(__name__)

# Tool functions that use LLM
def parse_html_structure(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"html_content": args}
    html_content = args.get("html_content", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert HTML parser. Analyze this HTML content and extract its structure.

HTML Content:
{html_content}

Acceptance Criteria (ensure your output meets these):
• Parse ≥90% of tag structures correctly (tag name, attributes)
• Distinguish inline styles vs. external / class-based styles
• Preserve correct parent-child hierarchy and nesting order

Follow these steps to achieve the criteria:
1. Identify all HTML elements and their relationships
2. Extract semantic meaning and roles
3. Build component hierarchy tree
4. Separate inline style declarations from class / ID references
5. Capture important attributes (id, class, src, href, etc.)

Return ONLY a valid JSON object with this structure:
{{
  "components": [
    {{
      "tag": "header",
      "semantic_type": "container",
      "role": "banner",
      "attributes": {{
        "class": "main-header",
        "id": "header"
      }},
      "styles": {{
        "background-color": "#f0f0f0"
      }},
      "children": []
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(html_content=html_content))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in parse_html_structure: {str(e)}")
        return json.dumps({"error": str(e)})

def parse_css_styles(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"css_content": args}
    css_content = args.get("css_content", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert CSS parser. Analyze this CSS content and extract style rules.

CSS Content:
{css_content}

Follow these steps:
1. Parse all CSS selectors and their rules
2. Group related styles by purpose (layout, typography, etc.)
3. Identify design patterns and relationships
4. Note any responsive or conditional styles

Return ONLY a valid JSON object with this structure:
{{
  "styles": {{
    "layout_styles": {{
      ".main-header": {{
        "display": "flex",
        "justify-content": "space-between",
        "pattern": "flex-container"
      }}
    }},
    "visual_styles": {{
      ".main-header": {{
        "background-color": "#f0f0f0",
        "pattern": "neutral-background"
      }}
    }}
  }}
}}""")
        response = llm.invoke(prompt.format(css_content=css_content))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in parse_css_styles: {str(e)}")
        return json.dumps({"error": str(e)})

def merge_html_css(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"html_data": args}
    html_data = args.get("html_data", "")
    css_data = args.get("css_data", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at combining HTML structure with CSS styles. Merge this HTML and CSS data.

HTML Data:
{html_data}

CSS Data:
{css_data}

Follow these steps:
1. Match CSS selectors with HTML elements
2. Apply styles to matching components
3. Resolve any style conflicts
4. Maintain component hierarchy
5. Combine semantic information with styles

Return ONLY a valid JSON object with this structure:
{{
  "components": [
    {{
      "tag": "header",
      "semantic_type": "container",
      "role": "banner",
      "computed_styles": {{
        "display": "flex",
        "justify-content": "space-between",
        "background-color": "#f0f0f0"
      }},
      "pattern": "flex-container",
      "children": []
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(html_data=html_data, css_data=css_data))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in merge_html_css: {str(e)}")
        return json.dumps({"error": str(e)})

def create_html_parser_agent():
    """Create HTML parser agent with LLM-orchestrated tools"""
    logger.info("Creating HTML parser agent")
    
    # Define tools
    tools = [
        Tool(
            name="parse_html_structure",
            func=parse_html_structure,
            description="""Parse HTML content and extract structured component data. 
            Input: dict with key 'html_content' (raw HTML string)
            Output: JSON with component hierarchy, semantic types, and attributes"""
        ),
        Tool(
            name="parse_css_styles",
            func=parse_css_styles,
            description="""Parse CSS content and extract style rules and patterns. 
            Input: dict with key 'css_content' (raw CSS string)
            Output: JSON with grouped styles and identified patterns"""
        ),
        Tool(
            name="merge_html_css",
            func=merge_html_css,
            description="""Merge HTML structure with CSS styles.
            Input: dict with keys 'html_data' (JSON string) and 'css_data' (JSON string)
            Output: JSON with combined component and style data"""
        )
    ]
    
    # Get LLM
    llm = get_llm()
    
    # Prepare tool names
    tool_names = ", ".join([tool.name for tool in tools])
    # Create agent prompt
    prompt = PromptTemplate.from_template("""
You are an expert HTML/CSS parser agent. Your task is to analyze HTML and CSS content and produce structured component data.

You have access to the following tools:
{tools}

Tool names: {tool_names}

ALWAYS return the value for "components" as a LIST, even if there is only one item.

When you need to use a tool, always provide the Action Input as a JSON object with the correct keys. When you have the final answer, always return a valid JSON object with a top-level "components" key.

When you need to use a tool, use the following format:

Thought: Do I need to use a tool? Yes
Action: <tool name>
Action Input: <input to the tool>

When you have the final answer, use the format:

Thought: Do I need to use a tool? No
Final Answer: <your final answer as a JSON object>

Begin!

Current task: Parse and analyze this HTML content: {html_content} and CSS content: {css_content}

{agent_scratchpad}
""")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    def process_parsing(state: dict) -> dict:
        """Process HTML/CSS content using LLM-orchestrated tools"""
        logger.info("HTML Parser: Starting processing")
        
        try:
            # Let the LLM orchestrate the tool calling
            result = agent_executor.invoke({
                "html_content": state["html_content"],
                "css_content": state["css_content"],
                "tool_names": tool_names
            })
            
            # Parse the final result
            output = result.get("output", "{}")
            try:
                parsed_result = json.loads(output)
                if isinstance(parsed_result, dict) and "components" in parsed_result:
                    components = normalize_to_list(parsed_result["components"])
                    return {
                        **state,
                        "parsed_components": components,
                        "current_agent": "HTML_PARSER_COMPLETE"
                    }
                else:
                    # fallback: return the whole parsed_result as parsed_components
                    components = normalize_to_list(parsed_result)
                    return {
                        **state,
                        "parsed_components": components,
                        "current_agent": "HTML_PARSER_COMPLETE"
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing result: {str(e)}")
                # Try to extract JSON from text if direct parsing fails
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    try:
                        parsed_result = json.loads(json_match.group(0))
                        return {
                            **state,
                            "parsed_components": normalize_to_list(parsed_result),
                            "current_agent": "HTML_PARSER_COMPLETE"
                        }
                    except:
                        pass
                
                # Return error state if all parsing fails
                return {
                    **state,
                    "error": f"Failed to parse result: {str(e)}",
                    "current_agent": "ERROR",
                    "parsed_components": []
                }
                
        except Exception as e:
            logger.error(f"HTML Parser Error: {str(e)}")
            return {
                **state,
                "error": f"HTML Parser Error: {str(e)}",
                "current_agent": "ERROR",
                "parsed_components": []
            }
    
    return process_parsing