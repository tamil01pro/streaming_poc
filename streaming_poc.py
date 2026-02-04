
import asyncio
import json
import sys
import argparse
from typing import Dict, Any, List, AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import uvicorn


# ============================================================================
# DATA MODELS
# ============================================================================

class QueryRequest(BaseModel):
    question: str


class PropertyChatRequest(BaseModel):
    property_details: Dict[str, Any]
    user_question: str
    chat_history: List[Dict[str, Any]] = []


# ============================================================================
# ML SERVICE - Simulates your ML API
# ============================================================================

class MLService:
    """
    ML Service - Simulates the actual ML API that processes queries
    This would be your ml-api service
    """
    
    @staticmethod
    def _determine_search_stages(query: str) -> List[str]:
        """
        Dynamically determine search stages based on query content
        In real implementation, this would analyze the query to determine processing steps
        """
        query_lower = query.lower()
        stages = []
        
        # Always start with parsing
        stages.append(f"Analyzing your search: '{query}'")
        
        # Determine stages based on query keywords
        if any(word in query_lower for word in ['near', 'close', 'distance', 'location']):
            stages.append("Identifying location requirements...")
            stages.append("Searching properties by location...")
            stages.append("Calculating distances to amenities...")
        
        if any(word in query_lower for word in ['price', 'cost', 'budget', 'affordable', 'cheap', 'expensive']):
            stages.append("Filtering by price range...")
            stages.append("Analyzing property values...")
        
        if any(word in query_lower for word in ['bedroom', 'bathroom', 'room', 'size', 'square']):
            stages.append("Matching property specifications...")
            stages.append("Filtering by size requirements...")
        
        if any(word in query_lower for word in ['school', 'education', 'university', 'college']):
            stages.append("Finding nearby schools...")
            stages.append("Gathering school ratings...")
        
        if any(word in query_lower for word in ['park', 'mall', 'shopping', 'restaurant', 'amenity']):
            stages.append("Searching nearby amenities...")
            stages.append("Enriching with landmark data...")
        
        # Default stages if no specific keywords found
        if len(stages) == 1:  # Only has the initial parsing stage
            stages.extend([
                "Searching property database...",
                "Filtering results by criteria...",
                "Ranking properties by relevance...",
                "Enriching with additional data..."
            ])
        
        return stages
    
    @staticmethod
    async def stream_search_progress(query: str) -> AsyncGenerator[str, None]:
        """
        Simulates search processing with progress updates
        In real implementation, this would call your actual search agents
        """
        print(f"[ML Service] Starting search for: {query}")
        
        # Dynamically determine stages based on query
        stages = MLService._determine_search_stages(query)
        
        # Stream each stage as SSE event character by character
        for i, message in enumerate(stages):
            # Stream message character by character
            accumulated_message = ""
            for char in message:
                accumulated_message += char
                # Send each character as it's typed
                data = json.dumps({
                    'type': 'progress_char',
                    'char': char,
                    'message': accumulated_message,
                    'is_complete': False,
                    'replace': True
                })
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.03)  # Small delay between characters for smooth typing effect
            
            # Send completion signal for this message
            data = json.dumps({
                'type': 'progress',
                'message': accumulated_message,
                'replace': True,
                'is_complete': True
            })
            yield f"data: {data}\n\n"
            
            print(f"[ML Service] Sent progress {i+1}/{len(stages)}: {message}")
            
            # Wait before starting next message (3 seconds total, minus time spent typing)
            typing_time = len(message) * 0.03
            wait_time = max(0, 3.0 - typing_time)
            await asyncio.sleep(wait_time)
        
        # Send final results with more properties
        results = {
            "type": "results",
            "properties": [
                {
                    "id": "1",
                    "address": "123 Main Street, San Francisco, CA 94102",
                    "price": 850000,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "square_feet": 1850,
                    "year_built": 2015,
                    "property_type": "Condo",
                    "schools": [
                        {"name": "Lincoln High School", "rating": 8.5, "distance": "0.3 miles", "grade": "9-12"},
                        {"name": "Roosevelt Elementary", "rating": 9.2, "distance": "0.5 miles", "grade": "K-5"},
                        {"name": "Washington Middle School", "rating": 8.8, "distance": "0.7 miles", "grade": "6-8"}
                    ]
                },
                {
                    "id": "2",
                    "address": "456 Oak Avenue, San Francisco, CA 94103",
                    "price": 1200000,
                    "bedrooms": 4,
                    "bathrooms": 3,
                    "square_feet": 2400,
                    "year_built": 2018,
                    "property_type": "Townhouse",
                    "schools": [
                        {"name": "Jefferson High School", "rating": 9.1, "distance": "0.4 miles", "grade": "9-12"},
                        {"name": "Madison Elementary", "rating": 9.5, "distance": "0.3 miles", "grade": "K-5"},
                        {"name": "Adams Middle School", "rating": 9.0, "distance": "0.6 miles", "grade": "6-8"},
                        {"name": "Stanford University", "rating": 9.8, "distance": "2.5 miles", "grade": "University"}
                    ]
                },
                {
                    "id": "3",
                    "address": "789 Pine Road, San Francisco, CA 94104",
                    "price": 650000,
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "square_feet": 1200,
                    "year_built": 2010,
                    "property_type": "Apartment",
                    "schools": [
                        {"name": "Hamilton High School", "rating": 8.2, "distance": "0.8 miles", "grade": "9-12"},
                        {"name": "Franklin Elementary", "rating": 8.7, "distance": "1.0 miles", "grade": "K-5"}
                    ]
                },
                {
                    "id": "4",
                    "address": "321 Elm Street, San Francisco, CA 94105",
                    "price": 950000,
                    "bedrooms": 3,
                    "bathrooms": 2.5,
                    "square_feet": 2100,
                    "year_built": 2019,
                    "property_type": "Single Family",
                    "schools": [
                        {"name": "Monroe High School", "rating": 9.3, "distance": "0.2 miles", "grade": "9-12"},
                        {"name": "Jackson Elementary", "rating": 9.4, "distance": "0.4 miles", "grade": "K-5"},
                        {"name": "Van Buren Middle School", "rating": 9.1, "distance": "0.5 miles", "grade": "6-8"},
                        {"name": "UC Berkeley Extension", "rating": 9.6, "distance": "3.0 miles", "grade": "University"}
                    ]
                },
                {
                    "id": "5",
                    "address": "654 Maple Drive, San Francisco, CA 94106",
                    "price": 750000,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "square_feet": 1500,
                    "year_built": 2016,
                    "property_type": "Condo",
                    "schools": [
                        {"name": "Harrison High School", "rating": 8.9, "distance": "0.6 miles", "grade": "9-12"},
                        {"name": "Tyler Elementary", "rating": 8.5, "distance": "0.7 miles", "grade": "K-5"}
                    ]
                },
                {
                    "id": "6",
                    "address": "987 Cedar Lane, San Francisco, CA 94107",
                    "price": 1100000,
                    "bedrooms": 5,
                    "bathrooms": 4,
                    "square_feet": 3200,
                    "year_built": 2020,
                    "property_type": "Single Family",
                    "schools": [
                        {"name": "Polk High School", "rating": 9.5, "distance": "0.3 miles", "grade": "9-12"},
                        {"name": "Taylor Elementary", "rating": 9.7, "distance": "0.2 miles", "grade": "K-5"},
                        {"name": "Fillmore Middle School", "rating": 9.4, "distance": "0.4 miles", "grade": "6-8"},
                        {"name": "San Francisco State University", "rating": 9.2, "distance": "4.2 miles", "grade": "University"}
                    ]
                }
            ],
            "landmarks": [
                {"name": "Golden Gate Park", "distance": "1.2 miles", "type": "Park"},
                {"name": "Union Square", "distance": "0.8 miles", "type": "Shopping"},
                {"name": "Fisherman's Wharf", "distance": "2.1 miles", "type": "Attraction"},
                {"name": "Chinatown", "distance": "1.5 miles", "type": "Neighborhood"}
            ]
        }
        print(f"[ML Service] Sending final results: {len(results['properties'])} properties")
        results_json = json.dumps(results)
        yield f"data: {results_json}\n\n"
        # Ensure final data is sent
        await asyncio.sleep(0.01)
    
    @staticmethod
    async def stream_chat_response(user_question: str, property_details: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Simulates ChatGPT-like streaming response
        In real implementation, this would call your LLM (like property_chat_service)
        """
        print(f"[ML Service] Generating chat response for: {user_question}")
        
        # Simulate LLM response generation (word by word)
        response_text = (
            f"Based on the property details you've shared, {user_question.lower()}. "
            "This property features excellent amenities and is located in a prime area. "
            "The neighborhood offers great schools, shopping centers, and easy access to public transportation. "
            "The property has been well-maintained and represents excellent value for the price. "
            "Would you like to know more about any specific aspect of this property?"
        )
        
        # Stream word by word (like ChatGPT)
        words = response_text.split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Small delay to simulate streaming
            chunk = {
                "type": "token",
                "content": word + " ",
                "index": i
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # Send completion signal
        print("[ML Service] Chat response complete")
        yield f"data: {json.dumps({'type': 'done', 'message': 'Response complete'})}\n\n"


# ============================================================================
# ML SERVICE API (FastAPI App)
# ============================================================================

ml_app = FastAPI(title="ML Service - Streaming")

ml_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@ml_app.post("/query/stream")
async def ml_query_stream(request: QueryRequest):
    """
    ML Service endpoint - Streams search progress
    This is what your ml-api/main.py /query endpoint would look like with streaming
    """
    print(f"[ML API] Received search request: {request.question}")
    return StreamingResponse(
        MLService.stream_search_progress(request.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@ml_app.post("/property_chat/stream")
async def ml_chat_stream(request: PropertyChatRequest):
    """
    ML Service endpoint - Streams chat response
    This is what your ml-api/main.py /property_chat endpoint would look like with streaming
    """
    print(f"[ML API] Received chat request: {request.user_question}")
    return StreamingResponse(
        MLService.stream_chat_response(request.user_question, request.property_details),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@ml_app.get("/health")
async def ml_health():
    return {"status": "healthy", "service": "ml-service"}


# ============================================================================
# BACKEND API - Proxies requests to ML Service
# ============================================================================

class BackendAPI:
    """
    Backend API - Proxies requests to ML Service and streams responses
    This is what your backend-api would do
    """
    
    ML_SERVICE_URL = "http://localhost:8001"
    
    @staticmethod
    async def proxy_search_stream(query: str) -> AsyncGenerator[str, None]:
        """
        Proxies search request to ML service and forwards SSE stream
        This is what your backend-api/app/api/routes/search.py would do
        """
        print(f"[Backend API] Proxying search request: {query}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"question": query}
            
            try:
                async with client.stream(
                    "POST",
                    f"{BackendAPI.ML_SERVICE_URL}/query/stream",
                    json=payload
                ) as response:
                    print(f"[Backend API] Connected to ML service, status: {response.status_code}")
                    
                    if response.status_code != 200:
                        error_msg = await response.aread()
                        error_text = error_msg.decode() if error_msg else "Unknown error"
                        print(f"[Backend API] ML service error: {response.status_code} - {error_text}")
                        yield f"data: {json.dumps({'error': f'ML service error: {response.status_code}', 'details': error_text})}\n\n"
                        return
                    
                    try:
                        async for line in response.aiter_lines():
                            if not line.strip():
                                continue  # Skip empty lines
                            
                            if line.startswith("data: "):
                                # Forward the SSE data as-is
                                print(f"[Backend API] Forwarding SSE data: {line[:50]}...")
                                yield f"{line}\n"
                            elif line.strip() and not line.startswith(":"):
                                # Handle any other non-comment lines
                                yield f"data: {json.dumps({'error': line})}\n\n"
                    except Exception as stream_error:
                        print(f"[Backend API] Stream error: {stream_error}")
                        yield f"data: {json.dumps({'error': f'Stream error: {str(stream_error)}'})}\n\n"
            
            except httpx.ConnectError as e:
                error_msg = f"Cannot connect to ML service at {BackendAPI.ML_SERVICE_URL}. Make sure ML service is running."
                print(f"[Backend API] Connection Error: {error_msg}")
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
            except Exception as e:
                print(f"[Backend API] Error: {e}")
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    @staticmethod
    async def proxy_chat_stream(
        property_details: Dict[str, Any],
        user_question: str,
        chat_history: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Proxies chat request to ML service and forwards SSE stream
        This is what your backend-api/app/services/chat_service.py would do
        """
        print(f"[Backend API] Proxying chat request: {user_question}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "property_details": property_details,
                "user_question": user_question,
                "chat_history": chat_history
            }
            
            try:
                async with client.stream(
                    "POST",
                    f"{BackendAPI.ML_SERVICE_URL}/property_chat/stream",
                    json=payload
                ) as response:
                    print(f"[Backend API] Connected to ML service, status: {response.status_code}")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            # Forward the SSE data as-is
                            print(f"[Backend API] Forwarding SSE data: {line[:50]}...")
                            yield f"{line}\n"
                        elif line.strip():
                            # Handle any other lines
                            yield f"data: {json.dumps({'error': line})}\n\n"
            except Exception as e:
                print(f"[Backend API] Error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"


# ============================================================================
# BACKEND API (FastAPI App)
# ============================================================================

backend_app = FastAPI(title="Backend API - Streaming Proxy")

backend_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@backend_app.get("/search/stream")
async def backend_search_stream(query: str):
    """
    Backend API endpoint - Streams search results with progress
    This is what your backend-api/app/api/routes/search.py /search endpoint would look like
    """
    print(f"[Backend API] Received search request: {query}")
    return StreamingResponse(
        BackendAPI.proxy_search_stream(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@backend_app.post("/chat/stream")
async def backend_chat_stream(request: PropertyChatRequest):
    """
    Backend API endpoint - Streams chat response
    This is what your backend-api/app/api/routes/chat.py would look like
    """
    print(f"[Backend API] Received chat request: {request.user_question}")
    return StreamingResponse(
        BackendAPI.proxy_chat_stream(
            request.property_details,
            request.user_question,
            request.chat_history
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@backend_app.get("/health")
async def backend_health():
    return {"status": "healthy", "service": "backend-api"}


# ============================================================================
# CLIENT - Terminal client to test streaming
# ============================================================================

class Client:
    """
    Terminal client to test SSE streaming
    This simulates what a frontend would do
    """
    
    BACKEND_URL = "http://localhost:8000"
    
    @staticmethod
    async def stream_search(query: str):
        """
        Test search streaming - shows progress updates
        """
        print(f"\n{'='*70}")
        print(f"🔍 SEARCH STREAMING TEST")
        print(f"{'='*70}")
        print(f"Query: '{query}'")
        print(f"{'-'*70}\n")
        
        current_message = ""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    async with client.stream(
                        "GET",
                        f"{Client.BACKEND_URL}/search/stream",
                        params={"query": query}
                    ) as response:
                        print(f"[Client] Connected to backend, status: {response.status_code}\n")
                        
                        if response.status_code != 200:
                            error_text = await response.aread()
                            print(f"❌ Error: Status {response.status_code}")
                            print(f"Response: {error_text.decode()}")
                            return
                        
                        line_count = 0
                        data_received = False
                        try:
                            async for line in response.aiter_lines():
                                line_count += 1
                                
                                if not line.strip():
                                    continue  # Skip empty lines
                                
                                if line.startswith("data: "):
                                    try:
                                        data = json.loads(line[6:])  # Remove "data: " prefix
                                        data_received = True
                                        
                                        # Handle progress updates - character by character streaming
                                        if data.get("type") == "progress_char":
                                            # Character-by-character streaming
                                            accumulated = data.get("message", "")
                                            
                                            # Check if this is the start of a new message
                                            # New message if: no current message, or accumulated doesn't start with current
                                            is_new_message = (not current_message or 
                                                            not accumulated.startswith(current_message))
                                            
                                            if is_new_message:
                                                # Clear previous message and start new one
                                                if current_message:
                                                    clear_length = max(len(current_message) + 2, 80)
                                                    print(f"\r{' ' * clear_length}", end="", flush=True)
                                            
                                            # Clear line and print accumulated message
                                            clear_length = max(len(accumulated) + 2, 80)
                                            print(f"\r{' ' * clear_length}", end="", flush=True)  # Clear
                                            print(f"\r🔄 {accumulated}", end="", flush=True)  # Print
                                            current_message = accumulated
                                        
                                        elif data.get("type") == "progress":
                                            # Complete progress message (final state)
                                            message = data.get("message", "")
                                            
                                            # Ensure complete message is displayed
                                            if current_message != message:
                                                clear_length = max(len(current_message) + 2, 80) if current_message else 80
                                                print(f"\r{' ' * clear_length}", end="", flush=True)
                                                print(f"\r🔄 {message}", end="", flush=True)
                                            current_message = message
                                        
                                        # Handle results
                                        elif data.get("type") == "results":
                                            # Clear the progress line completely
                                            if current_message:
                                                clear_length = max(len(current_message) + 2, 80)
                                                print(f"\r{' ' * clear_length}", end="", flush=True)
                                            # Move to new line for results
                                            print()  # New line after clearing progress
                                            
                                            print(f"\n{'='*70}")
                                            print("✅ SEARCH RESULTS:")
                                            print(f"{'='*70}")
                                            
                                            if "properties" in data:
                                                print("\n📋 Properties Found:")
                                                for prop in data["properties"]:
                                                    print(f"\n   • {prop.get('address', 'N/A')}")
                                                    print(f"     Price: ${prop.get('price', 'N/A'):,} | "
                                                          f"Bedrooms: {prop.get('bedrooms', 'N/A')} | "
                                                          f"Bathrooms: {prop.get('bathrooms', 'N/A')} | "
                                                          f"Size: {prop.get('square_feet', 'N/A')} sq ft")
                                                    print(f"     Type: {prop.get('property_type', 'N/A')} | "
                                                          f"Year Built: {prop.get('year_built', 'N/A')}")
                                                    
                                                    # Show schools data
                                                    if "schools" in prop and prop["schools"]:
                                                        print(f"     🎓 Nearby Schools:")
                                                        for school in prop["schools"]:
                                                            print(f"        - {school.get('name', 'N/A')} "
                                                                  f"(Rating: {school.get('rating', 'N/A')}/10, "
                                                                  f"Distance: {school.get('distance', 'N/A')}, "
                                                                  f"Grade: {school.get('grade', 'N/A')})")
                                            
                                            if "landmarks" in data:
                                                print("\n📍 Nearby Landmarks:")
                                                for landmark in data["landmarks"]:
                                                    print(f"   • {landmark.get('name', 'N/A')} "
                                                          f"({landmark.get('distance', 'N/A')}) - "
                                                          f"{landmark.get('type', 'N/A')}")
                                            print()
                                            break  # Exit loop after results
                                        
                                        # Handle errors
                                        elif "error" in data:
                                            # Clear progress line if showing
                                            if current_message:
                                                clear_length = max(len(current_message) + 2, 80)
                                                print(f"\r{' ' * clear_length}", end="", flush=True)
                                            print()  # New line
                                            print(f"\n❌ Error: {data.get('error')}")
                                            if "details" in data:
                                                print(f"Details: {data.get('details')}")
                                            return
                                            
                                    except json.JSONDecodeError as e:
                                        # Clear progress line if showing
                                        if current_message:
                                            clear_length = max(len(current_message) + 2, 80)
                                            print(f"\r{' ' * clear_length}", end="", flush=True)
                                        print()  # New line
                                        print(f"\n[Client] Error parsing JSON: {e}")
                                        print(f"Raw line: {line}")
                                elif line.strip() and not line.startswith(":"):
                                    # Handle non-data lines (comments, etc.) - don't print these
                                    pass  # Silently skip
                        
                        except httpx.ReadTimeout:
                            print(f"\n❌ Read timeout - stream closed unexpectedly (received {line_count} lines)")
                        except Exception as stream_error:
                            print(f"\n❌ Stream error: {stream_error} (received {line_count} lines)")
                            import traceback
                            traceback.print_exc()
                        
                        # If we got here without receiving data, show a message
                        if not data_received:
                            print(f"\n⚠️  No valid data received from stream (received {line_count} lines total).")
                            print("   Check if ML service is running and responding.")
                            print("   Make sure both ML Service (port 8001) and Backend API (port 8000) are running.")
                            print("   Check the service terminal windows for any error messages.")
                
                except httpx.ConnectError:
                    print(f"❌ Connection Error: Cannot connect to {Client.BACKEND_URL}")
                    print("   Make sure Backend API is running on port 8000")
                except httpx.TimeoutException:
                    print("❌ Timeout Error: Request took too long")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    async def stream_chat(property_details: dict, user_question: str):
        """
        Test chat streaming - shows ChatGPT-like response
        """
        print(f"\n{'='*70}")
        print(f"💬 CHAT STREAMING TEST")
        print(f"{'='*70}")
        print(f"Question: {user_question}")
        print(f"Property: {property_details.get('address', 'N/A')}")
        print(f"{'-'*70}\n")
        print("Response: ", end="", flush=True)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "property_details": property_details,
                "user_question": user_question,
                "chat_history": []
            }
            
            try:
                async with client.stream(
                    "POST",
                    f"{Client.BACKEND_URL}/chat/stream",
                    json=payload
                ) as response:
                    print(f"[Client] Connected to backend, status: {response.status_code}\n")
                    print("💬 ", end="", flush=True)
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])  # Remove "data: " prefix
                                
                                # Handle chat tokens
                                if data.get("type") == "token":
                                    content = data.get("content", "")
                                    print(content, end="", flush=True)
                                elif data.get("type") == "done":
                                    print("\n\n✅ [Chat response complete]")
                                    
                            except json.JSONDecodeError as e:
                                print(f"\n[Client] Error parsing JSON: {e}")
            except Exception as e:
                print(f"\n[Client] Error: {e}")


# ============================================================================
# MAIN - Entry point to run different services
# ============================================================================

def run_ml_service():
    """Run ML Service on port 8001"""
    print("="*70)
    print("Starting ML Service on http://localhost:8001")
    print("="*70)
    uvicorn.run(ml_app, host="0.0.0.0", port=8001)


def run_backend_api():
    """Run Backend API on port 8000"""
    print("="*70)
    print("Starting Backend API on http://localhost:8000")
    print("="*70)
    uvicorn.run(backend_app, host="0.0.0.0", port=8000)


async def run_test(test_type: str, query: str = None):
    """Run test client"""
    try:
        if test_type == "search":
            query = query or "homes near me"
            await Client.stream_search(query)
        elif test_type == "chat":
            question = query or "Tell me about this property"
            property_details = {
                "id": "123",
                "address": "123 Main Street, San Francisco, CA",
                "price": 500000,
                "bedrooms": 3,
                "bathrooms": 2,
                "square_feet": 1500,
                "year_built": 2015,
                "property_type": "Condo",
                "schools": [
                    {"name": "Lincoln High School", "rating": 8.5, "distance": "0.3 miles", "grade": "9-12"},
                    {"name": "Roosevelt Elementary", "rating": 9.2, "distance": "0.5 miles", "grade": "K-5"},
                    {"name": "Washington Middle School", "rating": 8.8, "distance": "0.7 miles", "grade": "6-8"},
                    {"name": "Stanford University", "rating": 9.8, "distance": "15 miles", "grade": "University"}
                ]
            }
            await Client.stream_chat(property_details, question)
        else:
            print(f"Unknown test type: {test_type}")
            print("Use 'search' or 'chat'")
            return
        
        # Keep terminal open for a moment to see results
        print("\n" + "="*70)
        print("Test completed. Press Ctrl+C to exit or wait 5 seconds...")
        print("="*70)
        await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SSE Streaming POC")
    parser.add_argument("--ml-service", action="store_true", help="Run ML Service")
    parser.add_argument("--backend", action="store_true", help="Run Backend API")
    parser.add_argument("--test", type=str, help="Run test: 'search' or 'chat'")
    parser.add_argument("--query", type=str, help="Query string for test")
    
    args = parser.parse_args()
    
    if args.ml_service:
        run_ml_service()
    elif args.backend:
        run_backend_api()
    elif args.test:
        asyncio.run(run_test(args.test, args.query))
    else:
        print("="*70)
        print("SSE Streaming POC - Usage:")
        print("="*70)
        print("1. Start ML Service:    python streaming_poc.py --ml-service")
        print("2. Start Backend API:    python streaming_poc.py --backend")
        print("3. Test Search:          python streaming_poc.py --test search --query 'homes near me'")
        print("4. Test Chat:            python streaming_poc.py --test chat --query 'Tell me about this property'")
        print("="*70)


if __name__ == "__main__":
    main()

