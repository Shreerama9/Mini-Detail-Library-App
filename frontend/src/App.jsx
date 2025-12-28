import DetailsList from './components/DetailsList'
import SuggestForm from './components/SuggestForm'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-800">Mini Detail Library</h1>
          <p className="text-gray-600">Search and get architectural detail suggestions</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DetailsList />
          <SuggestForm />
        </div>
      </main>

      <footer className="bg-white border-t mt-8">
        <div className="max-w-6xl mx-auto px-4 py-4 text-center text-gray-500 text-sm">
          PiAxis Mini Detail Library - Assignment
        </div>
      </footer>
    </div>
  )
}

export default App
