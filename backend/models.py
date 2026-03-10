from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Enum, Float, Date, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True) # Kolom 'Kode'
    name = Column(String(100))                          # Nama Perusahaan
    listing_date = Column(Date)                    # Tanggal Pencatatan
    shares = Column(BigInteger)                          # Jumlah Saham
    listing_board = Column(String(50))                   # Papan Pencatatan
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reports = relationship("FinancialReport", back_populates="owner")

class FinancialReport(Base):
    __tablename__ = "financial_reports"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    year = Column(Integer)
    period = Column(String(10)) # Q1, FY, dll
    revenue = Column(BigInteger)
    currency = Column(String(3)) # IDR or USD
    owner = relationship("Company", back_populates="reports")
    breakdowns = relationship("FinancialBreakdown", back_populates="report")

class FinancialBreakdown(Base):
    __tablename__ = "financial_breakdowns"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"))
    type = Column(String(50)) # REVENUE_BY_SECTOR, GEOGRAPHICAL
    label = Column(String(100))
    amount = Column(BigInteger)
    
    report = relationship("FinancialReport", back_populates="breakdowns")