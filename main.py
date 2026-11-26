from fastapi import FastAPI

from routers import pages, cultivations, records, farms, work_types, varieties

app = FastAPI()

app.include_router(pages.router)
app.include_router(cultivations.router)
app.include_router(records.router)
app.include_router(farms.router)
app.include_router(work_types.router)
app.include_router(varieties.router)
