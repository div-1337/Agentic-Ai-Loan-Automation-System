from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
response = llm.invoke("Say hello as Aryan, a Tata Capital loan advisor, in 2 sentences.")
print(response.content)