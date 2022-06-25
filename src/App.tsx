import { useState } from 'react'
import './App.css'

import BottomNav from './components/BottomNav'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <BottomNav />
    </div>
  )
}

export default App
