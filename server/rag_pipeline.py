from server.utils.vector_store import retriever
from server.utils.persona import wrap_with_persona

def run_rag(query: str, history: list):
    # Retrieve relevant chunks
    docs = retriever.get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in docs])
    
    # Wrap prompt in persona style
    prompt = wrap_with_persona(query, context, history)
    
    # Call LLM (OpenAI/local)
    from langchain.llms import OpenAI
    llm = OpenAI(temperature=0.7)
    answer = llm(prompt)
    
    return answer, [doc.metadata.get("source") for doc in docs]
