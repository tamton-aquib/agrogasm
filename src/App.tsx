import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'

import BottomNav from './components/BottomNav'
import ErrorBoundary from './components/ErrorBoundary'

import Community from './components/Community'
import Weather from './components/Weather'
import Settings from './components/Settings'
import NewPost from './components/NewPost'
import NotFound from './components/NotFound'

function App() {
    return (
        <Router>
            <ErrorBoundary>
                <div className="App">
                    <Routes>
                        <Route path="/" element={<Weather />} />
                        <Route path="/community" element={<Community />} />
                        <Route path="/community/new" element={<NewPost />} />
                        <Route path="/settings" element={<Settings />} />
                        <Route path="*" element={<NotFound />} />
                    </Routes>
                    <BottomNav />
                </div>
            </ErrorBoundary>
        </Router>
    )
}

export default App
