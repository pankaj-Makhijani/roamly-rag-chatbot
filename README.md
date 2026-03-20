# Roamly - Serverless RAG Chatbot on AWS

A fully serverless RAG chatbot built on AWS using Amazon Bedrock Knowledge Bases, Lambda, and Nova Lite.

> This repository accompanies the Medium blog post: **[Build a Serverless RAG Chatbot on AWS with Bedrock Knowledge Bases](https://itzzpankaj004.medium.com/build-a-serverless-rag-chatbot-on-aws-with-bedrock-knowledge-bases-e633007a9b8b)** — refer to the blog for the complete step by step setup guide.

---

## Repository Structure

```
roamly-rag-chatbot/
├── lambda_function.py        # Lambda RAG orchestration logic
├── frontend/
│   └── index.html            # Chat UI (single file, no framework)
└── docs/
    ├── package_catalog.txt
    ├── visa_information.txt
    ├── booking_cancellation_policy.txt
    ├── customer_faq.txt
    └── about_roamly.txt
```

---

## Tech Stack

- Amazon Bedrock Knowledge Bases
- Amazon OpenSearch Serverless
- Titan Text Embeddings V2
- Amazon Nova Lite
- AWS Lambda (Python 3.13)
- Amazon API Gateway
- Amazon S3

---

## Quick Start

1. Upload files from `docs/` to your S3 knowledge base bucket
2. Create and sync a Bedrock Knowledge Base pointing to that bucket
3. Deploy `lambda_function.py` to AWS Lambda with the environment variables below
4. Create an API Gateway REST API and connect it to the Lambda function
5. Replace `YOUR_API_GATEWAY_URL` in `frontend/index.html` and host it on S3

---

## Lambda Environment Variables

| Key | Value |
|---|---|
| `AWS_REGION_NAME` | `us-east-1` |
| `KNOWLEDGE_BASE_ID` | Your Knowledge Base ID |
| `MODEL_ID` | `amazon.nova-lite-v1:0` |
| `MAX_TOKENS` | `512` |
| `TEMPERATURE` | `0.7` |
| `TOP_P` | `0.9` |
| `KB_RESULTS_COUNT` | `3` |
| `SYSTEM_PROMPT` | Your custom system prompt |

---

## Customizing for Your Own Use Case

Replace the documents in `docs/` with your own business documents, update the `SYSTEM_PROMPT` environment variable, and re-sync the Knowledge Base. The architecture stays exactly the same.
