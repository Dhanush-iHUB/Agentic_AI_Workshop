"""
Example content for training the vector store with persona-specific content examples.
"""

EXAMPLE_CONTENT = {
    "gen_z": [
        {
            "text": "🔥 Level up your Instagram game with our new filters! Perfect for creating those viral moments that'll make your friends go 'sheeeesh!' Try them now and watch your engagement go through the roof! 📈 #trending #viralcontent",
            "metadata": {
                "type": "social_media",
                "platform": "instagram",
                "content_goal": "product_promotion"
            }
        },
        {
            "text": "No cap - this new feature is actually insane! 🤯 Drop everything and check out how it works (tutorial in bio). Trust, it's gonna be your new favorite thing! Plus, it's totally free rn! 🙌",
            "metadata": {
                "type": "product_announcement",
                "platform": "tiktok",
                "content_goal": "feature_promotion"
            }
        },
        {
            "text": "Hey bestie! 👋 Ready to glow up your content game? Our AI-powered editor is the vibe you've been looking for. It's giving main character energy fr fr! ✨",
            "metadata": {
                "type": "welcome_message",
                "platform": "website",
                "content_goal": "user_engagement"
            }
        }
    ],
    "cxo": [
        {
            "text": "Transform your enterprise operations with our AI-driven solution, delivering 40% cost reduction and 2.5x ROI within the first quarter. Our enterprise-grade platform ensures seamless integration with your existing infrastructure while maintaining robust security protocols.",
            "metadata": {
                "type": "value_proposition",
                "industry": "enterprise_software",
                "content_goal": "lead_generation"
            }
        },
        {
            "text": "Strategic Decision Framework: Leverage real-time analytics and predictive modeling to optimize resource allocation and drive sustainable growth. Our solution provides comprehensive visibility into key performance indicators, enabling data-driven decision making at scale.",
            "metadata": {
                "type": "product_description",
                "industry": "business_intelligence",
                "content_goal": "product_education"
            }
        },
        {
            "text": "Dear Executive Team, I'm pleased to present our latest enterprise solution that addresses the critical challenges facing modern businesses. Our platform delivers measurable impact across key metrics: operational efficiency, resource optimization, and revenue growth.",
            "metadata": {
                "type": "executive_brief",
                "industry": "enterprise_solutions",
                "content_goal": "executive_engagement"
            }
        }
    ],
    "technical": [
        {
            "text": "Implementation Guide: The REST API supports both JSON and Protocol Buffers, with rate limiting at 1000 requests/second. Authentication uses JWT tokens with RSA-256 encryption. See code examples below for common integration patterns.",
            "metadata": {
                "type": "technical_documentation",
                "technology": "api",
                "content_goal": "implementation_guide"
            }
        },
        {
            "text": "The distributed cache layer implements a consistent hashing algorithm with a replication factor of 3, ensuring high availability and fault tolerance. Average read latency: 5ms, write latency: 10ms at p99.",
            "metadata": {
                "type": "system_architecture",
                "technology": "distributed_systems",
                "content_goal": "technical_specification"
            }
        },
        {
            "text": "Debug the performance bottleneck using our profiling tools: 1. Enable debug logging with LOG_LEVEL=DEBUG 2. Run performance traces with --trace-mode=detailed 3. Analyze heap dumps for memory leaks 4. Check thread contention patterns",
            "metadata": {
                "type": "troubleshooting_guide",
                "technology": "debugging",
                "content_goal": "problem_solving"
            }
        }
    ]
}

async def populate_vector_store():
    """Populate the vector store with example content."""
    from ..services.vector_store import vector_store
    
    for persona, contents in EXAMPLE_CONTENT.items():
        texts = [content["text"] for content in contents]
        metadata = [{"persona": persona, **content["metadata"]} for content in contents]
        vector_store.add_example_content(texts=texts, personas=[persona] * len(texts), metadata=metadata)
        print(f"Added {len(texts)} examples for persona: {persona}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(populate_vector_store()) 