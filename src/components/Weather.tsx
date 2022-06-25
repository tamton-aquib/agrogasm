import { useRef, useState } from 'react';
import './Weather.css'

const API_KEY = "0cb7faf5612cfcefe21a8ef6857b7391"

const Weather = () => {
    const [query, setQuery] = useState("");
    const [weather, setWeather] = useState("");
    const [condition, setCondition] = useState("");
    const [temp, setTemp] = useState("");

    const cityRef = useRef()

    const getTodaysDate = () => {
        let d = new Date();
        return `${d.getDate()}-${d.getMonth() + 1}-${d.getFullYear()}`
    }

    async function getData() {
        const cityName = cityRef.current.value;

        const url = `https://api.openweathermap.org/data/2.5/weather?units=metrics&appid=${API_KEY}&q=${cityName}`
        await (await fetch(url)).json()
            .then(data => {
                setQuery("");
                let weather_condition = data.weather['0']['description']
                setWeather(data.name);
                setCondition(weather_condition)
                setTemp(`${Math.round(data.main.temp - 273)} ℃ `);
            })
    }

    return (<>
        <div className="date">{getTodaysDate()}</div>
        <div className="search">
            <input
                type="text"
                className="search-box"
                placeholder="Search..."
                onChange={e => { setQuery(e.target.value) }}
                value={query}
                ref={cityRef}
            />
            <span onClick={() => { getData() }} className="button"></span>
        </div>
        <div className="location">{weather}</div>
        <div className="weather-box">
            <div className="temp">{temp}</div>
            <div className="weather">{condition}</div>
        </div>
    </>)
}

export default Weather
