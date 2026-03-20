import boto3
import json
import os

bedrock = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION_NAME"])
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=os.environ["AWS_REGION_NAME"])

def lambda_handler(event, context):
    # Detect HTTP method for both REST API v1 and HTTP API v2
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    # Handle CORS preflight
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": ""
        }

    # Parse request body safely
    raw_body = event.get("body", "{}")
    body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

    user_message = body.get("message", "").strip()
    history = body.get("history", [])

    if not user_message:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": "message is required"})
        }

    # Step 1: Retrieve relevant chunks from the Knowledge Base
    context_text = retrieve_context(user_message)

    # Step 2: Build the augmented prompt with context and history
    messages = build_messages(user_message, history, context_text)

    # Step 3: Invoke Nova Lite with the augmented prompt
    request_body = {
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": int(os.environ["MAX_TOKENS"]),
            "temperature": float(os.environ["TEMPERATURE"]),
            "topP": float(os.environ["TOP_P"])
        }
    }

    response = bedrock.invoke_model(
        modelId=os.environ["MODEL_ID"],
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    reply = (
        result.get("output", {})
              .get("message", {})
              .get("content", [{}])[0]
              .get("text", "")
    )

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({"response": reply})
    }

def retrieve_context(query):
    """
    Queries the Bedrock Knowledge Base and returns the top K
    most relevant chunks as a single string.
    Falls back to empty string if retrieval fails.
    """
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=os.environ["KNOWLEDGE_BASE_ID"],
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": int(os.environ["KB_RESULTS_COUNT"])
                }
            }
        )

        chunks = []
        for result in response.get("retrievalResults", []):
            text = result.get("content", {}).get("text", "")
            if text:
                chunks.append(text)

        print(f"Retrieved {len(chunks)} chunks for query: {query}")
        return "\n\n".join(chunks)

    except Exception as e:
        print(f"KB retrieval error: {type(e).__name__}: {e}")
        return ""

def build_messages(user_message, history, context_text):
    """
    Builds the messages array for Nova Lite.
    Nova Lite does not support the system role so we inject
    the system prompt as the first user turn instead.
    """
    system_prompt = os.environ["SYSTEM_PROMPT"]

    # Append retrieved context to the system prompt if available
    if context_text:
        system_prompt += f"\n\nContext:\n{context_text}"

    messages = [
        {
            "role": "user",
            "content": [{"text": system_prompt}]
        },
        {
            "role": "assistant",
            "content": [{"text": "Understood. I will answer based on the provided context."}]
        }
    ]

    # Append full conversation history
    # History is owned by the browser and sent with every request
    for turn in history:
        if "user" in turn and "assistant" in turn:
            messages.append({
                "role": "user",
                "content": [{"text": turn["user"]}]
            })
            messages.append({
                "role": "assistant",
                "content": [{"text": turn["assistant"]}]
            })

    # Append the current user message
    messages.append({
        "role": "user",
        "content": [{"text": user_message}]
    })

    return messages

def cors_headers():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }