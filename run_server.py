"""Server starter script for Prime Generator REST API"""
import uvicorn

if __name__ == "__main__":
    print("[*] Starting Prime Generator Engine REST API server on http://localhost:8000 ...")
    print("[*] Interactive Swagger API Documentation: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
