# ai/rag_pattern_agent.py
import json
import logging
import re
from typing import Dict, Any
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from utils import get_llm, normalize_to_list
try:
    from .vector_store import get_store  # when ai is a package
except ImportError:
    from vector_store import get_store  # when running inside ai directory as script

# Configure logging
logger = logging.getLogger(__name__)

# Updated: use Chroma similarity search instead of LLM
_store = None

def _ensure_store():
    global _store
    if _store is None:
        _store = get_store()

def retrieve_similar_patterns(args: dict) -> str:
    # Defensive handling if args is passed as a raw JSON string
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            # Fallback: wrap the string as component_data
            args = {"component_data": args}
    component_data = args.get("component_data", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at identifying UI patterns.
Search for patterns that match these components.

Component Data:
{component_data}

Follow these steps:
1. Analyze component structure and purpose
2. Match with common UI patterns
3. Consider layout and interaction patterns
4. Look for design system patterns
5. Identify accessibility patterns

Return ONLY a valid JSON object with this structure:
{{
  "matched_patterns": [
    {{
      "pattern_name": "hero_section",
      "confidence": 0.95,
      "matches": [
        {{
          "component_id": "header-1",
          "pattern_role": "container"
        }}
      ],
      "requirements": [
        "full-width background",
        "centered content"
      ]
    }}
  ],
  "pattern_categories": [
    "layout",
    "navigation",
    "content"
  ]
}}""")
        response = llm.invoke(prompt.format(component_data=component_data))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in retrieve_similar_patterns: {str(e)}")
        return json.dumps({"error": str(e)})

def analyze_pattern_compatibility(args: dict) -> str:
    patterns = args.get("patterns", "")
    layout = args.get("layout", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at analyzing UI pattern compatibility.
Analyze how well these patterns fit with the layout structure.

Patterns:
{patterns}

Layout:
{layout}

Follow these steps:
1. Check pattern layout requirements
2. Verify spacing and alignment needs
3. Analyze responsive behavior compatibility
4. Check for pattern conflicts
5. Validate accessibility requirements

Return ONLY a valid JSON object with this structure:
{{
  "compatibility_analysis": [
    {{
      "pattern": "hero_section",
      "compatibility_score": 0.9,
      "layout_requirements_met": true,
      "potential_issues": [],
      "suggested_adjustments": [
        {{
          "type": "spacing",
          "suggestion": "increase vertical gap"
        }}
      ]
    }}
  ],
  "overall_compatibility": 0.85
}}""")
        response = llm.invoke(prompt.format(
            patterns=patterns,
            layout=layout
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in analyze_pattern_compatibility: {str(e)}")
        return json.dumps({"error": str(e)})

def generate_pattern_implementation(args: dict) -> str:
    patterns = args.get("patterns", "")
    compatibility = args.get("compatibility", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at implementing UI patterns.
Generate implementation details for these patterns based on compatibility analysis.

Patterns:
{patterns}

Compatibility Analysis:
{compatibility}

Follow these steps:
1. Create detailed implementation plan
2. Specify required properties
3. Define component relationships
4. Include responsive behavior
5. Add accessibility features

Return ONLY a valid JSON object with this structure:
{{
  "pattern_implementations": [
    {{
      "pattern": "hero_section",
      "implementation": {{
        "component_type": "Container",
        "properties": {{
          "layout": "flex",
          "direction": "column",
          "align": "center"
        }},
        "children": [
          {{
            "component_type": "Heading",
            "properties": {{
              "size": "2xl",
              "color": "primary"
            }}
          }}
        ]
      }},
      "responsive_behavior": {{
        "mobile": {{
          "spacing": "md",
          "text_size": "xl"
        }}
      }}
    }}
  ],
  "implementation_metadata": {{
    "accessibility_features": [
      "aria-labels",
      "semantic-structure"
    ],
    "required_dependencies": []
  }}
}}""")
        response = llm.invoke(prompt.format(
            patterns=patterns,
            compatibility=compatibility
        ))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in generate_pattern_implementation: {str(e)}")
        return json.dumps({"error": str(e)})

def retrieve_pattern_matches(args: dict) -> str:
    """Retrieve pattern docs from vector DB most similar to query/component text."""
    if isinstance(args, str):
        query = args
    else:
        query = args.get("query") or args.get("component_data", "")

    try:
        _ensure_store()
        docs = _store.similarity_search(query, k=5)
        patterns = [d.metadata for d in docs]
        return json.dumps({"patterns": patterns})
    except Exception as e:
        logger.error(f"Error in retrieve_pattern_matches: {str(e)}")
        return json.dumps({"error": str(e)})

def suggest_pattern_applications(args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"patterns": args}
    patterns = args.get("patterns", "")
    components = args.get("components", "")
    try:
        llm = get_llm()
        prompt = PromptTemplate.from_template("""You are an expert at applying UI/UX patterns to component structures.
Given these patterns and components, suggest how to apply the patterns.

Patterns:
{patterns}

Components:
{components}

Return ONLY a valid JSON object with this structure:
{{
  "pattern_applications": [
    {{
      "pattern": "card_list",
      "applied_to": "main_content",
      "modifications": ["group cards into CardList"]
    }}
  ]
}}""")
        response = llm.invoke(prompt.format(patterns=patterns, components=components))
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in suggest_pattern_applications: {str(e)}")
        return json.dumps({"error": str(e)})

def create_rag_pattern_agent():
    """Create RAG Pattern agent with LLM-orchestrated tools"""
    logger.info("Creating RAG Pattern agent")
    
    # Define tools
    tools = [
        Tool(
            name="retrieve_similar_patterns",
            func=retrieve_similar_patterns,
            description="""Search for UI patterns matching components.
            Input: dict with key 'component_data' (JSON string of component data)
            Output: JSON with matched patterns and categories"""
        ),
        Tool(
            name="analyze_pattern_compatibility",
            func=analyze_pattern_compatibility,
            description="""Analyze pattern compatibility with layout.
            Input: dict with keys 'patterns' (JSON string) and 'layout' (JSON string)
            Output: JSON with compatibility analysis"""
        ),
        Tool(
            name="generate_pattern_implementation",
            func=generate_pattern_implementation,
            description="""Generate pattern implementation details.
            Input: dict with keys 'patterns' (JSON string) and 'compatibility' (JSON string)
            Output: JSON with implementation details"""
        ),
        Tool(
            name="retrieve_pattern_matches",
            func=retrieve_pattern_matches,
            description="""Retrieve UI/UX patterns from a knowledge base.
            Input: query string or dict with key 'query'
            Output: JSON with retrieved patterns"""
        ),
        Tool(
            name="suggest_pattern_applications",
            func=suggest_pattern_applications,
            description="""Suggest pattern applications to component structures.
            Input: dict with keys 'patterns' (JSON string) and 'components' (JSON string)
            Output: JSON with suggested pattern applications"""
        )
    ]
    
    # Get LLM
    llm = get_llm()
    
    # Prepare tool names
    tool_names = ", ".join([tool.name for tool in tools])
    # Create agent prompt
    prompt = PromptTemplate.from_template("""
You are an expert RAG Pattern agent. Your task is to retrieve and apply UI/UX patterns to component structures.

Acceptance Criteria:
• Retrieve patterns from internal LCNC-compatible design corpus (Chroma DB)
• Suggest closest alternatives when component fidelity is low
• Provide context-aware hints like "Use Card Block with Flex Row"

You have access to the following tools:
{tools}

Tool names: {tool_names}

ALWAYS return the value for "patterns" as a LIST, even if there is only one item.

When you need to use a tool, always provide the Action Input as a JSON object with the correct keys. When you have the final answer, always return a valid JSON object with a top-level "patterns" key.

When you need to use a tool, use the following format:

Thought: Do I need to use a tool? Yes
Action: <tool name>
Action Input: <input to the tool>

When you have the final answer, use the format:

Thought: Do I need to use a tool? No
Final Answer: <your final answer as a JSON object>

Begin!

Current task: Retrieve and apply patterns for these components: {mapped_components}

{agent_scratchpad}
""")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    def process_rag(state: dict) -> dict:
        """Deterministic RAG retrieval without LLM orchestration"""
        logger.info("RAG Pattern Agent: Deterministic retrieval start")
        try:
            comp_json = json.dumps(state.get("mapped_components", []))
            raw = retrieve_similar_patterns({"component_data": comp_json})
            data = json.loads(raw) if isinstance(raw, str) else raw
            patterns = normalize_to_list(data.get("matched_patterns") or data.get("patterns"))
            return {
                **state,
                "patterns": patterns,
                "current_agent": "RAG_PATTERN_COMPLETE"
            }
        except Exception as e:
            logger.error(f"RAG Pattern deterministic error: {str(e)}")
            return {
                **state,
                "error": f"RAG Pattern error: {str(e)}",
                "current_agent": "ERROR",
                "patterns": []
            }
    return process_rag