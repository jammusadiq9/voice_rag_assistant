import os
import sys

# Project root directory ko Python module search path me add karna
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from config.settings import settings
from src.core.rag_engine import RAGEngine

app = FastAPI(title="Voice RAG Assistant API")
rag_engine = RAGEngine()

@app.get("/voice", response_class=HTMLResponse)
async def voice_interface():
    """Standalone voice client to avoid Streamlit iframe WebRTC blocks"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎙️ Live Voice Assistant</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: #0f172a;
                color: #f8fafc;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: #1e293b;
                padding: 40px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
            }}
            h1 {{ font-size: 24px; margin-bottom: 8px; }}
            p {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; }}
            .call-btn {{
                background-color: #2563eb;
                color: white;
                font-size: 18px;
                font-weight: 600;
                padding: 16px 32px;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.2s ease;
                width: 100%;
            }}
            .call-btn:hover {{ background-color: #1d4ed8; }}
            .call-btn.active {{ background-color: #dc2626; }}
            #status {{
                margin-top: 18px;
                font-size: 14px;
                color: #38bdf8;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎙️ Voice RAG Assistant</h1>
            <p>Speak naturally to query your uploaded knowledge base documents in real-time.</p>
            <button id="callBtn" class="call-btn">Start Voice Call</button>
            <div id="status">Status: Ready to connect</div>
        </div>

        <script type="module">
            import Vapi from "https://esm.sh/@vapi-ai/web@latest";

            const vapi = new Vapi("{settings.VAPI_PUBLIC_KEY}");
            const btn = document.getElementById("callBtn");
            const status = document.getElementById("status");
            let isConnected = false;

            btn.addEventListener("click", async () => {{
                if (!isConnected) {{
                    status.innerText = "Status: Connecting to assistant...";
                    btn.disabled = true;
                    try {{
                        await vapi.start("{settings.VAPI_ASSISTANT_ID}");
                    }} catch (err) {{
                        console.error("Vapi Error:", err);
                        status.innerText = "Status: Error - " + (err.message || "Failed");
                        btn.disabled = false;
                    }}
                }} else {{
                    status.innerText = "Status: Disconnecting...";
                    vapi.stop();
                }}
            }});

            vapi.on("call-start", () => {{
                isConnected = true;
                btn.disabled = false;
                btn.innerText = "End Voice Call";
                btn.classList.add("active");
                status.innerText = "Status: Connected (Listening & Speaking...)";
            }});

            vapi.on("call-end", () => {{
                isConnected = false;
                btn.disabled = false;
                btn.innerText = "Start Voice Call";
                btn.classList.remove("active");
                status.innerText = "Status: Call ended";
            }});

            vapi.on("error", (e) => {{
                console.error("Vapi Event Error:", e);
                status.innerText = "Status: Connection error occurred";
                btn.disabled = false;
            }});
        </script>
    </body>
    </html>
    """

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    payload = await request.json()
    message = payload.get("message", {})
    
    if message.get("type") == "tool-calls":
        tool_call = message.get("toolCalls", [{}])[0]
        func = tool_call.get("function", {})
        
        if func.get("name") == "query_knowledge_base":
            import json
            args = json.loads(func.get("arguments", "{}"))
            user_question = args.get("query", "")
            
            result = rag_engine.query(user_question)
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.get("id"),
                        "result": result
                    }
                ]
            }
            
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.api:app", host="0.0.0.0", port=8000, reload=True)