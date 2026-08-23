
from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="Resume Parser API",
    description=(
        "A simple Resume Parser Backend built with "
        "FastAPI, PyMuPDF, PyMySQL, and MySQL."
    ),
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Resume Parser API is running.",
    }

