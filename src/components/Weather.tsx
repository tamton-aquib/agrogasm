import { useEffect, useRef, useState } from 'react';
import './Weather.css'
import Alert from './Alert'

const API_KEY = "0cb7faf5612cfcefe21a8ef6857b7391"

const Weather = () => {
    const [stuff, setStuff] = useState({
        "condition": "",
        "weather": "",
        "temp": ""
    });

    const month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

    const getTodaysDate = () => {
        let d = new Date();
        let name = month[d.getMonth() + 1];
        return `${d.getDate()}th ${name} of ${d.getFullYear()}`
    }

    async function setData() {
        const cityName = "Kottayam";

        const url = `https://api.openweathermap.org/data/2.5/weather?units=metrics&appid=${API_KEY}&q=${cityName}`
        await (await fetch(url)).json()
            .then(data => {
                // console.log(data)
                let stuff = {
                    "condition": data.weather['0']['description'],
                    "weather": data.name,
                    "temp": `${Math.round(data.main.temp - 273)} ℃ `
                };

                // setStuff({
                //     "condition": 'Overly cloud',
                //     "weather": 'Clouds',
                //     "temp": '36℃ '
                // })
                setStuff(stuff)
            })
    }
    useEffect(() => {
    setData()

    },[])

    return (<div className="container">
        <div className='title-wrapper'>
            <h3>Todays</h3>
            <h2>Forecast</h2>
        </div>
        <div className="date">{getTodaysDate()}</div>
        <img src="/src/assets/clouds.gif" alt="" className='weather-status-img' />
        <div className="location"><i className="fa fa-location-arrow" aria-hidden="true"></i> {stuff.weather}</div>
        <div className="weather-box">
            <div className="temp">{stuff.temp}</div>
            <div className="weather">{stuff.condition}</div>
        </div>
        <div className="alert-container">
            <Alert myclassName="orange-alert" />
            <Alert myclassName="red-alert" />
            <Alert myclassName="orange-alert" />
            <Alert myclassName="orange-alert" />
        </div>
    </div>
    )
}

export default Weather
