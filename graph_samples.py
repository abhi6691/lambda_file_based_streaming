import asyncio
from datetime import datetime
import time
from langgraph.graph import StateGraph, MessagesState, START, END

class GraphStreamingBase:
    def create_graph(self):
        """Creates and returns the graph. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement create_graph.")

    def stream_graph(self, app, inputs):
        # async for chunk in app.astream(inputs, stream_mode="values"):
        #     yield chunk
        response_chunks = []
        for chunk in app.stream(inputs, stream_mode=self.stream_mode):
        #     response_chunks.append(chunk)
        # return response_chunks
            time.sleep(inputs['sleep_time'])
            yield chunk

class ValuesModeGraph(GraphStreamingBase):
    stream_mode = "values"

    def create_graph(self):
        graph = StateGraph(MessagesState)

        def greeting_node(state: MessagesState):
            msg = state["messages"]
            return {"messages": f"Received message: {msg}"}

        def weather_info_node(state: MessagesState):
            return {"messages": "The weather in San Francisco is sunny."}

        graph.add_node("greeting", greeting_node)
        graph.add_node("weather_info", weather_info_node)
        graph.add_edge(START, "greeting")
        graph.add_edge("greeting", "weather_info")
        graph.add_edge("weather_info", END)

        return graph

class UpdatesModeGraph(GraphStreamingBase):
    stream_mode = "updates"

    def create_graph(self):
        graph = StateGraph(MessagesState)

        def location_node(state: MessagesState):
            return {"messages": "User is in San Francisco."}

        def greeting_node(state: MessagesState):
            return {"messages": "Hello! How can I assist you today?"}

        graph.add_node("location", location_node)
        graph.add_node("greeting", greeting_node)
        graph.add_edge(START, "location")
        graph.add_edge("location", "greeting")
        graph.add_edge("greeting", END)

        return graph

class MessagesModeGraph(GraphStreamingBase):
    stream_mode = "messages"

    def create_graph(self):
        graph = StateGraph(MessagesState)

        def question_node(state: MessagesState):
            return {"messages": "What is the capital of France?"}

        async def ai_response_node(state: MessagesState):
            tokens = ["The", "capital", "of", "France", "is", "Paris."]
            for token in tokens:
                await asyncio.sleep(0.5)  # Use asyncio.sleep for non-blocking delay
                yield {"messages": token}

        graph.add_node("question", question_node)
        graph.add_node("ai_response", ai_response_node)
        graph.add_edge(START, "question")
        graph.add_edge("question", "ai_response")
        graph.add_edge("ai_response", END)

        return graph


class EventsModeGraph(GraphStreamingBase):
    def create_graph(self):
        graph = StateGraph(MessagesState)

        def start_node(state: MessagesState):
            return {"messages": "Starting process."}

        def intermediate_node(state: MessagesState):
            return {"messages": "Process is halfway done."}

        def end_node(state: MessagesState):
            return {"messages": "Process completed successfully."}

        graph.add_node("start", start_node)
        graph.add_node("intermediate", intermediate_node)
        graph.add_node("end", end_node)
        graph.add_edge(START, "start")
        graph.add_edge("start", "intermediate")
        graph.add_edge("intermediate", "end")
        graph.add_edge("end", END)

        return graph

class DebugModeGraph(GraphStreamingBase):
    stream_mode = "debug"

    def create_graph(self):
        graph = StateGraph(MessagesState)

        def fetch_data_node(state: MessagesState):
            return {"messages": "Fetched data from the database."}

        def process_data_node(state: MessagesState):
            return {"messages": "Processed the data successfully."}

        def finalize_node(state: MessagesState):
            return {"messages": "Data processing complete and saved results."}

        graph.add_node("fetch_data", fetch_data_node)
        graph.add_node("process_data", process_data_node)
        graph.add_node("finalize", finalize_node)
        graph.add_edge(START, "fetch_data")
        graph.add_edge("fetch_data", "process_data")
        graph.add_edge("process_data", "finalize")
        graph.add_edge("finalize", END)

        return graph


def print_with_sleep(message):
    print(message)
    time.sleep(0.5)