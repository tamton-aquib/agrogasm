import { useState } from 'react'
import './App.css'

import BottomNav from './components/BottomNav'
import Weather from './components/Weather'

function App() {
    return (
        <div className="App">
            <BottomNav />
            <Weather />
        </div>
    )
}

export default App
