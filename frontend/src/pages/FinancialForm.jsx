import React, { useState } from 'react';
import { Plus, Trash2, Save, Building2 } from 'lucide-react';
import axios from 'axios';

const FinancialForm = () => {
  const [formData, setFormData] = useState({
    ticker: '',
    year: new Date().getFullYear(),
    period: 'FY',
    revenue: 0,
    currency: 'IDR', // Default IDR
    breakdowns: [] // Untuk detail rincian sektor/geografis
  });

  const addBreakdown = () => {
    setFormData({
      ...formData,
      breakdowns: [...formData.breakdowns, { type: 'REVENUE_BY_SECTOR', label: '', amount: 0 }]
    });
  };

  const handleSave = async () => {
    try {
      // Endpoint FastAPI port 8000
      const res = await axios.post('http://localhost:8000/reports', formData);
      alert("Data berhasil disimpan ke MySQL!");
    } catch (err) {
      console.error(err);
      alert("Gagal menyimpan data. Pastikan Backend Python menyala.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 bg-white shadow-lg rounded-2xl border border-slate-200">
      <div className="flex items-center gap-3 mb-8 border-b pb-4">
        <Building2 className="text-blue-600" size={32} />
        <h1 className="text-2xl font-bold text-slate-800">Input Mikroanalisis Emiten</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div>
          <label className="block text-sm font-semibold text-slate-600">Ticker Saham</label>
          <input 
            type="text" 
            placeholder="Contoh: ASII"
            className="w-full mt-1 p-3 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
            onChange={(e) => setFormData({...formData, ticker: e.target.value.toUpperCase()})}
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-600">Tahun Laporan</label>
          <input 
            type="number" 
            className="w-full mt-1 p-3 border rounded-xl"
            value={formData.year}
            onChange={(e) => setFormData({...formData, year: e.target.value})}
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-600">Periode</label>
          <select className="w-full mt-1 p-3 border rounded-xl" onChange={(e) => setFormData({...formData, period: e.target.value})}>
            <option value="FY">Full Year (FY)</option>
            <option value="Q1">Quarter 1 (Q1)</option>
            <option value="Q2">Quarter 2 (Q2)</option>
            <option value="Q3">Quarter 3 (Q3)</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
        <div>
            <label className="block text-sm font-semibold text-slate-600">Mata Uang Laporan</label>
            <select 
            className="w-full mt-1 p-3 border rounded-xl"
            value={formData.currency}
            onChange={(e) => setFormData({...formData, currency: e.target.value})}
            >
            <option value="IDR">Rupiah (IDR)</option>
            <option value="USD">US Dollar (USD)</option>
            </select>
        </div>
        <div>
            <label className="block text-sm font-semibold text-slate-600">
            Total Pendapatan ({formData.currency === 'IDR' ? 'Input Angka Asli' : 'Input USD'})
            </label>
            <input 
            type="number" 
            className="w-full mt-1 p-3 border rounded-xl"
            onChange={(e) => setFormData({...formData, revenue: e.target.value})}
            />
            <p className="text-xs text-slate-500 mt-1 italic">
            *Sistem akan otomatis membulatkan ke {formData.currency === 'IDR' ? 'Miliar' : 'Juta'} di Dashboard.
            </p>
        </div>
        </div>

      <div className="bg-slate-50 p-6 rounded-2xl border border-dashed border-slate-300">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold text-slate-700">Rincian Pendapatan & Aset (Breakdown)</h2>
          <button 
            onClick={addBreakdown}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <Plus size={18} /> Tambah Rincian
          </button>
        </div>

        {formData.breakdowns.map((item, index) => (
          <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3 items-end">
            <select className="p-2 border rounded-lg bg-white">
              <option value="REVENUE_BY_SECTOR">Sektor Bisnis</option>
              <option value="REVENUE_BY_GEO">Geografis (Ekspor/Impor)</option>
              <option value="ASSET_DETAIL">Rincian Aset</option>
            </select>
            <input type="text" placeholder="Label (Misal: Ekspor China)" className="p-2 border rounded-lg" />
            <input type="number" placeholder="Nilai (IDR)" className="p-2 border rounded-lg" />
            <button className="text-red-500 hover:bg-red-50 p-2 rounded-lg"><Trash2 size={20}/></button>
          </div>
        ))}
      </div>

      <button 
        onClick={handleSave}
        className="w-full mt-8 bg-emerald-600 text-white font-bold py-4 rounded-xl hover:bg-emerald-700 flex justify-center items-center gap-2 shadow-lg shadow-emerald-200 transition"
      >
        <Save size={20} /> Simpan Laporan Ke MySQL
      </button>
    </div>
  );
};

export default FinancialForm;