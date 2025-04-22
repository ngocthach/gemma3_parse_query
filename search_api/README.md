## Boosting Search Accuracy with Gemma3

Use Gemma 3 to parse user queries and search Elasticsearch.

### Features
- Parse user queries.
- Search for relevant results in Elasticsearch.

### API Endpoints
- `POST /v1/search`: Receive entities to search restaurant in Elasticsearch.
- `POST /v1/llm-search`: Parse user queries to entities, then search restaurant in Elasticsearch.

### Deploy

#### Create .env
    Create file .env from env template (env)

#### Build  and Run
    docker compose up -d --build 

#### Check log
    docker logs -f search-api





