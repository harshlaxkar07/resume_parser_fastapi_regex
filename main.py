from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router


BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="Resume Parser API",
    description=(
        "A Resume Parser backend built with FastAPI, PyMuPDF, PyMySQL and "
        "MySQL. The parser console is served at /ui."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """
    Liveness probe for the API.
    """

    return {"status": "healthy"}


if FRONTEND_DIR.is_dir():

    app.mount(
        "/ui",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="ui",
    )

    @app.get("/", include_in_schema=False)
    def console() -> RedirectResponse:
        """
        Send the application root to the parser console.
        """

        return RedirectResponse(url="/ui/")

else:

    @app.get("/")
    def home() -> dict[str, str]:
        return {
            "message": "Resume Parser API is running.",
        }
