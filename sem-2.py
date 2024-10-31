from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="KinoSearch"
)

movies = [
    {"id": 1, "title": "God father", "year": 1972, "director": "F.F.Coppola", "length": "02:55:00", "rating": 9},
    {"id": 2, "title": "Parasite", "year": 2019, "director": "B.J.Ho", "length": "02:12:00", "rating": 9},
    {"id": 3, "title": "Seven", "year": 1995, "director": "D.Fincher", "length": "02:07:00", "rating": 9},
    {"id": 4, "title": "Green Mile", "year": 1999, "director": "F.Darabont", "length": "03:09:00", "rating": 8},
]


class Movie(BaseModel):
    id: int
    title: str = Field(max_length=99)
    year: int = Field(ge=1900, le=datetime.now().year)
    director: str = Field(max_length=99)
    length: str
    rating: int = Field(ge=0, le=10)

    @field_validator("length")
    def validate_length(cls, v):
        try:
            datetime.strptime(v, "%H:%M:%S")
            return v
        except ValueError:
            raise ValueError("Field 'length' should be in format 'HH:MM:SS'")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    field = error["loc"][-1]
    reason = error["msg"]
    return JSONResponse(
        status_code=400,
        content={"status": 400, "reason": f"Field '{field}' {reason}"}
    )


@app.get("/api/movies", response_model=dict)
def get_all_movies():
    return {"status": 200, "data": movies}


@app.get("/api/movies/:id", response_model=dict)
def get_movie(movie_id: int):
    data = [movie for movie in movies if movie.get("id") == movie_id]
    if len(data):
        return {"status": 200, "movie": data}
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@app.post("/api/movies", response_model=dict)
def add_movie(new_movie: Movie):
    movies_with_same_id = [movie for movie in movies if movie.get("id") == new_movie.id]
    if not len(movies_with_same_id):
        try:
            movies.append(new_movie.dict())
            return {"status": 200, "movie": new_movie}
        except Exception as e:
            return {"status": 500, "reason": str(e)}
    else:
        return {"status": 500, "reason": "Movie with this ID already exists"}


@app.patch("/api/movies/:id", response_model=dict)
def edit_movie(movie_id: int, edited_movie: Movie):
    current_movie = [movie for movie in movies if movie.get("id") == movie_id][0]
    if current_movie:
        if movie_id != edited_movie.id:
            raise HTTPException(status_code=500, detail="ID cant be changed")
        else:
            movies[movies.index(current_movie)] = edited_movie.dict()
            return {"status": 200, "movies": movies}
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@app.delete("/api/movies/:id", response_model=dict)
def delete_movie(movie_id: int):
    try:
        current_movie = [movie for movie in movies if movie.get("id") == movie_id][0]
        if current_movie:
            movies.pop(movies.index(current_movie))
            return {"status": 202}
        else:
            raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        return {"status": 500, "reason": str(e)}


