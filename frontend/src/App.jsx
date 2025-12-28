import DetailsList from './components/DetailsList'
import SuggestForm from './components/SuggestForm'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-800">Mini Detail Library</h1>
          <p className="text-gray-600">Search and get architectural detail suggestions</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 flex-grow">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DetailsList />
          <SuggestForm />
        </div>
      </main>

      <footer className="bg-white border-t mt-auto">
        <div className="max-w-6xl mx-auto px-4 py-4 text-center text-gray-500 text-sm">
          <a href="https://piaxis.ai/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:text-blue-800 hover:underline">
            piaxis.ai
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App