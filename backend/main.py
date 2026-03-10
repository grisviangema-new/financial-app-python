from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models, database
import traceback
from schemas import ReportSchema, BreakdownSchema
import yfinance as yf

app = FastAPI()

#Membuat semua tabel di database jika belum ada
database.Base.metadata.create_all(bind=database.engine)

# Fungsi untuk mendapatkan kurs USD/IDR terbaru
def get_exchange_rate():
    try:
        ticker = yf.Ticker("IDR=X")
        data = ticker.history(period="1d")
        return data['Close'].iloc[-1]
    except:
        return 15700  # Fallback jika API gagal

# --- MIDDLEWARE CORS ---
# Penting agar React (port 5173) bisa mengirim data ke Python (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- ENDPOINT SIMPAN DATA ---
@app.post("/reports")
def create_report(report_data: ReportSchema, db: Session = Depends(database.get_db)):
    kurs = get_exchange_rate()

    # Logic Pembulatan & Konversi
    # Jika input dalam IDR, simpan asli dan versi konversi USD
    # Kita asumsikan user menginput angka asli (misal: 1.000.000.000)
    
    revenue_idr = report_data.revenue
    if report_data.currency == "IDR":
        # Bulatkan ke Miliar (dibagi 10^9)
        val_display = round(revenue_idr / 1_000_000_000, 2) 
        unit = "Miliar IDR"
    else:
        # Jika USD, bulatkan ke Juta (dibagi 10^6)
        val_display = round(revenue_idr / 1_000_000, 2)
        unit = "Juta USD"
        
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