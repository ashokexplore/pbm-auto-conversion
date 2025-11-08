import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={
            <div className="container mx-auto px-4 py-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                PBM Auto Conversion System
              </h1>
              <p className="text-gray-600">
                AI-powered data transformation application
              </p>
            </div>
          } />
        </Routes>
      </div>
    </Router>
  )
}

export default App

