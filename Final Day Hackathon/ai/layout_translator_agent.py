# ai/layout_translator_agent.py
import json
import logging
import re
from typing import Dict, Any
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from utils import get_llm, normalize_to_list

# Configure logging
logger = logging.getLogger(__name__)

def analyze_layout_structure(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"components": args}
    components = args.get("components", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at analyzing UI layout structures.
Analyze these components and extract their layout relationships.

Components:
{components}

Acceptance Criteria:
• Handle flex, grid and absolute positioning layouts
• Produce responsive layouts with breakpoint hints (sm, md, lg, etc.)
• Maintain alignment, spacing and nesting rules of original HTML

Follow these steps:
1. Identify layout hierarchy and nesting
2. Detect layout patterns (grid, flex, etc.)
3. Analyze spacing and alignment
4. Map responsive behaviors
5. Identify layout constraints

Return ONLY a valid JSON object with this structure:
{{
  "layout_structure": {{
    "type": "flex",
    "direction": "column",
    "spacing": "lg",
    "children": [
      {{
        "type": "grid",
        "columns": 3,
        "spacing": "md",
        "children": []
      }}
    ]
  }},
  "responsive_breakpoints": [
    {{
      "width": "sm",
      "changes": {{
        "grid.columns": 1
      }}
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(components=components))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in analyze_layout_structure: {str(e)}")
        return json.dumps({"error": str(e)})

def translate_layout_styles(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"styles": args}
    styles = args.get("styles", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at translating CSS styles to LCNC layout properties.
Transform these CSS styles into LCNC-compatible layout properties.

Styles:
{styles}

Acceptance Criteria:
• Handle flex, grid and absolute positioning layouts
• Produce responsive layouts with breakpoint hints (sm, md, lg, etc.)
• Maintain alignment, spacing and nesting rules of original HTML

Follow these steps:
1. Map CSS layout properties to LCNC equivalents
2. Convert units to platform-specific values
3. Transform complex CSS into simple properties
4. Handle responsive styles
5. Optimize for LCNC platform

Return ONLY a valid JSON object with this structure:
{{
  "layout_properties": {{
    "container": {{
      "width": "full",
      "maxWidth": "1200px",
      "padding": {{
        "x": "md",
        "y": "lg"
      }},
      "gap": "md"
    }}
  }},
  "responsive_styles": {{
    "sm": {{
      "container.padding": {{
        "x": "sm",
        "y": "md"
      }}
    }}
  }}
}}""")
        response = llm.invoke(prompt.format(styles=styles))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in translate_layout_styles: {str(e)}")
        return json.dumps({"error": str(e)})

def optimize_layout_structure(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"layout": args}
    layout = args.get("layout", "")
    styles = args.get("styles", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at optimizing UI layouts for LCNC platforms.
Combine and optimize the layout structure with translated styles.

Layout:
{layout}

Styles:
{styles}

Acceptance Criteria:
• Handle flex, grid and absolute positioning layouts
• Produce responsive layouts with breakpoint hints (sm, md, lg, etc.)
• Maintain alignment, spacing and nesting rules of original HTML

Follow these steps:
1. Merge layout structure with style properties
2. Optimize component placement
3. Apply responsive optimizations
4. Ensure consistent spacing
5. Validate layout constraints

Return ONLY a valid JSON object with this structure:
{{
  "optimized_layout": {{
    "root": {{
      "type": "container",
      "properties": {{
        "maxWidth": "1200px",
        "margin": "auto",
        "padding": "lg"
      }},
      "children": [
        {{
          "type": "grid",
          "properties": {{
            "columns": {{
              "base": 1,
              "md": 2,
              "lg": 3
            }},
            "gap": "md"
          }}
        }}
      ]
    }}
  }},
  "layout_metadata": {{
    "breakpoints": ["sm", "md", "lg"],
    "spacing_scale": "geometric"
  }}
}}""")
        response = llm.invoke(prompt.format(
            layout=layout,
            styles=styles
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in optimize_layout_structure: {str(e)}")
        return json.dumps({"error": str(e)})

def create_layout_translator_agent():
    """Create Layout Translator agent with LLM-orchestrated tools"""
    logger.info("Creating Layout Translator agent")
    
    # Define tools
    tools = [
        Tool(
            name="analyze_layout_structure",
            func=analyze_layout_structure,
            description="""Analyze component layout structure.
            Input: dict with key 'components' (JSON string of component data)
            Output: JSON with layout structure and responsive breakpoints"""
        ),
        Tool(
            name="translate_layout_styles",
            func=translate_layout_styles,
            description="""Translate CSS styles to LCNC layout properties.
            Input: dict with key 'styles' (JSON string of style data)
            Output: JSON with translated layout properties"""
        ),
        Tool(
            name="optimize_layout_structure",
            func=optimize_layout_structure,
            description="""Optimize layout structure with translated styles.
            Input: dict with keys 'layout' (JSON string) and 'styles' (JSON string)
            Output: JSON with optimized layout structure"""
        )
    ]
    
    # Get LLM
    llm = get_llm()
    
    # Prepare tool names
    tool_names = ", ".join([tool.name for tool in tools])
    # Create agent prompt
    prompt = PromptTemplate.from_template("""
You are an expert Layout Translator agent. Your task is to analyze and optimize component layouts for LCNC platforms.

You have access to the following tools:
{tools}

Tool names: {tool_names}

ALWAYS return the value for "layout_structure" as a LIST, even if there is only one item.

When you need to use a tool, always provide the Action Input as a JSON object with the correct keys. When you have the final answer, always return a valid JSON object with a top-level "layout_structure" key.

When you need to use a tool, use the following format:

Thought: Do I need to use a tool? Yes
Action: <tool name>
Action Input: <input to the tool>

When you have the final answer, use the format:

Thought: Do I need to use a tool? No
Final Answer: <your final answer as a JSON object>

Begin!

Current task: Analyze and optimize this layout: {mapped_components}

{agent_scratchpad}
""")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    def process_layout(state: Dict[str, Any]) -> Dict[str, Any]:
        """Process layout translation using LLM-orchestrated tools"""
        logger.info("Layout Translator: Starting processing")
        
        try:
            # Let the LLM orchestrate the tool calling
            mc_json = json.dumps(state["mapped_components"])
            # Hard cap to avoid 16k-token overflow (≈4 chars ≈1 token simplistically)
            if len(mc_json) > 12000:
                mc_json = mc_json[:12000] + "...TRUNCATED"  # indicate truncation

            result = agent_executor.invoke({
                "mapped_components": mc_json,
                "tool_names": tool_names
            })
            
            # Parse the final result
            output = result.get("output", "{}")
            try:
                parsed_result = json.loads(output)
                if isinstance(parsed_result, dict) and "layout_structure" in parsed_result:
                    layout_structure = normalize_to_list(parsed_result["layout_structure"])
                    return {
                        **state,
                        "layout_structure": layout_structure,
                        "responsive_config": parsed_result.get("responsive_config", {}),
                        "current_agent": "LAYOUT_TRANSLATOR_COMPLETE"
                    }
                else:
                    layout_structure = normalize_to_list(parsed_result)
                    return {
                        **state,
                        "layout_structure": layout_structure,
                        "responsive_config": parsed_result.get("responsive_config", {}),
                        "current_agent": "LAYOUT_TRANSLATOR_COMPLETE"
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing result: {str(e)}")
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    try:
                        parsed_result = json.loads(json_match.group(0))
                        return {
                            **state,
                            "layout_structure": normalize_to_list(parsed_result),
                            "responsive_config": parsed_result.get("responsive_config", {}),
                            "current_agent": "LAYOUT_TRANSLATOR_COMPLETE"
                        }
                    except:
                        pass
                
                # Graceful fallback: continue with empty layout_structure
                return {
                    **state,
                    "layout_structure": normalize_to_list({}),
                    "responsive_config": {},
                    "current_agent": "LAYOUT_TRANSLATOR_COMPLETE"
                }
                
        except Exception as e:
            logger.error(f"Layout Translator Error: {str(e)}")
            return {
                **state,
                "error": f"Layout Translator Error: {str(e)}",
                "current_agent": "ERROR",
                "layout_structure": normalize_to_list({}),
                "responsive_config": {}
            }
    
    return process_layout