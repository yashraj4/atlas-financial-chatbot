from langgraph.graph import StateGraph, END
from backend.app.agents.state import AgentState
from backend.app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from duckduckgo_search import DDGS
import os

# Mock LLM for robustness when API Key fails
class MockLLM:
    def invoke(self, prompt: str):
        prompt_lower = str(prompt).lower()
        content = "I can help with that."
        
        if "classify" in prompt_lower:
            if "loan" in prompt_lower or "rate" in prompt_lower or "eligibility" in prompt_lower:
                return type('obj', (object,), {'content': 'rag'})
            return type('obj', (object,), {'content': 'general'})
            
        if "eligibility" in prompt_lower and "premier" in prompt_lower:
            content = """**Premier Account Eligibility:**
- Gross annual income of £75,000+ paid into the account.
- OR a total of £100,000+ in savings/investments with Atlas.
- You must be a UK resident."""
        elif "mortgage" in prompt_lower:
             content = "We offer fixed-rate and tracker mortgages. The current 2-year fixed rate is approx 4.5% APR."
        elif "savings" in prompt_lower:
             content = "Our Blue Rewards Saver offers 5.12% AER on balances up to £5,000."
        else:
             content = "I am Atlas, your high-performance financial intelligence. I can optimize your loans, savings, and mortgage strategies. (System currently in Demo Mode)."
             
        return type('obj', (object,), {'content': content})

import requests
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# --- HYBRID INTELLIGENCE CORE ---

class HybridLLM:
    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        self.model_name = "Hybrid-v1"
        
        # Init Groq
        if settings.GROQ_API_KEY:
            # List of Groq models to try (Newest to Oldest)
            groq_candidates = [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768" 
            ]
            
            for model in groq_candidates:
                try:
                    client = ChatGroq(
                        temperature=0, 
                        model_name=model, 
                        groq_api_key=settings.GROQ_API_KEY
                    )
                    client.invoke("Hi") # Test it
                    self.groq_client = client
                    print(f"--- Groq Client Ready: {model} (Priority 1) ---")
                    break
                except Exception as e:
                    print(f"Groq {model} Init Failed: {e}")

        # Init Gemini
        if settings.GOOGLE_API_KEY:
            # List of Gemini models to try
            gemini_candidates = [
                "gemini-2.0-flash",
                "gemini-1.5-flash", 
                "gemini-1.5-pro",
                "gemini-1.0-pro",
                "gemini-pro"
            ]
            
            for model in gemini_candidates:
                try:
                    # Try to init and invoke
                    client = ChatGoogleGenerativeAI(
                        model=model,
                        google_api_key=settings.GOOGLE_API_KEY,
                        temperature=0,
                        convert_system_message_to_human=True
                    )
                    # We must test invoke because init implies lazy loading sometimes
                    client.invoke("Hi")
                    self.gemini_client = client
                    print(f"--- Gemini Client Ready: {model} (Priority 2) ---")
                    break
                except Exception as e:
                    print(f"Gemini {model} Failed: {e}")

    def invoke(self, prompt):
        errors = []
        
        # Try Groq First
        if self.groq_client:
            try:
                return self.groq_client.invoke(prompt)
            except Exception as e:
                err_msg = f"Groq Error: {e}"
                print(f"⚠️ {err_msg}. Switching to Gemini Fallback...")
                errors.append(err_msg)
        
        # Fallback to Gemini
        if self.gemini_client:
            try:
                return self.gemini_client.invoke(prompt)
            except Exception as e:
                err_msg = f"Gemini Error: {e}"
                print(f"⚠️ {err_msg}.")
                errors.append(err_msg)
                
        # If both fail
        error_str = " | ".join(errors)
        raise Exception(f"All AI systems offline. Errors: {error_str}")

# Initialize Global Hybrid Brain
try:
    llm = HybridLLM()
except Exception as e:
    print(f"CRITICAL BRAIN FAILURE: {e}")
    llm = None

def router_node(state: AgentState):
    query = state["query"]
    print(f"--- ROUTER: Analyzing '{query}' ---")
    
    if not llm:
        return {"intent": "general"} # Will fail gracefully in general node
    
    try:
        prompt = f"""Classify the user's banking query.
        Query: {query}
        
        Options:
        - rag (Questions about specific products, rates, eligibility, policies, or general banking facts)
        - general (Greetings, compliments, or questions unrelated to banking)
        
        Reply ONLY with 'rag' or 'general'."""
        
        response = llm.invoke(prompt)
        intent = response.content.strip().lower()
        if "rag" in intent: intent = "rag"
        else: intent = "general"
    except Exception as e:
        print(f"Router Error: {e}")
        intent = "general"
        
    return {"intent": intent}

def rag_node(state: AgentState):
    query = state["query"]
    print(f"--- RAG: Searching for '{query}' ---")
    
    context = ""
    source_label = "None"
    
    # LAYER 1: Tavily API (Best for Agents, requires Key)
    if not context and settings.TAVILY_API_KEY:
        try:
            print("--- Attempting Tavily Search... ---")
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = tavily.search(query=f"Banking {query}", search_depth="basic", max_results=3)
            context = "\n".join([f"- {r['content']} (Source: {r['url']})" for r in response['results']])
            source_label = "Tavily Search API (High Reliability)"
        except Exception as e:
            print(f"Tavily Failed: {e}")

    # LAYER 2: DuckDuckGo (Free, rate-limited)
    if not context:
        try:
            print("--- Attempting DuckDuckGo Search... ---")
            with DDGS() as ddgs:
                results = list(ddgs.text(f"Banking {query}", max_results=3))
                if results:
                    context = "\n".join([f"- {r['body']} (Source: {r['title']})" for r in results])
                    source_label = "DuckDuckGo (Web)"
        except Exception as e:
            print(f"DDG Failed: {e}")

    # LAYER 3: Wikipedia (Completely Free, No Key)
    if not context:
        try:
            print("--- Attempting Wikipedia Search... ---")
            import wikipedia
            # Search for relevant page
            search_results = wikipedia.search(query)
            if search_results:
                page = wikipedia.page(search_results[0])
                context = f"Summary: {page.summary[:1000]}..."
                source_label = f"Wikipedia: {page.title}"
        except Exception as e:
            print(f"Wikipedia Failed: {e}")

    if not context:
        context = "No information found in Live Search, DuckDuckGo, or Wikipedia."
        source_label = "All Sources Failed"

    try:
        if not llm:
            raise Exception("LLM not connected")

        # Generate Answer
        prompt = f"""You are **Atlas**, a high-performance financial intelligence unit designed for modern banking.
        
        **Directives:**
        1. **Precision First**: Answer based primarily on the 'Search Context' below.
        2. **Professional Grade**: Use a sleek, professional, and confident tone. Avoid fluff.
        3. **Structure**: Use **Bold** for key concepts and bullet points for lists.
        4. **Transparency**: If the context is empty, identify yourself as Atlas and provide general financial wisdom, but clearly state it is general knowledge.
        
        **Search Context:**
        {context}
        
        **User Command:** {query}
        """
        
        response = llm.invoke(prompt)
        
        # Clean Footer Transparency
        if "None" in source_label or "Failed" in source_label:
             footer = f"\n\n---\n⚡ **Analysis**: Atlas General Knowledge Core"
        else:
             footer = f"\n\n---\n📡 **Data Source**: {source_label}"
             
        content = response.content + footer
        
    except Exception as e:
        content = f"**System Error**: Processing logic interrupted. Details: {e}"
        
    return {"final_response": content}

def general_node(state: AgentState):
    print("--- GENERAL: Chatting ---")
    query = state["query"]
    
    if not llm:
        return {"final_response": "Atlas System Offline (API Key Missing). Check configuration."}

    prompt = f"""You are **Atlas**, a sophisticated and polite financial AI.
    
    User Input: "{query}"
    
    **Instructions:**
    - Respond with a sleek, professional, and helpful tone.
    - Briefly mention your capabilities: **Market Analysis**, **Loan Optimization**, **Savings Strategies**.
    - Keep it under 2 sentences.
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content
    except Exception as e:
        print(f"GENERAL NODE ERROR: {e}")
        content = f"**Connection Lost**: Neural link unstable. Error: {e}"

    return {"final_response": content}

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("rag", rag_node)
workflow.add_node("general", general_node)

workflow.set_entry_point("router")

def route_decision(state: AgentState):
    return state.get("intent", "general")

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag": "rag",
        "general": "general"
    }
)

workflow.add_edge("rag", END)
workflow.add_edge("general", END)

app = workflow.compile()
