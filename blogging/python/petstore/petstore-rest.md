# 1) Create the project (Hatch)

```bash
mkdir petstore-project && cd petstore-project
python -m venv .venv
source .venv/bin/activate
pip install hatch

# 1) New project with src layout
hatch new petstore
cd petstore

# 2) Make sure Hatch uses src/ layout
# (Hatch does this by default for 'new --init'; we’ll confirm in pyproject)

# 3) Add runtime & dev deps
hatch run pip install fastapi "uvicorn[standard]" pydantic pytest anyio httpx

# OR declare them in pyproject (below) and:
# hatch env create
```

---

# 2) Project structure

```
petstore/
├─ pyproject.toml
├─ src/
│  └─ petstore/
│     ├─ __init__.py
│     ├─ app.py
│     ├─ config.py
│     ├─ errors.py
│     ├─ middleware.py
│     ├─ models.py
│     ├─ schemas.py
│     ├─ services/
│     │  └─ pets.py
│     ├─ repositories/
│     │  ├─ __init__.py
│     │  ├─ base.py
│     │  └─ inmem.py
│     └─ api/
│        ├─ __init__.py
│        ├─ deps.py
│        └─ pets.py
└─ tests/
   └─ test_pets.py
```

---

# 3) `pyproject.toml` (Hatch + scripts)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "petstore"
version = "0.1.0"
description = "Modular REST API petstore (FastAPI + in-memory DB) using Hatch"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "pydantic>=2.8"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "httpx>=0.27",
  "anyio>=4.4",
]

[tool.hatch.build.targets.wheel]
packages = ["src/petstore"]

[tool.hatch.envs.default]
features = ["dev"]

[tool.hatch.envs.default.scripts]
dev = "uvicorn petstore.app:app --reload"
test = "pytest -q"
```

Run:

```bash
hatch run dev  # starts server on http://127.0.0.1:8000
```

---

# 4) Domain model & schemas

## `src/petstore/models.py`

```python
from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime

PetStatus = Literal["available", "pending", "sold"]

@dataclass
class Pet:
    id: int
    name: str
    species: str
    age_years: Optional[int] = None
    status: PetStatus = "available"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1  # for optimistic concurrency
```

## `src/petstore/schemas.py`

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

PetStatus = Literal["available", "pending", "sold"]

class PetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    species: str = Field(min_length=1, max_length=64)
    age_years: Optional[int] = Field(default=None, ge=0, le=100)
    status: PetStatus = "available"

class PetUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    species: Optional[str] = Field(default=None, min_length=1, max_length=64)
    age_years: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[PetStatus] = None

class PetOut(BaseModel):
    id: int
    name: str
    species: str
    age_years: Optional[int]
    status: PetStatus
    version: int

    class Config:
        from_attributes = True

class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int

class PetList(BaseModel):
    items: list[PetOut]
    _meta: PageMeta
```

---

# 5) Repository abstraction + in-memory implementation

## `src/petstore/repositories/base.py`

```python
from typing import Protocol, Optional, Iterable
from ..models import Pet

class PetRepository(Protocol):
    def create(self, pet: Pet) -> Pet: ...
    def get(self, pet_id: int) -> Optional[Pet]: ...
    def update(self, pet: Pet, *, expected_version: Optional[int] = None) -> Pet: ...
    def delete(self, pet_id: int) -> bool: ...
    def list(
        self,
        *,
        species: Optional[str] = None,
        status: Optional[str] = None,
        sort: Optional[str] = None,   # "name", "-name", "created_at", "-created_at"
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Pet], int]: ...
```

## `src/petstore/repositories/inmem.py`

```python
from __future__ import annotations
from typing import Optional
from threading import RLock
from datetime import datetime
from ..models import Pet
from .base import PetRepository

class InMemoryPetRepo(PetRepository):
    def __init__(self) -> None:
        self._data: dict[int, Pet] = {}
        self._next_id = 1
        self._lock = RLock()

    def create(self, pet: Pet) -> Pet:
        with self._lock:
            pet.id = self._next_id
            self._next_id += 1
            self._data[pet.id] = pet
            return pet

    def get(self, pet_id: int) -> Optional[Pet]:
        with self._lock:
            return self._data.get(pet_id)

    def update(self, pet: Pet, *, expected_version: Optional[int] = None) -> Pet:
        with self._lock:
            current = self._data.get(pet.id)
            if not current:
                raise KeyError("not found")
            if expected_version is not None and current.version != expected_version:
                raise ValueError("version_conflict")
            # apply update
            pet.version = current.version + 1
            pet.updated_at = datetime.utcnow()
            self._data[pet.id] = pet
            return pet

    def delete(self, pet_id: int) -> bool:
        with self._lock:
            return self._data.pop(pet_id, None) is not None

    def list(
        self,
        *,
        species: Optional[str] = None,
        status: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Pet], int]:
        with self._lock:
            items = list(self._data.values())
            if species:
                items = [p for p in items if p.species.lower() == species.lower()]
            if status:
                items = [p for p in items if p.status == status]
            # sorting
            key = "name"
            reverse = False
            if sort:
                reverse = sort.startswith("-")
                key = sort[1:] if reverse else sort
            items.sort(key=lambda p: getattr(p, key, None), reverse=reverse)
            total = len(items)
            items = items[offset: offset + limit]
            return items, total
```

---

# 6) Service layer (business logic)

## `src/petstore/services/pets.py`

```python
from typing import Optional
from dataclasses import replace
from ..models import Pet
from ..schemas import PetCreate, PetUpdate
from ..repositories.base import PetRepository

class PetService:
    def __init__(self, repo: PetRepository):
        self.repo = repo

    def create(self, data: PetCreate) -> Pet:
        pet = Pet(id=0, name=data.name, species=data.species,
                  age_years=data.age_years, status=data.status)
        return self.repo.create(pet)

    def get(self, pet_id: int) -> Optional[Pet]:
        return self.repo.get(pet_id)

    def list(self, **kwargs):
        return self.repo.list(**kwargs)

    def replace(self, pet_id: int, data: PetCreate, *, expected_version: Optional[int]) -> Pet:
        current = self.repo.get(pet_id)
        if not current:
            raise KeyError("not found")
        new_pet = replace(current,
                          name=data.name,
                          species=data.species,
                          age_years=data.age_years,
                          status=data.status)
        return self.repo.update(new_pet, expected_version=expected_version)

    def update_partial(self, pet_id: int, patch: PetUpdate, *, expected_version: Optional[int]) -> Pet:
        current = self.repo.get(pet_id)
        if not current:
            raise KeyError("not found")
        new_pet = replace(
            current,
            name = patch.name if patch.name is not None else current.name,
            species = patch.species if patch.species is not None else current.species,
            age_years = patch.age_years if patch.age_years is not None else current.age_years,
            status = patch.status if patch.status is not None else current.status,
        )
        return self.repo.update(new_pet, expected_version=expected_version)

    def delete(self, pet_id: int) -> bool:
        return self.repo.delete(pet_id)
```

---

# 7) API layer (routers, deps, error handling, ETags)

## `src/petstore/errors.py`

```python
from fastapi import HTTPException, status

def not_found(entity: str = "Resource"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")

def precondition_required():
    raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                        detail="Missing If-Match header for write with concurrency control")

def precondition_failed():
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                        detail="ETag mismatch (version conflict)")
```

## `src/petstore/api/deps.py`

```python
from functools import lru_cache
from ..repositories.inmem import InMemoryPetRepo
from ..services.pets import PetService

@lru_cache
def get_pet_service() -> PetService:
    # one shared in-memory repo instance for the process
    return PetService(InMemoryPetRepo())
```

## `src/petstore/api/pets.py`

```python
from typing import Optional
from fastapi import APIRouter, Depends, status, Response, Header, Query
from ..schemas import PetCreate, PetUpdate, PetOut, PetList, PageMeta
from ..services.pets import PetService
from ..api.deps import get_pet_service
from ..errors import not_found, precondition_required, precondition_failed

router = APIRouter(prefix="/pets", tags=["pets"])

def make_etag(version: int) -> str:
    # Weak ETag; good enough for demo
    return f'W/"{version}"'

@router.post("", response_model=PetOut, status_code=status.HTTP_201_CREATED)
def create_pet(data: PetCreate, resp: Response, svc: PetService = Depends(get_pet_service)):
    pet = svc.create(data)
    resp.headers["Location"] = f"/pets/{pet.id}"
    resp.headers["ETag"] = make_etag(pet.version)
    return pet

@router.get("/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int, resp: Response, svc: PetService = Depends(get_pet_service)):
    pet = svc.get(pet_id)
    if not pet:
        not_found("Pet")
    resp.headers["ETag"] = make_etag(pet.version)
    return pet

@router.get("", response_model=PetList)
def list_pets(
    species: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(available|pending|sold)$"),
    sort: Optional[str] = Query(None, pattern="^-?(name|created_at)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: PetService = Depends(get_pet_service),
):
    items, total = svc.list(species=species, status=status, sort=sort, limit=limit, offset=offset)
    return PetList(items=items, _meta=PageMeta(total=total, limit=limit, offset=offset))

@router.put("/{pet_id}", response_model=PetOut)
def replace_pet(
    pet_id: int,
    data: PetCreate,
    resp: Response,
    svc: PetService = Depends(get_pet_service),
    if_match: Optional[str] = Header(default=None, alias="If-Match"),
):
    if if_match is None:
        precondition_required()
    expected = int(if_match.strip('W/"'))
    try:
        pet = svc.replace(pet_id, data, expected_version=expected)
    except KeyError:
        not_found("Pet")
    except ValueError:
        precondition_failed()
    resp.headers["ETag"] = make_etag(pet.version)
    return pet

@router.patch("/{pet_id}", response_model=PetOut)
def update_pet(
    pet_id: int,
    patch: PetUpdate,
    resp: Response,
    svc: PetService = Depends(get_pet_service),
    if_match: Optional[str] = Header(default=None, alias="If-Match"),
):
    if if_match is None:
        precondition_required()
    expected = int(if_match.strip('W/"'))
    try:
        pet = svc.update_partial(pet_id, patch, expected_version=expected)
    except KeyError:
        not_found("Pet")
    except ValueError:
        precondition_failed()
    resp.headers["ETag"] = make_etag(pet.version)
    return pet

@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, svc: PetService = Depends(get_pet_service)):
    ok = svc.delete(pet_id)
    if not ok:
        not_found("Pet")
```

---

# 8) App factory, middleware, and config

## `src/petstore/config.py`

```python
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Petstore API"
    version: str = "0.1.0"

settings = Settings()
```

## `src/petstore/middleware.py`

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request

class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

## `src/petstore/app.py`

```python
from fastapi import FastAPI
from .config import settings
from .middleware import RequestIDMiddleware
from .api.pets import router as pets_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    contact={"name": "Petstore", "url": "https://example.com"},
)

app.add_middleware(RequestIDMiddleware)
app.include_router(pets_router)

# Health
@app.get("/health")
def health():
    return {"status": "ok"}
```

---

# 9) Tests (happy path)

## `tests/test_pets.py`

```python
import anyio
from fastapi import status
from httpx import AsyncClient
from petstore.app import app

async def _client():
    return AsyncClient(app=app, base_url="http://test")

@anyio.run
async def test_crud_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create
        r = await client.post("/pets", json={"name":"Fido","species":"dog","age_years":3})
        assert r.status_code == status.HTTP_201_CREATED
        pet = r.json()
        pet_id = pet["id"]
        etag = r.headers["ETag"]

        # Get
        r = await client.get(f"/pets/{pet_id}")
        assert r.status_code == 200

        # List
        r = await client.get("/pets?species=dog&limit=10&offset=0&sort=name")
        assert r.status_code == 200
        assert r.json()["_meta"]["total"] >= 1

        # Patch with ETag
        r = await client.patch(f"/pets/{pet_id}", headers={"If-Match": etag}, json={"status":"pending"})
        assert r.status_code == 200
        new_etag = r.headers["ETag"]

        # Delete
        r = await client.delete(f"/pets/{pet_id}")
        assert r.status_code == status.HTTP_204_NO_CONTENT

        # Not found
        r = await client.get(f"/pets/{pet_id}")
        assert r.status_code == 404
```

---

# 10) How to run

```bash
# Start the API (auto-reload)
hatch run dev
# -> http://127.0.0.1:8000/docs for Swagger UI

# Run tests
hatch run test
```

---

# 11) Sample cURL calls (core REST concepts)

```bash
# Create (201 + Location + ETag)
curl -i -X POST http://127.0.0.1:8000/pets \
  -H "Content-Type: application/json" \
  -d '{"name":"Mittens","species":"cat","age_years":2,"status":"available"}'

# Read (200 + ETag)
curl -i http://127.0.0.1:8000/pets/1

# List with pagination/filter/sort
curl -s "http://127.0.0.1:8000/pets?species=cat&status=available&limit=10&offset=0&sort=-created_at" | jq

# Update with optimistic concurrency (412 on mismatch)
ETAG=$(curl -si http://127.0.0.1:8000/pets/1 | grep ETag | awk '{print $2}' | tr -d '\r')
curl -i -X PATCH http://127.0.0.1:8000/pets/1 \
  -H "If-Match: ${ETAG}" \
  -H "Content-Type: application/json" \
  -d '{"status":"sold"}'

# Delete (204)
curl -i -X DELETE http://127.0.0.1:8000/pets/1
```

---

# Why this satisfies your goals

* **Modular**: clear separation into `api/`, `services/`, `repositories/`, `models.py`, `schemas.py`.
* **Hatch**: single project name `petstore` yields `src/petstore` layout; handy scripts (`dev`, `test`).
* **Core REST concepts**: resource URIs, proper methods & status codes, validation, **Location** header on create, **ETag / If-Match** for concurrency, **pagination/filter/sort**, structured error responses, and OpenAPI docs at `/docs`.
* **Simple**: in-memory thread-safe dict repo (no external DB), but you can later swap `InMemoryPetRepo` with a real database implementation without changing handlers.
