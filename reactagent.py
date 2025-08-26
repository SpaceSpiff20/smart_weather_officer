from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from datetime import datetime

from rag import create_pdf_vector_store
from tools import get_weather,get_forecast, get_time_and_date
from prompt import react_prompt

#initialize vector db
vector_store = create_pdf_vector_store()

#llm and memory
llm = ChatOllama(model='mistral', temperature=0.5)
memory = ConversationBufferWindowMemory(k=4, memory_key="chat_history", return_messages=True)

# weather tool
@tool
def get_current_weather(city: str)-> str:
    '''tool takes string city name as input and returns associated current weather details 
    like city name, temperature, feels like, pressure,conditions, visibility, humidity, wind'''
    data = get_weather(city)['readable']
    return data
#get_current_weather_tool= StructuredTool.from_function(get_current_weather)

@tool
def get_forecast_weather(city: str)-> str:
    '''tool takes string city name as input and returns associated weather forecast details 
    like datetime, temperature, description, wind, humidity in form of string'''
    data = get_forecast(city)['string']
    return data
#get_forecast_weather_tool = StructuredTool.from_function(get_forecast_weather)

@tool
def get_current_date_time(city: str) -> str:
    """tool takes city name as input and returns the current date and timeas output. you can add numbers with date to get date like tomorrow(add 1), day after tomorrow(add 2)"""
    return get_time_and_date(city)

#pdf retrieval tool
@tool
def search_weather_knowledge(query: str)-> str:
    '''tool takes user query and returns relevant weather related knowledge'''
    if vector_store is None:
        return "No weather knowledge data available."
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = vector_store  # Use pre-loaded vector store
        docs = db.similarity_search(query, k=3)
        result = "\n".join([doc.page_content for doc in docs])
        return result if result else "No relevant weather knowledge found."
    except Exception as e:
        return f"Error searching weather knowledge: {str(e)}"

#tool list
#tools = [get_current_weather_tool, get_forecast_weather_tool]
tools = [get_current_weather, get_forecast_weather, get_current_date_time, search_weather_knowledge]

prompt = PromptTemplate.from_template(react_prompt)

agent = create_react_agent(llm, tools, prompt)
reactagent = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    handle_parsing_errors=True,
    verbose=True,  # Optional: shows the agent's thought process
    max_iterations=5
)
