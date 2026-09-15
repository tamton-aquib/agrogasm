import { useEffect, useState } from 'react';
import { WEATHER_API_KEY, getWeatherCity } from '../config';
import cloudsUrl from '../assets/clouds.gif';
import './Weather.css'
import Alert from './Alert'

interface WeatherState {
    condition: string;
    location: string;
    temp: string;
    icon: string;
}

interface WeatherAlert {
    event: string;
    description: string;
    severity: 'red' | 'orange';
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

function ordinal(day: number): string {
    if (day >= 11 && day <= 13) return `${day}th`;
    switch (day % 10) {
        case 1: return `${day}st`;
        case 2: return `${day}nd`;
        case 3: return `${day}rd`;
        default: return `${day}th`;
    }
}

function getTodaysDate(d = new Date()): string {
    return `${ordinal(d.getDate())} ${MONTHS[d.getMonth()]} of ${d.getFullYear()}`;
}

function advisoryFor(condition: string): WeatherAlert[] {
    const c = condition.toLowerCase();
    if (c.includes('thunder') || c.includes('storm') || c.includes('cyclone')) {
        return [{ event: 'Red Alert', description: 'Severe storm conditions. Stay indoors.', severity: 'red' }];
    }
    if (c.includes('heavy rain') || c.includes('extreme') || c.includes('flood')) {
        return [{ event: 'Orange Alert', description: 'Heavy rain expected. Take precautions.', severity: 'orange' }];
    }
    return [];
}

const Weather = () => {
    const [city] = useState(getWeatherCity());
    const [weather, setWeather] = useState<WeatherState>({ condition: '', location: city, temp: '', icon: '' });
    const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
    const [loading, setLoading] = useState(true);
    const [weatherError, setWeatherError] = useState<string | null>(null);

    useEffect(() => {
        const controller = new AbortController();
        async function load() {
            if (!WEATHER_API_KEY) {
                setWeatherError('Missing VITE_OWM_KEY. Add it to .env to enable live weather.');
                setLoading(false);
                return;
            }
            try {
                setLoading(true);
                const url = `https://api.openweathermap.org/data/2.5/weather?units=metric&appid=${WEATHER_API_KEY}&q=${encodeURIComponent(city)}`;
                const res = await fetch(url, { signal: controller.signal });
                if (!res.ok) throw new Error(`Weather API responded ${res.status}`);
                const data = await res.json();
                const condition: string = data.weather?.[0]?.description ?? 'unknown';
                const icon: string = data.weather?.[0]?.icon ?? '';
                setWeather({
                    condition,
                    location: data.name ?? city,
                    temp: `${Math.round(data.main?.temp ?? 0)} ℃`,
                    icon,
                });

                // Try live severe-weather alerts via One Call 3.0 (needs subscription).
                // Fall back to condition-based advisory if unavailable.
                try {
                    const { lat, lon } = data.coord ?? {};
                    if (lat !== undefined && lon !== undefined) {
                        const oneCall = `https://api.openweathermap.org/data/3.0/onecall?lat=${lat}&lon=${lon}&exclude=current,minutely,hourly,daily&appid=${WEATHER_API_KEY}`;
                        const ar = await fetch(oneCall, { signal: controller.signal });
                        if (ar.ok) {
                            const aj = await ar.json();
                            const live: WeatherAlert[] = (aj.alerts ?? []).map((a: { event?: string; description?: string }) => ({
                                event: a.event ?? 'Weather Alert',
                                description: a.description ?? '',
                                severity: /red|extreme|emergency/i.test(a.event ?? '') ? 'red' : 'orange',
                            }));
                            setAlerts(live.length > 0 ? live : advisoryFor(condition));
                        } else {
                            setAlerts(advisoryFor(condition));
                        }
                    } else {
                        setAlerts(advisoryFor(condition));
                    }
                } catch {
                    if (!controller.signal.aborted) setAlerts(advisoryFor(condition));
                }
            } catch (err) {
                if ((err as Error).name !== 'AbortError') {
                    setWeatherError((err as Error).message);
                }
            } finally {
                if (!controller.signal.aborted) setLoading(false);
            }
        }
        load();
        return () => controller.abort();
    }, [city])

    const imgSrc = weather.icon
        ? `https://openweathermap.org/img/wn/${weather.icon}@2x.png`
        : cloudsUrl;

    return (<div className="container">
        <div className='title-wrapper'>
            <h3>Todays</h3>
            <h2>Forecast</h2>
        </div>
        <div className="date">{getTodaysDate()}</div>
        <img src={imgSrc} alt={weather.condition || 'weather'} className='weather-status-img' />
        <div className="location"><i className="fa fa-location-arrow" aria-hidden="true"></i> {weather.location}</div>
        <div className="weather-box">
            {loading ? <div className="temp">Loading...</div> : <div className="temp">{weather.temp}</div>}
            <div className="weather">{weather.condition}</div>
            {weatherError && <p role="alert">{weatherError}</p>}
        </div>
        <div className="alert-container">
            {alerts.length === 0 && !loading && !weatherError && (
                <p>No severe weather alerts for {weather.location}.</p>
            )}
            {alerts.map((a, i) => (
                <Alert
                    key={i}
                    myclassName={a.severity === 'red' ? 'red-alert' : 'orange-alert'}
                    content={a.description ? `${a.event}: ${a.description}` : a.event}
                />
            ))}
        </div>
    </div>
    )
}

export default Weather
