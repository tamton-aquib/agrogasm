import { useEffect, useState } from 'react';
import './Community.css';

const dummy = {
    "posts": [],
    "global": {
        "threshold": 0
    }
}

const Community = () => {
    const [stuff, setStuff] = useState(dummy);

    async function setData() {
        const url = "http://127.0.0.1:5000/";
        await (await fetch(url)).json()
            .then(data => {
                setStuff(data.data);
            })
    }
    useEffect(() => {
        setData();
    }, []);

    return (
        <div className='container'>
            <h1>Posts</h1>
            {stuff.posts.map((post) =>
                <div key={post.pid} className="card">
                    <div className="author">
                        {post.author}
                    </div>
                    <div className="title">
                        {post.title}
                    </div>
                    <div className="description">
                        {post.description}
                    </div>
                    <span>
                        <i className="fas fa-arrow-up    ">&nbsp;</i>
                        {post.upvote} &nbsp;
                        <i className="fas fa-arrow-up    ">&nbsp;</i>
                        {post.downvote}
                    </span>
                </div>
            )}
        </div>
    )
}

export default Community;
