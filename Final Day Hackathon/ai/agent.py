# ai/agent.py
import json
import logging
from typing import Dict, Any, Annotated, TypedDict, Union, List
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from html_parser_agent import create_html_parser_agent
from component_mapper_agent import create_component_mapper_agent
from layout_translator_agent import create_layout_translator_agent
from rag_pattern_agent import create_rag_pattern_agent
from compatibility_ranker_agent import create_compatibility_ranker_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define state type
class WorkflowState(TypedDict):
    html_content: str
    css_content: str
    current_agent: str
    error: Union[str, None]
    parsed_components: list
    mapped_components: list
    layout_structure: dict
    matched_patterns: list
    ranked_components: list
    pattern_metadata: dict
    ranking_metadata: dict
    responsive_config: dict

def create_workflow_graph() -> StateGraph:
    """Create the workflow graph using LangGraph"""
    logger.info("Creating workflow graph")
    
    # Create workflow graph with state schema
    workflow = StateGraph(WorkflowState)
    
    # Create agents
    html_parser = create_html_parser_agent()
    component_mapper = create_component_mapper_agent()
    layout_translator = create_layout_translator_agent()
    rag_pattern = create_rag_pattern_agent()
    compatibility_ranker = create_compatibility_ranker_agent()
    
    # Add nodes
    workflow.add_node("HTML_PARSER", html_parser)
    workflow.add_node("COMPONENT_MAPPER", component_mapper)
    workflow.add_node("LAYOUT_TRANSLATOR", layout_translator)
    workflow.add_node("RAG_PATTERN", rag_pattern)
    workflow.add_node("COMPATIBILITY_RANKER", compatibility_ranker)
    
    # Define conditional routing
    def route_to_mapper(state: Dict) -> str:
        """Route to component mapper if HTML parsing succeeded"""
        if state.get("error"):
            return "ERROR"
        if state.get("current_agent") == "HTML_PARSER_COMPLETE":
            return "COMPONENT_MAPPER"
        return "HTML_PARSER"
    
    def route_to_translator(state: Dict) -> str:
        """Route to layout translator if component mapping succeeded"""
        if state.get("error"):
            return "ERROR"
        if state.get("current_agent") == "COMPONENT_MAPPER_COMPLETE":
            return "LAYOUT_TRANSLATOR"
        return "COMPONENT_MAPPER"
    
    def route_to_rag(state: Dict) -> str:
        """Route to RAG pattern agent if layout translation succeeded"""
        if state.get("error"):
            return "ERROR"
        if state.get("current_agent") == "LAYOUT_TRANSLATOR_COMPLETE":
            return "RAG_PATTERN"
        return "LAYOUT_TRANSLATOR"
    
    def route_to_ranker(state: Dict) -> str:
        """Route to compatibility ranker if RAG pattern matching succeeded"""
        if state.get("error"):
            return "ERROR"
        if state.get("current_agent") == "RAG_PATTERN_COMPLETE":
            return "COMPATIBILITY_RANKER"
        return "RAG_PATTERN"
    
    def route_to_end(state: Dict) -> str:
        """Route to 'end' string so conditional edge mapping matches the END node"""
        if state.get("error") or state.get("current_agent") == "COMPATIBILITY_RANKER_COMPLETE":
            return "end"
        return "COMPATIBILITY_RANKER"
    
    # Add edges with conditional routing
    workflow.add_conditional_edges(
        "HTML_PARSER",
        route_to_mapper,
        {
            "COMPONENT_MAPPER": "COMPONENT_MAPPER",
            "ERROR": "ERROR",
            "HTML_PARSER": "HTML_PARSER"
        }
    )
    
    workflow.add_conditional_edges(
        "COMPONENT_MAPPER",
        route_to_translator,
        {
            "LAYOUT_TRANSLATOR": "LAYOUT_TRANSLATOR",
            "ERROR": "ERROR",
            "COMPONENT_MAPPER": "COMPONENT_MAPPER"
        }
    )
    
    workflow.add_conditional_edges(
        "LAYOUT_TRANSLATOR",
        route_to_rag,
        {
            "RAG_PATTERN": "RAG_PATTERN",
            "ERROR": "ERROR",
            "LAYOUT_TRANSLATOR": "LAYOUT_TRANSLATOR"
        }
    )
    
    workflow.add_conditional_edges(
        "RAG_PATTERN",
        route_to_ranker,
        {
            "COMPATIBILITY_RANKER": "COMPATIBILITY_RANKER",
            "ERROR": "ERROR",
            "RAG_PATTERN": "RAG_PATTERN"
        }
    )
    
    workflow.add_conditional_edges(
        "COMPATIBILITY_RANKER",
        route_to_end,
        {
            "end": END,
            "COMPATIBILITY_RANKER": "COMPATIBILITY_RANKER"
        }
    )
    
    # Add error handling
    def handle_error(state: Dict) -> Dict:
        """Handle error state"""
        return {
            **state,
            "current_agent": "ERROR",
            "error": state.get("error", "Unknown error occurred")
        }
    
    workflow.add_node("ERROR", handle_error)
    
    # Set entry point
    workflow.set_entry_point("HTML_PARSER")
    
    # Compile the graph
    return workflow.compile()

def process_html_to_lcnc(html_content: str, css_content: str) -> Dict[str, Any]:
    """Process HTML/CSS content through the agent workflow"""
    logger.info("Starting HTML to LCNC conversion")
    
    try:
        # Create initial state
        initial_state: WorkflowState = {
            "html_content": html_content,
            "css_content": css_content,
            "current_agent": "START",
            "error": None,
            "parsed_components": [],
            "mapped_components": [],
            "layout_structure": {},
            "matched_patterns": [],
            "ranked_components": [],
            "pattern_metadata": {},
            "ranking_metadata": {},
            "responsive_config": {}
        }
        
        # Create and run workflow
        workflow = create_workflow_graph()
        final_state = workflow.invoke(initial_state)
        
        # Decide which structure to return for LCNC rendering
        lcnc_structure = (
            final_state.get("layout_structure")
            or final_state.get("optimized_components")
            or final_state.get("mapped_components")
            or final_state.get("parsed_components")
            or []
        )

        # Build analysis report by gathering everything that is useful for consumers
        analysis_report = {
            "matched_patterns": final_state.get("matched_patterns", []),
            "pattern_metadata": final_state.get("pattern_metadata", {}),
            "compatibility": final_state.get("compatibility", []),
            "fixes": final_state.get("fixes", []),
            "ranking_metadata": final_state.get("ranking_metadata", {}),
            "responsive_config": final_state.get("responsive_config", {}),
            "workflow_agent": final_state.get("current_agent")
        }

        return {
            "error": final_state.get("error"),
            "lcnc_structure": lcnc_structure,
            "analysis_report": analysis_report
        }
        
    except Exception as e:
        logger.error(f"Error in workflow execution: {str(e)}")
        return {
            "error": f"Workflow execution error: {str(e)}",
            "lcnc_structure": [],
            "analysis_report": {}
        }