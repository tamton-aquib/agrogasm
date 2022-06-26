import { useEffect, useState } from 'react';
import './Community.css';

const Community = () => {
    const [stuff, setStuff] = useState("");

    async function setData() {
        const url = "http://127.0.0.1:5000/";
        // await (await fetch(url)).text()
        // .then((data) => setStuff(data));
        await (await fetch(url)).json()
            .then(data => {
                setStuff("Noice");
            })
    }

    useEffect(() => {
        setData();
    });

    return (
        <>
            <h1>Nice</h1>
            {stuff}
        </>
    )
}

export default Community;
