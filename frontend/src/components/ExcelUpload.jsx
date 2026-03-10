import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, X, CheckCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const ExcelUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', msg: '' });

  // Fungsi saat file di-drop
  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setFile(selectedFile);
      setStatus({ type: '', msg: '' });
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/upload-companies', formData);
      setStatus({ type: 'success', msg: res.data.message });
      setFile(null);
    } catch (err) {
      setStatus({ type: 'error', msg: 'Gagal mengupload file. Cek format kolom Excel Anda.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-3xl shadow-sm border border-slate-200">
      <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
        <FileSpreadsheet className="text-emerald-600" /> Bulk Update Emiten
      </h2>

      {/* Area Drag and Drop */}
      <div 
        {...getRootProps()} 
        className={`relative border-2 border-dashed rounded-2xl p-10 transition-all cursor-pointer text-center
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 bg-slate-50'}`}
      >
        <input {...getInputProps()} />
        <Upload className={`mx-auto mb-4 ${isDragActive ? 'text-blue-500 scale-110' : 'text-slate-400'}`} size={40} />
        
        {file ? (
          <div className="flex items-center justify-center gap-2 text-emerald-600 font-semibold">
            <CheckCircle size={18} /> {file.name}
          </div>
        ) : (
          <div>
            <p className="text-slate-700 font-medium">Tarik & letakkan file Excel di sini</p>
            <p className="text-slate-400 text-sm mt-1">Atau klik untuk memilih file (.xlsx, .xls)</p>
          </div>
        )}
      </div>

      {/* Feedback & Tombol */}
      {status.msg && (
        <div className={`mt-4 p-3 rounded-lg text-sm font-medium ${
          status.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
        }`}>
          {status.msg}
        </div>
      )}

      <div className="mt-6 flex gap-3">
        {file && !loading && (
          <button 
            onClick={() => setFile(null)}
            className="flex-1 py-3 px-4 border border-slate-300 rounded-xl font-semibold text-slate-600 hover:bg-slate-50"
          >
            Batal
          </button>
        )}
        <button 
          onClick={handleUpload}
          disabled={!file || loading}
          className={`flex-2 w-full py-3 px-6 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg transition
            ${!file || loading ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' : 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200'}`}
        >
          {loading ? <Loader2 className="animate-spin" /> : <Upload size={18} />}
          {loading ? 'Memproses...' : 'Update Database'}
        </button>
      </div>
    </div>
  );
};

export default ExcelUpload;