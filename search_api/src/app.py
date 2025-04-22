import asyncio
import logging
import time
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Depends
from service import create_searcher
from sample_data import SAMPLE_RESTAURANTS
from parser import query_parser


app = FastAPI(
    title="Search restaurant API",
    description="This API allows search restaurant.",
    version="1.0.0",
    contact={
        "name": "Thach Le",
        "email": "thach.le.tech@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

logger = logging.getLogger("search_api")
logging.basicConfig(level=logging.INFO)

# Global search client 
searcher = None

@app.on_event("startup")
async def startup_event():
    global searcher
    searcher = await create_searcher()
    
@app.on_event("shutdown")
async def shutdown_event():
    if searcher and hasattr(searcher, "elastic_search_client"):
        await searcher.elastic_search_client.close()


@app.get("/v1/test")
async def root():
    return {"message": "Hello World"}


@app.post("/v1/search")
async def search(entities: Dict):
    t0 = time.time()
    logger.info("Searching with entities: {}".format(entities))
    try:
        if not searcher:
            raise HTTPException(status_code=503, detail="Search service not initialized")
            
        response = await searcher.search(entities=entities, top_k=5)
        return {
            "runtime": int((time.time() - t0) * 1000),
            "data": response,
        }
    except Exception as e:
        logger.error(f"Error querying Elasticsearch: {e}")
        raise HTTPException(status_code=500, detail=f"Error querying Elasticsearch: {str(e)}")


@app.post("/v1/llm-search")
async def llm_search(data: Dict):
    query = data['query']
    entities = await query_parser.parse_user_query(query)
    return await search(entities=entities)


@app.post("/v1/index")
async def index_sample_data():
    """Index sample restaurant data into Elasticsearch"""
    t0 = time.time()
    try:
        if not searcher:
            raise HTTPException(status_code=503, detail="Search service not initialized")
            
        # Index the sample restaurant data
        result = await searcher.elastic_search_client.index_documents(
            documents=SAMPLE_RESTAURANTS
        )
        
        return {
            "runtime": int((time.time() - t0) * 1000),
            "message": "Sample data indexed successfully",
            "stats": result
        }
    except Exception as e:
        logger.error(f"Error indexing sample data: {e}")
        raise HTTPException(status_code=500, detail=f"Error indexing sample data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", reload=True, port=8085)
