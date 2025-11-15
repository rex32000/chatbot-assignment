# chatbot-assignment
Chatboot assignment

- Uses gemini 2.0-flash for responding to users query
- FASSIS in memory vector embedding used for storing the knowledge base
- Added a simple gaurdrail to be an additional llm which just checks for the text if it is offensive or illegal
- Added fast API with 2 endpoints: chat, health


### Running the application

```
docker build -t chat .
docket run -p 8000:8000 chat
```

### Requests

Health check request
```
curl --location 'http://0.0.0.0:8000/health'
```

Chat requests
```
curl --location 'http://0.0.0.0:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "session_id": "newSession",
    "user_message": "Hello, i would like to book a table"
}'
```
