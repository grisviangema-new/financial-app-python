from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import models, database
import traceback

app = FastAPI()

#Membuat semua tabel di database jika belum ada
database.Base.metadata.create_all(bind=database.engine)

# --- MIDDLEWARE CORS ---
# Penting agar React (port 5173) bisa mengirim data ke Python (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMA DATA (Validasi Input) ---
class BreakdownSchema(BaseModel):
    type: str
    label: str
    amount: int

class ReportSchema(BaseModel):
    ticker: str
    year: int
    period: str
    revenue: int
    breakdowns: List[BreakdownSchema]

# --- ENDPOINT SIMPAN DATA ---
@app.post("/reports")
def create_report(report_data: ReportSchema, db: Session = Depends(database.get_db)):
    try:
        # 1. Cek apakah perusahaan sudah ada, jika belum buat baru
        company = db.query(models.Company).filter(models.Company.ticker == report_data.ticker).first()
        if not company:
            company = models.Company(ticker=report_data.ticker, name=report_data.ticker)
            db.add(company)
            db.commit()
            db.refresh(company)

        # 2. Simpan Laporan Utama
        new_report = models.FinancialReport(
            company_id=company.id,
            year=report_data.year,
            period=report_data.period,
            revenue=report_data.revenue
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # 3. Simpan Detail Breakdown
        for item in report_data.breakdowns:
            new_breakdown = models.FinancialBreakdown(
                report_id=new_report.id,
                type=item.type,
                label=item.label,
                amount=item.amount
            )
            db.add(new_breakdown)
        
        db.commit()
        return {"status": "success", "message": f"Laporan {report_data.ticker} berhasil disimpan"}

    except Exception as e:
        db.rollback() # Batalkan jika ada error
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))