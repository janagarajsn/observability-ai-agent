# Expose generate-logs and ingest-logs as fast api
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from log_generator import generate_static_logs_for_day
from log_ingestor import ingest_static_files
from ticket_generator import generate_batch
from ticket_ingestor import ingest_tickets

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Observability AI Agent")

# Enable CORS since we are calling this API from a frontend application running separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-logs", description="Generate sample logs for a specific day", tags=["Logs"])
def generate_logs_api(input_date: str, num_logs: int):
    try:
        file_path = generate_static_logs_for_day(input_date, num_logs)
        return JSONResponse(status_code=200, content={"message": "Logs generated successfully", "file_path": file_path})
    except Exception as e:
        logger.error(f"Error generating logs: {e}")
        return JSONResponse(status_code=500, content={"message": "Error generating logs"})

@app.post("/ingest-logs", description="Ingest logs into a Qdrant collection", tags=["Logs"])
def ingest_logs_api(collection_name: str, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(ingest_static_files, collection_name)
        return JSONResponse(status_code=202, content={"message": "Ingestion started", "collection_name": collection_name})
    except Exception as e:
        logger.error(f"Error starting ingestion: {e}")
        return JSONResponse(status_code=500, content={"message": "Error starting ingestion"})
    
@app.post("/generate-incidents", description="Generate sample incidents for a specific day", tags=["Incidents"])
def generate_incidents(input_date: str, num_incidents: int):
    try:
        file_path = generate_batch(date_str=input_date, num=num_incidents)
        return JSONResponse(status_code=200, content={"message": "Incidents generated successfully", "file_path": file_path})
    except Exception as e:
        logger.error(f"Error generating incidents: {e}")
        return JSONResponse(status_code=500, content={"message": "Error generating incidents"})

@app.post("/ingest-incidents", description="Ingest incidents into a Qdrant collection", tags=["Incidents"])
def ingest_incidents_api(collection_name: str, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(ingest_incidents, collection_name)
        return JSONResponse(status_code=202, content={"message": "Ingestion started", "collection_name": collection_name})
    except Exception as e:
        logger.error(f"Error starting ingestion: {e}")
        return JSONResponse(status_code=500, content={"message": "Error starting ingestion"})
