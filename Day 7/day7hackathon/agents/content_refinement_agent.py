from .base_agent import BaseAgent

class ContentRefinementAgent(BaseAgent):
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        super().__init__(model_name, temperature)
    
    def process(self, content, persona, style_examples):
        """
        Rewrite content to match the target persona and style
        Args:
            content (str): Original content to rewrite
            persona (str): Target persona ('genz' or 'professional')
            style_examples (list): Retrieved style examples to base the rewrite on
        Returns:
            str: Rewritten content
        """
        # Create a detailed prompt using style examples
        style_prompt = "\n".join([
            f"Style Example {i+1}:",
            f"Content: {ex['content']}",
            f"Style: {ex['style']}"
            for i, ex in enumerate(style_examples)
        ])
        
        system_prompt = f"""You are an expert content writer specializing in writing for {'Generation Z' if persona == 'genz' else 'Professional'} audiences.
        Your task is to rewrite the given content to match the style and tone appropriate for the target audience.
        Use the provided style examples as inspiration for the tone, vocabulary, and writing style.
        
        For Generation Z, focus on:
        - Casual, conversational tone
        - Modern slang and emoji usage
        - Short, punchy sentences
        - Engaging and relatable language
        
        For Professionals, focus on:
        - Formal, business-appropriate tone
        - Industry-standard terminology
        - Clear, concise communication
        - Data-driven and solution-focused language
        
        Here are some style examples to guide you:
        {style_prompt}
        
        Maintain the same key information and message, but adapt the style completely."""
        
        user_prompt = f"Please rewrite this content:\n\n{content}"
        
        messages = self._create_messages(system_prompt, user_prompt)
        response = self.llm.invoke(messages)
        
        return response.content 