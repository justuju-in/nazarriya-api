# nazarriya-backend
NazarRiya web server


## Developer instructions
0. Setup
Clone repo: `git clone git@github.com:paulrahul/nazarriya-backend.git`
Install dependencies: `pip install -r requiremements.txt`

1. Run server
```
cd server
fastapi dev main.py
```

2. CURL call to server
```
curl -X POST "http://localhost:8000/chat"   -H "Content-Type: application/json"   -d '{
    "user_id": "user123",
    "message": "What does mutual consent mean?",
    "session_id": "b4f17d5a-9fcb-4f30-98f7-81a83f2b4c78"
}'
```
