from langchain.chat_models import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.agents import AgentType

# Fonction pour générer la réponse avec LLaMA 2 (via Ollama)
def generate_answer_with_llama(result, external_info, question):
    # Combiner les résultats internes et externes
    context = f"Résultats internes : {result}\nRésultats externes : {external_info}"
    
    # Utiliser LangChain pour générer une réponse
    prompt = PromptTemplate(input_variables=["context", "question"], template="{context}\nQuestion: {question}\nRéponse:")
    llm = LLMChain(prompt=prompt)
    
    answer = llm.run({"context": context, "question": question})
    return answer
