# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
from collections.abc import AsyncIterator
from typing import Any

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

load_dotenv()
setup_telemetry()
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "simple-agent"
app.description = "API for interacting with the Agent simple-agent"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Spring Boot Proxy Compatible API Endpoints
from pydantic import BaseModel


class SpringBootChatRequest(BaseModel):
    userId: str | None = "user"
    sessionId: str | None = None
    message: str


class SpringBootChatResponse(BaseModel):
    sessionId: str
    reply: str
    status: str
    metadata: dict[str, Any] | None = None


@app.get("/api/v1/health")
def springboot_proxy_health() -> dict[str, str]:
    import datetime

    return {
        "status": "UP",
        "service": "Spring Boot ADK Agent Proxy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.post("/api/v1/chat")
async def springboot_proxy_chat(
    req: SpringBootChatRequest,
) -> SpringBootChatResponse:
    if not req.message or not req.message.strip():
        return SpringBootChatResponse(
            sessionId=req.sessionId or "",
            reply="Message cannot be empty.",
            status="BAD_REQUEST",
        )

    runner: Runner = app.state.runner
    user_id = req.userId or "user"

    if not req.sessionId:
        session = await runner.session_service.create_session(
            app_name=app.state.agent_app_name, user_id=user_id
        )
        session_id = session.id
    else:
        session_id = req.sessionId

    from google.genai.types import Content, Part

    user_content = Content(role="user", parts=[Part.from_text(text=req.message)])

    response_text = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=user_content
    ):
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    return SpringBootChatResponse(
        sessionId=session_id,
        reply=response_text or "No response from agent.",
        status="SUCCESS",
    )


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

