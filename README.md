# SSE Streaming POC - Complete Flow

This is a single-file demonstration of Server-Sent Events (SSE) streaming for both search and chat services.

## 📋 Overview

The file `streaming_poc.py` contains:
- **ML Service** - Simulates your ml-api service with streaming endpoints
- **Backend API** - Simulates your backend-api service that proxies to ML service
- **Client** - Terminal client to test the streaming functionality

## 🔄 Data Flow

```
Client → Backend API → ML Service → Backend API → Client
         (SSE Stream)   (SSE Stream)   (SSE Stream)   (SSE Stream)
```

1. **Client** sends request to Backend API
2. **Backend API** proxies request to ML Service
3. **ML Service** processes and streams SSE events (progress/response)
4. **Backend API** forwards SSE stream to Client
5. **Client** displays streaming data in terminal

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r streaming_poc_requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn httpx pydantic
```

## 🏃 Running the Services

### Terminal 1: Start ML Service (Port 8001)
```bash
cd "C:\Users\tamil\Desktop\propaity code"
python streaming_poc.py --ml-service
```

### Terminal 2: Start Backend API (Port 8000)
```bash
cd "C:\Users\tamil\Desktop\propaity code"
python streaming_poc.py --backend
```

### Terminal 3: Test Search Streaming
```bash
cd "C:\Users\tamil\Desktop\propaity code"
python streaming_poc.py --test search --query "homes near downtown"
```

### Terminal 3: Test Chat Streaming
```bash
cd "C:\Users\tamil\Desktop\propaity code"
python streaming_poc.py --test chat --query "What are the nearby schools?"
```

"""
SSE Streaming POC - Complete Flow in Single File
=================================================

This file demonstrates SSE (Server-Sent Events) streaming for:
1. Search Service - streams progress updates
2. Chat Service - streams ChatGPT-like responses

Data Flow:
----------
Client -> Backend API -> ML Service -> Backend API -> Client
         (SSE Stream)   (SSE Stream)   (SSE Stream)   (SSE Stream)

Run Instructions:
1. Start ML Service:    python streaming_poc.py --ml-service
2. Start Backend API:   python streaming_poc.py --backend (in new terminal)
3. Test Search:         python streaming_poc.py --test search "homes near me"
4. Test Chat:           python streaming_poc.py --test chat "Tell me about this property"
"""


## 📊 Features

### Search Streaming
- Shows real-time progress updates:
  - Parsing query (10%)
  - Searching properties (30%)
  - Filtering results (50%)
  - Ranking properties (70%)
  - Enriching with landmarks (90%)
  - Complete (100%)
- Displays final results with properties and landmarks

### Chat Streaming
- Streams response word-by-word (ChatGPT-like)
- Shows tokens as they arrive
- Displays completion message when done

## 🔍 Understanding the Code

### ML Service Section
- `MLService.stream_search_progress()` - Simulates search with progress
- `MLService.stream_chat_response()` - Simulates chat response streaming
- Maps to: `ml-api/app/main.py` endpoints

### Backend API Section
- `BackendAPI.proxy_search_stream()` - Proxies search to ML service
- `BackendAPI.proxy_chat_stream()` - Proxies chat to ML service
- Maps to: `backend-api/app/api/routes/search.py` and `chat.py`

### Client Section
- `Client.stream_search()` - Tests search streaming
- `Client.stream_chat()` - Tests chat streaming
- Simulates frontend behavior

## 🎯 Integration Points

When integrating into your actual codebase:

1. **ML Service** (`ml-api/app/main.py`):
   - Replace `MLService.stream_search_progress()` with your actual `process_question()` function
   - Replace `MLService.stream_chat_response()` with your actual `property_chat_service()` function
   - Use streaming LLM calls instead of `invoke()`

2. **Backend API** (`backend-api/app/api/routes/search.py`):
   - Replace `BackendAPI.proxy_search_stream()` with your actual `SearchService.search_properties()` but with streaming
   - Keep the same SSE format

3. **Backend API** (`backend-api/app/services/chat_service.py`):
   - Replace `BackendAPI.proxy_chat_stream()` with your actual `ChatService.get_property_chat_response()` but with streaming
   - Keep the same SSE format

## 📝 Notes

- All services run in a single file for easy understanding
- SSE format: `data: {json}\n\n`
- Progress updates are sent as separate SSE events
- Chat tokens are sent word-by-word for ChatGPT-like experience
- All logging shows the data flow through each service

## 🐛 Troubleshooting

- **Port already in use**: Make sure ports 8000 and 8001 are available
- **Connection refused**: Ensure ML service is running before starting Backend API
- **No output**: Check that both services are running and client is connecting to correct port (8000)

