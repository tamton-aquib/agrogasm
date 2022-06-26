import './NewPost.css';
const NewPost = () => {

    return (
        <div className="container">
            <h3>Add new post</h3>
            <form>
                <input placeholder="Title" name="title" className="title" />
                <input placeholder="Description" className="description" />

                <button>Submit</button>
            </form>
            
        </div>

    )
}

export default NewPost
