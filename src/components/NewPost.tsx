import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API_URL } from '../config';
import './NewPost.css';

const NewPost = () => {
    const navigate = useNavigate();
    const [author, setAuthor] = useState('');
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [formError, setFormError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    async function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!author.trim() || !title.trim() || !description.trim()) {
            setFormError('Author, title and description are all required.');
            return;
        }
        try {
            setSubmitting(true);
            setFormError(null);
            const res = await fetch(`${API_URL}/community/new`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ author: author.trim(), title: title.trim(), description: description.trim() }),
            });
            if (!res.ok) {
                const body = await res.json().catch(() => ({}));
                throw new Error((body as { error?: string }).error || `Submit failed (${res.status})`);
            }
            navigate('/community');
        } catch (err) {
            setFormError((err as Error).message);
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <div className="container">
            <h3>Add new post</h3>
            <form onSubmit={onSubmit}>
                <label>
                    Your name ({author.length}/80)
                    <input placeholder="Your name" name="author" aria-label="Author" className="title" value={author} onChange={(e) => setAuthor(e.target.value)} maxLength={80} required />
                </label>
                <label>
                    Title ({title.length}/200)
                    <input placeholder="Title" name="title" aria-label="Title" className="title" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
                </label>
                <label>
                    Description ({description.length}/2000)
                    <textarea placeholder="Description" name="description" aria-label="Description" className="description" value={description} onChange={(e) => setDescription(e.target.value)} maxLength={2000} rows={5} required />
                </label>
                {formError && <p role="alert">{formError}</p>}
                <div className="actions">
                    <button type="submit" disabled={submitting}>{submitting ? 'Submitting...' : 'Submit'}</button>
                    <Link to="/community">Cancel</Link>
                </div>
            </form>
        </div>
    )
}

export default NewPost
