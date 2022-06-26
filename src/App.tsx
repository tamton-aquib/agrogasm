import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'

import BottomNav from './components/BottomNav'

import Community from './components/Community'
import Weather from './components/Weather'
import Profile from './components/Settings'

function App() {
	return (
		<Router>
			<div className="App">
				<Routes>
					<Route path="/" exact element={<Weather />} />
					<Route path="/community" element={<Community />} />
					<Route path="/profile" element={<Profile />} />
				</Routes>
				<BottomNav />
			</div>
		</Router>
	)
}

export default App
