from fastapi import FastAPI
from APP.ROUTERS import auth, register, employee, rh, ml, psychologist
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(ml.router)
app.include_router(register.router)
app.include_router(employee.router)
app.include_router(rh.router)
app.include_router(psychologist.router)
