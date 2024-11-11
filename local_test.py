import boto3
import json

def invoke_lambda_with_streaming(function_name, payload):
    # Initialize the boto3 client for Lambda
    client = boto3.client("lambda")

    # Invoke Lambda with the "InvokeWithResponseStream" API
    response = client.invoke_with_response_stream(
        FunctionName=function_name,
        Payload=json.dumps(payload)
    )

    # print(f"Recieved response: {response}")

    # Process the streamed response as it arrives
    for event in response['EventStream']:
        # print(f"Recieved event: {event}")
        # Each event has a payload (data chunk) containing a part of the response
        if 'PayloadChunk' in event:
            # Decode the chunk and print it
            print(event['PayloadChunk']['Payload'].decode('utf-8'), end='')

# Example usage
invoke_lambda_with_streaming(
    function_name="arn:aws:lambda:us-west-2:061994666073:function:LangGraphLambdaFunction",
    payload={"idx": 1, "sleep_time": 1.5}, 
)
