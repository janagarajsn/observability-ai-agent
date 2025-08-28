import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import PrivateAttr
from langchain.schema import BaseRetriever, Document, AgentAction, AgentFinish
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import Tool, initialize_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# ----------------- Load environment -----------------
load_dotenv()

# ----------------- Logging -----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)

# ----------------- Config -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENT_MODEL = os.getenv("RETRIEVER_MODEL", "gpt-4.1-mini")
QDRANT_URL = os.getenv("QDRANT_URL", "http://host.docker.internal:6333")
QDRANT_CLOUD_API_KEY = os.getenv("QDRANT_CLOUD_API_KEY")
COLLECTION_LOGS = os.getenv("COLLECTION_NAME", "aks_logs")
COLLECTION_TICKETS = os.getenv("COLLECTION_INCIDENTS", "tickets")  # renamed for clarity
DEFAULT_K = int(os.getenv("DEFAULT_K", 5))
THRESHOLD_LIMIT = float(os.getenv("THRESHOLD_LIMIT", 0.5))

# ----------------- Qdrant + Vector Stores -----------------
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_CLOUD_API_KEY)
text_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

log_vector_store = QdrantVectorStore(client=qdrant_client, collection_name=COLLECTION_LOGS, embedding=text_embeddings)
ticket_store = QdrantVectorStore(client=qdrant_client, collection_name=COLLECTION_TICKETS, embedding=text_embeddings) if COLLECTION_TICKETS else None

# ----------------- LLM -----------------
llm = ChatOpenAI(model=AGENT_MODEL, api_key=OPENAI_API_KEY, temperature=0)

# ----------------- Callbacks -----------------
class AgentTraceHandler(BaseCallbackHandler):
    def on_agent_action(self, action: AgentAction, **kwargs):
        logger.info(f"[TRACE] Agent called tool: {action.tool}")
        logger.info(f"[TRACE] Tool input: {action.tool_input}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        final_output = finish.return_values.get("output", "")
        logger.info(f"[TRACE] Agent finished with output: {final_output}")

# ----------------- Threshold Retriever -----------------
class ThresholdRetriever(BaseRetriever):
    """Retriever wrapper with threshold filtering."""
    _vectorstore: QdrantVectorStore = PrivateAttr()
    _k: int = PrivateAttr()
    _threshold: float = PrivateAttr()
    
    def __init__(self, vectorstore: QdrantVectorStore, k: int = DEFAULT_K, threshold: float = THRESHOLD_LIMIT):
        super().__init__()
        self._vectorstore = vectorstore
        self._k = k
        self._threshold = threshold

    def _get_relevant_documents(self, query: str) -> List[Document]:
        docs_and_scores = self._vectorstore.similarity_search_with_score(query, k=self._k)
        filtered_docs = []
        for d, s in docs_and_scores:
            if s >= self._threshold:
                d.metadata = dict(d.metadata or {})
                d.metadata["similarity_score"] = s
                filtered_docs.append(d)
        if not filtered_docs:
            logger.info(f"No documents passed threshold {self._threshold}")
        return filtered_docs

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)

# ----------------- Tools -----------------
def search_logs(query: str) -> List[Document]:
    retriever = ThresholdRetriever(log_vector_store)
    return retriever.get_relevant_documents(query)

def search_tickets(query: str) -> List[Document]:
    if not ticket_store:
        return []
    retriever = ThresholdRetriever(ticket_store)
    return retriever.get_relevant_documents(query)

def summarize_logs_and_tickets(log_docs: List[Document], ticket_docs: Optional[List[Document]] = None) -> str:
    """Summarize logs and optionally show related system tickets."""
    if not log_docs and not ticket_docs:
        return "No logs or system tickets found for your query."

    log_text = "\n".join([d.page_content for d in log_docs]) if log_docs else ""
    summary_prompt = f"Summarize the following logs into a concise human-readable summary of key issues:\n{log_text}"
    summary = llm.invoke(summary_prompt).content.strip() if log_text else "No logs found."

    output = [summary]

    if ticket_docs:
        output.append("\nRelated System Tickets:")
        for doc in ticket_docs:
            ticket_id = doc.metadata.get("ticketId", "")
            message = doc.page_content.strip()
            output.append(f"{ticket_id} → {message}" if ticket_id else message)

    return "\n".join(output)

# ----------------- Agent -----------------
tools = [
    Tool(name="SearchLogs", func=search_logs, description="Search logs based on user query"),
    Tool(name="SearchTickets", func=search_tickets, description="Search related system tickets"),
    Tool(name="SummarizeLogs", func=lambda text: summarize_logs_and_tickets([], []), description="Summarize logs"),
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    callbacks=[AgentTraceHandler()]
)

def agentic_query(user_query: str) -> str:
    """Run the user query through the agent."""
    logger.info(f"Agentic query: {user_query}")
    return agent.run(user_query)

# ----------------- CLI -----------------
if __name__ == "__main__":
    print("Observability AI CLI. Type 'exit' to quit.")
    while True:
        query = input("Enter your query: ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        try:
            # Always use agentic flow
            output = agentic_query(query)
            print("\n=== Result ===\n")
            print(output)
            print("\n================\n")
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"Error: {e}")
