import asyncio
from datetime import datetime
import json
import time
from graph_samples import DebugModeGraph, EventsModeGraph, MessagesModeGraph, UpdatesModeGraph, ValuesModeGraph
from langgraph.graph import END, StateGraph, START, MessagesState
from langchain_core.messages import HumanMessage

from aws_lambda_powertools import Logger

logger = Logger(service="langgraph-streaming")

def serialize_message(message):
    """Convert objects like HumanMessage to a JSON-serializable format."""
    if isinstance(message, HumanMessage):
        # Convert HumanMessage to a dictionary or string representation
        return {"type": "HumanMessage", "content": message.content}
    elif isinstance(message, dict):
        # Recursively serialize dictionary values
        return {k: serialize_message(v) for k, v in message.items()}
    elif isinstance(message, list):
        # Recursively serialize list items
        return [serialize_message(item) for item in message]
    else:
        # Return other types as they are
        return message

def handler(event, context, file_path):
    # Use asyncio.run to handle the asynchronous streaming in Lambda
    graph_type_values = ["values", "updates", "messages", "events", "debug"]
    idx = event.get("idx", 0)
    sleep_time = event.get("sleep_time", 1)
    # response_chunks = asyncio.run(invoke_graph(event={"graph_type": graph_type_values[idx]}, context={}))
    graph_type = graph_type_values[idx]
    if graph_type == "values":
        graph_class = ValuesModeGraph()
    elif graph_type == "updates":
        graph_class = UpdatesModeGraph()
    elif graph_type == "messages":
        graph_class = MessagesModeGraph()
    elif graph_type == "events":
        graph_class = EventsModeGraph()
    elif graph_type == "debug":
        graph_class = DebugModeGraph()
    
    graph = graph_class.create_graph()
    app = graph.compile()
    sleep_time = event.get("sleep_time", 1)
    inputs = {"messages": [("human", "what's the weather in sf")], "sleep_time": sleep_time}
    
    # return graph_class.stream_graph(app, inputs)
    # Print each chunk after asyncio.run completes
    with open(file_path, "w") as file:
        for chunk in graph_class.stream_graph(app, inputs):
            serialized_chunk = serialize_message(chunk)
            resp = json.dumps({"output": serialized_chunk}) + "\n"
            file.write(resp)
            file.flush() 

        file.write("END_OF_CONTENT\n")
        file.flush()


# def handler(file_path):
#     """Simulates writing content to a file line-by-line."""
#     with open(file_path, "w") as file:
#         for i in range(1, 6):  # Simulate content generation
#             content = f"Generated content line {i}\n"
#             file.write(content)
#             file.flush()  # Ensure each line is written immediately
#             time.sleep(1)  # Simulate processing time for each line

#         # Write the end-of-content marker
#         file.write("END_OF_CONTENT\n")
#         file.flush()
#     print("Handler finished writing content.")

def create_graph():
    # logger.info("Creating graph!!!")
    graph = StateGraph(MessagesState)

    def greeting_node(state: MessagesState):
        msg = state["messages"]
        return {"messages": f"Received message: {msg}"}
    
    def current_time_node(state: MessagesState):
        # Get the current time in the user's timezone
        user_time = datetime.now()
        time.sleep(5)
        # Determine the greeting based on the hour
        hour = user_time.hour
        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # Format the current time as a string
        current_time = user_time.strftime("%I:%M %p")
        message = f"{greeting}! The current time is {current_time})."
        return {"messages": message} 
    
    graph.add_node("greeting", greeting_node)
    graph.add_node("current_time", current_time_node)

    graph.add_edge(START, "greeting")   
    graph.add_edge("greeting", "current_time")
    graph.add_edge("current_time", END)
    
    return graph

def invoke_lambda():
    # Create sample event and context for testing
    test_event = {"messages": "Hello", "stream_mode": "messages"}
    test_context = {}
    
    # Call handler function and print responses
    for response in handler(test_event, test_context):
        print(response)

def invoke_graph(event, context):
    graph_type = event.get("graph_type", "values")
    if graph_type == "values":
        graph_class = ValuesModeGraph()
    elif graph_type == "updates":
        graph_class = UpdatesModeGraph()
    elif graph_type == "messages":
        graph_class = MessagesModeGraph()
    elif graph_type == "events":
        graph_class = EventsModeGraph()
    elif graph_type == "debug":
        graph_class = DebugModeGraph()
    
    graph = graph_class.create_graph()
    app = graph.compile()
    sleep_time = event.get("sleep_time", 1)
    inputs = {"messages": [("human", "what's the weather in sf")], "sleep_time": sleep_time}
    
    return graph_class.stream_graph(app, inputs)

if __name__ == "__main__":
    handler(event={"idx": 0, "sleep_time": "1"}, context={})
