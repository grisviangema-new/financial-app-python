from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database

app = FastAPI(title="Financial Analysis API")

# Buat tabel otomatis saat startup
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def home():
    return {"message": "Backend Python Saham Indonesia Aktif"}

@app.get("/companies")
def get_companies(db: Session = Depends(database.get_db)):
    return db.query(models.Company).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)