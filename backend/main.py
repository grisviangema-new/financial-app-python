from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from schemas import ReportSchema, BreakdownSchema
from datetime import datetime
from io import BytesIO

import pandas as pd
import models, database
import traceback
import yfinance as yf
import dateparser


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

# Fungsi pembantu untuk membersihkan angka saham
def clean_numeric(value):
    if pd.isna(value): return 0
    # Hilangkan titik jika terbaca sebagai string (misal: "1.924.688.333" -> "1924688333")
    if isinstance(value, str):
        value = value.replace('.', '').replace(',', '')
    return int(float(value))

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
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/upload-companies")
async def upload_companies(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        contents = await file.read()
        # Membaca excel, pastikan kolom dibaca apa adanya
        df = pd.read_excel(BytesIO(contents))

        # Standarisasi Nama Kolom (antisipasi spasi berlebih)
        df.columns = [c.strip() for c in df.columns]

        for index, row in df.iterrows():
            ticker = str(row['Kode']).strip()

            # --- LOGIKA PARSING TANGGAL ---
            raw_date = str(row['Tanggal Pencatatan'])
            # dateparser mendukung multibahasa (termasuk 'Des' untuk Desember)
            parsed_date = dateparser.parse(raw_date, languages=['id'])
            
            # Jika parsing gagal, gunakan None atau tanggal default
            final_date = parsed_date.date() if parsed_date else None
            
            # Membersihkan data saham
            raw_saham = clean_numeric(row['Saham'])

            # Update atau Insert logic
            existing = db.query(models.Company).filter(models.Company.ticker == ticker).first()
            
            if existing:
                existing.name = row['Nama Perusahaan']
                existing.shares = raw_saham
                existing.listing_board = row['Papan Pencatatan']
                existing.listing_date = final_date
                existing.last_updated = datetime.now()
            else:
                new_item = models.Company(
                    ticker=ticker,
                    name=row['Nama Perusahaan'],
                    listing_date=final_date,
                    shares=raw_saham,
                    listing_board=row['Papan Pencatatan'],
                    last_updated=datetime.now()
                )
                db.add(new_item)
        
        db.commit()
        return {"message": f"Berhasil memproses {len(df)} emiten."}
        
    except Exception as e:
        db.rollback()
        print(f"Detail Error: {str(e)}") # Cek ini di terminal uvicorn Anda
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")