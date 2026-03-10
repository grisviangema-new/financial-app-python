import FinancialForm from './pages/FinancialForm';
import ExcelUpload from './components/ExcelUpload';

function App() {
  return (
    <div className="min-h-screen bg-slate-100 py-10">
      <ExcelUpload />
      <FinancialForm />
    </div>
  );
}

export default App;