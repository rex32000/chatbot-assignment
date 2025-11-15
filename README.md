# chatbot-assignment
Chatboot assignment

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
    "user_message": "what details are required"
}'
```
