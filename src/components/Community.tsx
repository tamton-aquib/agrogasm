import { useEffect, useState } from 'react';
import './Community.css';

const Community = () => {
    const [stuff, setStuff] = useState();

    async function setData() {
        const url = "https://127.0.0.1:5000/";
        await (await fetch(url)).json()
            .then(data => {
                console.log(data);
                setStuff(JSON.parse(data));
            })
    }

    useEffect(() => {
        setData();
    });

    return (
        <>
            <div className="nice">{stuff.nice}</div>
            <h1>Nice</h1>
        </>
    )
}

export default Community;
