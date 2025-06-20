# ai/component_mapper_agent.py
import json
import re
import logging
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from utils import get_llm, normalize_to_list
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def map_semantic_components(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"component_data": args}
    component_data = args.get("component_data", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at mapping HTML components to semantic LCNC components.
Analyze these HTML components and map them to appropriate LCNC components.

Component Data:
{component_data}

Acceptance Criteria:
• Accurately map common tags (div, span, img, button, a, form, etc.) to LCNC blocks
• Use classes / IDs to infer semantic roles when possible
• When no direct LCNC mapping exists, flag component with "unmappable": true

Follow these steps:
1. Analyze each HTML component's structure and purpose
2. Map to the most appropriate LCNC component type
3. Preserve component hierarchy and relationships
4. Map attributes and styles to LCNC properties
5. Identify reusable patterns

Return ONLY a valid JSON object with this structure:
{{
  "mapped_components": [
    {{
      "original_tag": "header",
      "lcnc_type": "Container",
      "semantic_role": "banner",
      "properties": {{
        "layout": "flex",
        "spacing": "between",
        "background": "neutral"
      }},
      "children": []
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(component_data=component_data))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in map_semantic_components: {str(e)}")
        return json.dumps({"error": str(e)})

def analyze_component_patterns(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"components": args}
    components = args.get("components", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at identifying UI component patterns.
Analyze these components and identify reusable patterns and optimizations.

Components:
{components}

Follow these steps:
1. Identify repeating component structures
2. Detect common UI patterns
3. Suggest component abstractions
4. Identify shared properties
5. Recommend optimizations

Return ONLY a valid JSON object with this structure:
{{
  "patterns": [
    {{
      "pattern_name": "card_list",
      "components": ["Card", "List", "Image"],
      "frequency": 3,
      "optimization": "Create reusable CardList component"
    }}
  ],
  "optimizations": [
    {{
      "type": "abstraction",
      "suggestion": "Extract shared styles into theme",
      "affected_components": ["header", "footer"]
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(components=components))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in analyze_component_patterns: {str(e)}")
        return json.dumps({"error": str(e)})

def optimize_component_structure(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"components": args}
    components = args.get("components", "")
    patterns = args.get("patterns", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at optimizing UI component structures.
Apply these patterns to optimize the component structure.

Components:
{components}

Patterns:
{patterns}

Follow these steps:
1. Apply identified patterns
2. Create reusable components
3. Optimize component hierarchy
4. Apply suggested abstractions
5. Maintain component relationships

Return ONLY a valid JSON object with this structure:
{{
  "optimized_components": [
    {{
      "lcnc_type": "CardList",
      "properties": {{
        "layout": "grid",
        "spacing": "md"
      }},
      "children": [
        {{
          "lcnc_type": "Card",
          "properties": {{
            "variant": "primary"
          }}
        }}
      ]
    }}
  ],
  "applied_patterns": [
    {{
      "pattern": "card_list",
      "location": "main_content"
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(
            components=components,
            patterns=patterns
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in optimize_component_structure: {str(e)}")
        return json.dumps({"error": str(e)})

def create_component_mapper_agent():
    """Create Component Mapper agent with LLM-orchestrated tools"""
    logger.info("Creating Component Mapper agent")
    
    # Define tools
    tools = [
        Tool(
            name="map_semantic_components",
            func=map_semantic_components,
            description="""Map HTML components to semantic LCNC components.
            Input: dict with key 'component_data' (JSON string of HTML component data)
            Output: JSON with mapped LCNC components"""
        ),
        Tool(
            name="analyze_component_patterns",
            func=analyze_component_patterns,
            description="""Analyze components for patterns and optimizations.
            Input: dict with key 'components' (JSON string of component data)
            Output: JSON with identified patterns and optimizations"""
        ),
        Tool(
            name="optimize_component_structure",
            func=optimize_component_structure,
            description="""Optimize component structure using identified patterns.
            Input: dict with keys 'components' (JSON string) and 'patterns' (JSON string)
            Output: JSON with optimized component structure"""
        )
    ]
    
    # Get LLM
    llm = get_llm()
    
    # Prepare tool names
    tool_names = ", ".join([tool.name for tool in tools])
    # Create agent prompt
    prompt = PromptTemplate.from_template("""
You are an expert Component Mapper agent. Your task is to map HTML components to LCNC components and optimize their structure.

You have access to the following tools:
{tools}

Tool names: {tool_names}

ALWAYS return the value for "mapped_components" as a LIST, even if there is only one item.

When you need to use a tool, always provide the Action Input as a JSON object with the correct keys. When you have the final answer, always return a valid JSON object with a top-level "mapped_components" key.

When you need to use a tool, use the following format:

Thought: Do I need to use a tool? Yes
Action: <tool name>
Action Input: <input to the tool>

When you have the final answer, use the format:

Thought: Do I need to use a tool? No
Final Answer: <your final answer as a JSON object>

Begin!

Current task: Map and optimize these components: {parsed_components}

{agent_scratchpad}
""")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    def process_mapping(state: Dict[str, Any]) -> Dict[str, Any]:
        """Process component mapping using LLM-orchestrated tools"""
        logger.info("Component Mapper: Starting processing")
        
        try:
            # Let the LLM orchestrate the tool calling
            result = agent_executor.invoke({
                "parsed_components": json.dumps(state["parsed_components"]),
                "tool_names": tool_names
            })
            
            # Parse the final result
            output = result.get("output", "{}")
            try:
                parsed_result = json.loads(output)
                if isinstance(parsed_result, dict) and "mapped_components" in parsed_result:
                    mapped_components = normalize_to_list(parsed_result["mapped_components"])
                    return {
                        **state,
                        "mapped_components": mapped_components,
                        "applied_patterns": parsed_result.get("applied_patterns", []),
                        "current_agent": "COMPONENT_MAPPER_COMPLETE"
                    }
                else:
                    mapped_components = normalize_to_list(parsed_result)
                    return {
                        **state,
                        "mapped_components": mapped_components,
                        "applied_patterns": parsed_result.get("applied_patterns", []),
                        "current_agent": "COMPONENT_MAPPER_COMPLETE"
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing result: {str(e)}")
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    try:
                        parsed_result = json.loads(json_match.group(0))
                        return {
                            **state,
                            "mapped_components": normalize_to_list(parsed_result),
                            "applied_patterns": parsed_result.get("applied_patterns", []),
                            "current_agent": "COMPONENT_MAPPER_COMPLETE"
                        }
                    except:
                        pass
                
                # Return error state if all parsing fails
                return {
                    **state,
                    "error": f"Failed to parse result: {str(e)}",
                    "current_agent": "ERROR",
                    "mapped_components": [],
                    "applied_patterns": []
                }
                
        except Exception as e:
            logger.error(f"Component Mapper Error: {str(e)}")
            return {
                **state,
                "error": f"Component Mapper Error: {str(e)}",
                "current_agent": "ERROR",
                "mapped_components": [],
                "applied_patterns": []
            }
    
    return process_mapping