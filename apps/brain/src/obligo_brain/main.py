from fastapi import FastAPI

from obligo_brain.api.v1 import health

app = FastAPI(title="obligo-brain")

app.include_router(health.router)
