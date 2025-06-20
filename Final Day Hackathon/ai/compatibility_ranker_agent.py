# ai/compatibility_ranker_agent.py
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

def analyze_component_compatibility(args: dict) -> str:
    components = args.get("components", "")
    patterns = args.get("patterns", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at analyzing component compatibility.
Analyze how well these components work together and with their patterns.

Components:
{components}

Patterns:
{patterns}

Follow these steps:
1. Analyze component relationships
2. Check pattern implementation quality
3. Verify property consistency
4. Assess accessibility compliance
5. Evaluate responsive behavior

Return ONLY a valid JSON object with this structure:
{{
  "compatibility_scores": [
    {{
      "component_id": "header-1",
      "pattern_score": 0.95,
      "accessibility_score": 0.9,
      "responsive_score": 0.85,
      "overall_score": 0.9,
      "issues": [],
      "recommendations": []
    }}
  ],
  "global_scores": {{
    "pattern_fidelity": 0.92,
    "accessibility": 0.88,
    "responsive_design": 0.85
  }}
}}""")
        response = llm.invoke(prompt.format(
            components=components,
            patterns=patterns
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in analyze_component_compatibility: {str(e)}")
        return json.dumps({"error": str(e)})

def rank_implementation_options(args: dict) -> str:
    components = args.get("components", "")
    compatibility = args.get("compatibility", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at ranking UI implementation options.
Rank and prioritize implementation options based on compatibility analysis.

Components:
{components}

Compatibility Analysis:
{compatibility}

Follow these steps:
1. Evaluate implementation options
2. Consider technical constraints
3. Assess maintainability
4. Check scalability
5. Analyze performance impact

Return ONLY a valid JSON object with this structure:
{{
  "ranked_options": [
    {{
      "component_id": "header-1",
      "implementation_rank": 1,
      "score": 0.95,
      "benefits": [
        "optimal accessibility",
        "responsive performance"
      ],
      "trade_offs": [
        "higher complexity"
      ]
    }}
  ],
  "ranking_criteria": {{
    "accessibility_weight": 0.3,
    "performance_weight": 0.3,
    "maintainability_weight": 0.2,
    "scalability_weight": 0.2
  }}
}}""")
        response = llm.invoke(prompt.format(
            components=components,
            compatibility=compatibility
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in rank_implementation_options: {str(e)}")
        return json.dumps({"error": str(e)})

def optimize_component_selection(args: dict) -> str:
    rankings = args.get("rankings", "")
    compatibility = args.get("compatibility", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at optimizing UI component selection.
Optimize the final component selection based on rankings and compatibility.

Rankings:
{rankings}

Compatibility:
{compatibility}

Follow these steps:
1. Select optimal components
2. Balance trade-offs
3. Ensure system cohesion
4. Verify requirements
5. Validate selections

Return ONLY a valid JSON object with this structure:
{{
  "optimized_components": [
    {{
      "component_id": "header-1",
      "selected_implementation": {{
        "pattern": "hero_section",
        "variant": "centered",
        "properties": {{
          "layout": "flex",
          "spacing": "lg"
        }}
      }},
      "optimization_score": 0.95,
      "requirements_met": [
        "accessibility",
        "responsive"
      ]
    }}
  ],
  "optimization_metadata": {{
    "overall_score": 0.92,
    "trade_offs_accepted": [
      {{
        "type": "complexity",
        "benefit": "better accessibility"
      }}
    ]
  }}
}}""")
        response = llm.invoke(prompt.format(
            rankings=rankings,
            compatibility=compatibility
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in optimize_component_selection: {str(e)}")
        return json.dumps({"error": str(e)})

def rank_component_compatibility(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"components": args}
    components = args.get("components", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at ranking component compatibility for LCNC platforms.
Analyze these components and rank their compatibility.

Components:
{components}

Return ONLY a valid JSON object with this structure:
{{
  "compatibility": [
    {{
      "component": "CardList",
      "score": 0.95,
      "issues": [],
      "recommendations": ["Use built-in CardList for best results"]
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(components=components))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in rank_component_compatibility: {str(e)}")
        return json.dumps({"error": str(e)})

def suggest_compatibility_fixes(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"compatibility": args}
    compatibility = args.get("compatibility", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at suggesting fixes for LCNC compatibility issues.
Given these compatibility results, suggest fixes and improvements.

Compatibility:
{compatibility}

Return ONLY a valid JSON object with this structure:
{{
  "fixes": [
    {{
      "component": "CustomButton",
      "fix": "Replace with built-in Button for full compatibility"
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(compatibility=compatibility))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in suggest_compatibility_fixes: {str(e)}")
        return json.dumps({"error": str(e)})

def create_compatibility_ranker_agent():
    """Create Compatibility Ranker agent with LLM-orchestrated tools"""
    logger.info("Creating Compatibility Ranker agent")
    
    # Define tools
    tools = [
        Tool(
            name="analyze_component_compatibility",
            func=analyze_component_compatibility,
            description="""Analyze component compatibility.
            Input: dict with keys 'components' (JSON string) and 'patterns' (JSON string)
            Output: JSON with compatibility scores"""
        ),
        Tool(
            name="rank_implementation_options",
            func=rank_implementation_options,
            description="""Rank implementation options.
            Input: dict with keys 'components' (JSON string) and 'compatibility' (JSON string)
            Output: JSON with ranked options"""
        ),
        Tool(
            name="optimize_component_selection",
            func=optimize_component_selection,
            description="""Optimize component selection.
            Input: dict with keys 'rankings' (JSON string) and 'compatibility' (JSON string)
            Output: JSON with optimized selections"""
        ),
        Tool(
            name="rank_component_compatibility",
            func=rank_component_compatibility,
            description="""Rank component compatibility for LCNC platforms.
            Input: dict with key 'components' (JSON string)
            Output: JSON with ranked compatibility"""
        ),
        Tool(
            name="suggest_compatibility_fixes",
            func=suggest_compatibility_fixes,
            description="""Suggest compatibility fixes for LCNC platforms.
            Input: dict with key 'compatibility' (JSON string)
            Output: JSON with suggested fixes"""
        )
    ]
    
    # Get LLM
    llm = get_llm()
    
    # Prepare tool names
    tool_names = ", ".join([tool.name for tool in tools])
    # Create agent prompt
    prompt = PromptTemplate.from_template("""
You are an expert Compatibility Ranker agent. Your task is to rank and improve component compatibility for LCNC platforms.

Acceptance Criteria:
• Score each component on mapping, layout fidelity, property completeness
• Generate summary of gaps (e.g., "2 components missing hover style")
• Return components ordered by descending overall_score

You have access to the following tools:
{tools}

Tool names: {tool_names}

ALWAYS return the value for "compatibility" as a LIST, even if there is only one item.

When you need to use a tool, always provide the Action Input as a JSON object with the correct keys. When you have the final answer, always return a valid JSON object with a top-level "compatibility" key.

When you need to use a tool, use the following format:

Thought: Do I need to use a tool? Yes
Action: <tool name>
Action Input: <input to the tool>

When you have the final answer, use the format:

Thought: Do I need to use a tool? No
Final Answer: <your final answer as a JSON object>

Begin!

Current task: Rank and improve compatibility for these components: {optimized_components}

{agent_scratchpad}
""")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    def process_compatibility(state: dict) -> dict:
        logger.info("Compatibility Ranker: Starting processing")
        try:
            # Defensive fallback: use mapped_components if optimized_components is missing
            optimized_components = state.get("optimized_components", state.get("mapped_components", []))
            result = agent_executor.invoke({
                "optimized_components": json.dumps(optimized_components),
                "tool_names": tool_names
            })
            output = result.get("output", "{}")
            try:
                parsed_result = json.loads(output)
                if isinstance(parsed_result, dict) and "compatibility" in parsed_result:
                    compatibility = normalize_to_list(parsed_result["compatibility"])
                    return {
                        **state,
                        "compatibility": compatibility,
                        "fixes": parsed_result.get("fixes", []),
                        "current_agent": "COMPATIBILITY_RANKER_COMPLETE"
                    }
                else:
                    compatibility = normalize_to_list(parsed_result)
                    return {
                        **state,
                        "compatibility": compatibility,
                        "fixes": parsed_result.get("fixes", []),
                        "current_agent": "COMPATIBILITY_RANKER_COMPLETE"
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing result: {str(e)}")
                json_match = re.search(r'\{[\s\S]*\}', output)
                if json_match:
                    try:
                        parsed_result = json.loads(json_match.group(0))
                        return {
                            **state,
                            "compatibility": normalize_to_list(parsed_result),
                            "fixes": parsed_result.get("fixes", []),
                            "current_agent": "COMPATIBILITY_RANKER_COMPLETE"
                        }
                    except:
                        pass
                # Fallback: return empty compatibility but continue workflow
                return {
                    **state,
                    "compatibility": [],
                    "fixes": [],
                    "current_agent": "COMPATIBILITY_RANKER_COMPLETE"
                }
        except Exception as e:
            logger.error(f"Compatibility Ranker Error: {str(e)}")
            return {
                **state,
                "error": f"Compatibility Ranker Error: {str(e)}",
                "current_agent": "ERROR",
                "compatibility": [],
                "fixes": []
            }
    return process_compatibility