import { useState } from 'react';
import { getWeatherCity } from '../config';
import './Settings.css'

function readLS(key: string, fallback: string): string {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

const Settings = () => {
    const [city, setCity] = useState(getWeatherCity());
    const [theme, setTheme] = useState(() => readLS('agrogasm.theme', 'system'));
    const [saved, setSaved] = useState(false);

    function save(e: React.FormEvent) {
        e.preventDefault();
        try {
            localStorage.setItem('agrogasm.city', city.trim() || 'Kottayam');
            localStorage.setItem('agrogasm.theme', theme);
            document.documentElement.dataset.theme = theme;
        } catch {
            // storage unavailable, still show saved state
        }
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    }

    return (
        <div className="container">
            <h2>Settings</h2>
            <form onSubmit={save}>
                <label>
                    Weather city
                    <input
                        aria-label="Weather city"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        placeholder="Kottayam"
                        maxLength={80}
                    />
                </label>
                <label>
                    Theme
                    <select aria-label="Theme" value={theme} onChange={(e) => setTheme(e.target.value)}>
                        <option value="system">System</option>
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                    </select>
                </label>
                <button type="submit">Save</button>
                {saved && <p role="status">Saved. Reload Weather to apply city.</p>}
            </form>
            <p className="hint">City and theme are stored locally in your browser only.</p>
        </div>
    )
}

export default Settings
