from fastapi import FastAPI

from obligo_brain.api.v1 import health
from obligo_brain.platform.otel import setup_otel

app = FastAPI(title="obligo-brain")

setup_otel(app)

app.include_router(health.router)
