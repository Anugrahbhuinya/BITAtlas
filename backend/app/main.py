from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes.chat import router
from app.routes.history import router as history_router
from app.routes.admin import router as admin_router
from app.services.admin_service import seed_admin_user

app = FastAPI(
    title="BIT Mesra AI Assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await seed_admin_user()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Check if there is a json_invalid error
    for error in errors:
        if error.get("type") == "json_invalid":
            return JSONResponse(
                status_code=400,
                content={
                    "type": "error",
                    "answer": f"JSON decode error: {error.get('msg', 'Invalid JSON payload')}"
                }
            )
    
    # Check if a required field is missing
    missing_fields = []
    for error in errors:
        if error.get("type") == "missing":
            loc = error.get("loc", [])
            field_name = loc[-1] if loc else "body"
            missing_fields.append(str(field_name))
            
    if missing_fields:
        return JSONResponse(
            status_code=400,
            content={
                "type": "error",
                "answer": f"Missing required field(s): {', '.join(missing_fields)}"
            }
        )

    # General validation error
    return JSONResponse(
        status_code=400,
        content={
            "type": "error",
            "answer": f"Validation Error: {errors[0].get('msg', 'Invalid request')}"
        }
    )

app.include_router(router)
app.include_router(history_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "message": "BIT Mesra AI Assistant API Running"
    }