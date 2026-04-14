
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base

from auth import router as auth_router
from equipment import router as equipment_router
from rooms import router as rooms_router
from reservations import router as reservations_router
from notifications import router as notifications_router
from equipment_returns import router as equipment_returns_router
from analytics import router as analytics_router
from realtime import manager

app = FastAPI()

# enable CORS for frontend
origins = [
    "http://localhost:3000",
    "https://avrc-system.onrender.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import models so metadata is registered, then create tables
import models  # noqa: F401
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Database tables already exist or error creating tables:", e)

try:
    from migrate_equipment_purchase_date import migrate as migrate_equipment_purchase_date_column

    migrate_equipment_purchase_date_column()
except Exception as e:
    print("migrate_equipment_purchase_date (startup):", e)

try:
    from equipment_purchase_dates import fill_equipment_purchase_dates

    _startup_db = SessionLocal()
    try:
        _n = fill_equipment_purchase_dates(_startup_db, only_missing=True)
        if _n:
            print(f"[OK] Filled {_n} equipment row(s) with sample purchase_date (was missing)")
    finally:
        _startup_db.close()
except Exception as e:
    print("fill_equipment_purchase_dates (startup):", e)

# include routers
app.include_router(auth_router)
app.include_router(equipment_router)
app.include_router(rooms_router)
app.include_router(reservations_router)
app.include_router(notifications_router)
app.include_router(equipment_returns_router)
app.include_router(analytics_router)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=1008)
        return

    try:
        from utils import decode_access_token
        from models import User

        user_id = decode_access_token(token)
        if not user_id:
            await ws.close(code=1008)
            return

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            is_admin = bool(user and (getattr(user, "role", "") or "").lower() == "admin")
        finally:
            db.close()

        await manager.connect(ws, user_id=int(user_id), is_admin=is_admin)
        await ws.send_json({"type": "connected", "user_id": int(user_id), "is_admin": is_admin})

        while True:
            # Keep connection alive; client doesn't need to send messages
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)
        try:
            await ws.close(code=1011)
        except Exception:
            pass

@app.get("/")
def read_root():
    return {"message": "AVRC Reservation System Backend is running!"}

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    from sqlalchemy import text
    try:
        db.execute(text("SELECT 1"))
        return {"db_status": "Connected"}
    except Exception as e:
        return {"db_status": "Error", "details": str(e)}
