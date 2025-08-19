from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from src.conthabil import crud, schemas
from src.conthabil.database import get_db


# -- App Initialization --
app = FastAPI(
    title="Conthabil Test API",
    description="API for storing and retrieving gazette URLs.",
    version="1.0.0",
    root_path="/api"
)


# -- CORS Middleware --
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# -- API Router --
router = APIRouter()


# -- Route Declarations --
@router.post("/gazettes/", response_model=schemas.GazetteResponse, tags=["Gazettes"])
def create_gazette(gazette: schemas.GazetteCreate, db: Session = Depends(get_db)):
    """
    Create a new gazette entry.
    """

    return crud.create_gazette(db=db, gazette=gazette)


@router.get("/gazettes/", response_model=List[schemas.GazetteResponse], tags=["Gazettes"])
def read_gazettes(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Retrieve gazette entries.

    - If **month** and **year** are provided, it filters entries by publication date.
    - Otherwise, it returns a paginated list of all entries.

    - **skip**: Number of entries to skip (for pagination).
    - **limit**: Maximum number of entries to return (for pagination).
    """

    if month and year:
        return crud.get_gazettes_by_month_year(db, month=month, year=year)

    if (month and not year) or (not month and year):
        raise HTTPException(
            status_code=400, detail="Both month and year must be provided for filtering."
        )

    return crud.get_gazettes(db, skip=skip, limit=limit)


app.include_router(router)
