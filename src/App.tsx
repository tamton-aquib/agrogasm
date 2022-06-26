import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'

import BottomNav from './components/BottomNav'

import Community from './components/Community'
import Weather from './components/Weather'
import Settings from './components/Settings'
import NewPost from './components/NewPost'

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/" exact element={<Weather />} />
                    <Route path="/community" element={<Community />} />
                    <Route path="/community/new" element={<Community />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/community/new" element={<NewPost />} />
                </Routes>
                <BottomNav />
            </div>
        </Router>
    )
}

export default App
