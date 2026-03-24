from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import pages, queue, ws, search

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages.router)
app.include_router(queue.router)
app.include_router(ws.router)
app.include_router(search.router)
