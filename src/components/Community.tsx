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

    // const reliability = (post: { upvote: number, downvote: number }) => {
    // let rel: string;
    // let total = post.upvote + post.downvote;
    // let avg = post.upvote / post.downvote;
    // console.log(avg);

    // if (total >= stuff.global.threshold) {
    // if (avg >= 70) {
    // rel = "reliable";
    // } else if (avg >= 50) {
    // rel = "unsure"
    // } else {
    // rel = "unreliable"
    // }
    // } else {
    // rel = "new!"
    // }
    // return rel
    // }

    return (
        <div className='container'>
            <h1>Posts</h1>
            {stuff.posts.map((post) =>
                <div key={post.pid} className="card">
                    <div className="author">
                        {post.author}
                    </div>
                    <span>{post.reliability}</span>
                    <div className="title">
                        {post.title}
                    </div>
                    <div className="description">
                        {post.description}
                    </div>
                    <span>
                        <i className="fas fa-arrow-up    ">&nbsp;</i>
                        {post.upvote} &nbsp;
                        <i className="fas fa-arrow-down    ">&nbsp;</i>
                        {post.downvote}
                    </span>
                </div>
            )}
        </div>
    )
}

export default Community;
