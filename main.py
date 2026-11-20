from fastapi import FastAPI

from routers import pages, vegetables, records, farms, work_types

app = FastAPI()

app.include_router(pages.router)
app.include_router(vegetables.router)
app.include_router(records.router)
app.include_router(farms.router)
app.include_router(work_types.router)
