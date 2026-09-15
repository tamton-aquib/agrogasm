import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_URL, getWeatherCity, timeAgo } from '../config';
import type { CommunityData, ReliabilityFilter, SortMode } from '../types';
import './Community.css';

const EMPTY: CommunityData = {
    posts: [],
    global: { threshold: 10 },
};
const PAGE_SIZE = 20;

function normalizeComments(post: unknown) {
    const p = post as Record<string, unknown>;
    const c = p['comments'];
    if (Array.isArray(c)) return c as CommunityData['posts'][number]['comments'];
    if (c && typeof c === 'object') return [c as CommunityData['posts'][number]['comments'][number]];
    return [];
}

const Community = () => {
    const [city] = useState(getWeatherCity());
    const [data, setData] = useState<CommunityData>(EMPTY);
    const [total, setTotal] = useState(0);
    const [offset, setOffset] = useState(0);
    const [loading, setLoading] = useState(true);
    const [queryError, setQueryError] = useState<string | null>(null);
    const [votingId, setVotingId] = useState<number | null>(null);

    const [q, setQ] = useState('');
    const [sort, setSort] = useState<SortMode>('new');
    const [relFilter, setRelFilter] = useState<ReliabilityFilter>('');

    const [openCommentPid, setOpenCommentPid] = useState<number | null>(null);
    const [commentAuthor, setCommentAuthor] = useState('');
    const [commentText, setCommentText] = useState('');
    const [commenting, setCommenting] = useState(false);

    const load = useCallback(async (signal?: AbortSignal) => {
        try {
            setLoading(true);
            setQueryError(null);
            const params = new URLSearchParams({
                limit: String(PAGE_SIZE),
                offset: String(offset),
                sort,
            });
            if (q.trim()) params.set('q', q.trim());
            if (relFilter) params.set('reliability', relFilter);
            const res = await fetch(`${API_URL}/?${params.toString()}`, { signal });
            if (!res.ok) throw new Error(`Server responded ${res.status}`);
            const json = await res.json();
            const raw = (json.data ?? json) as CommunityData;
            const posts = (raw.posts ?? []).map((p) => ({
                ...p,
                comments: normalizeComments(p),
            }));
            setData({ posts, global: raw.global ?? { threshold: 10 } });
            setTotal((json.meta?.total as number) ?? posts.length);
        } catch (err) {
            if ((err as Error).name !== 'AbortError') {
                setQueryError((err as Error).message || 'Failed to load posts');
            }
        } finally {
            setLoading(false);
        }
    }, [offset, q, sort, relFilter]);

    useEffect(() => {
        const controller = new AbortController();
        load(controller.signal);
        return () => controller.abort();
    }, [load]);

    function onSearch(e: React.FormEvent) {
        e.preventDefault();
        setOffset(0);
        load();
    }

    async function vote(pid: number, direction: 'up' | 'down') {
        const prev = data.posts;
        try {
            setVotingId(pid);
            setData((d) => ({
                ...d,
                posts: d.posts.map((p) =>
                    p.pid === pid
                        ? { ...p, upvote: p.upvote + (direction === 'up' ? 1 : 0), downvote: p.downvote + (direction === 'down' ? 1 : 0) }
                        : p
                ),
            }));
            const res = await fetch(`${API_URL}/community/${pid}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction }),
            });
            if (!res.ok) throw new Error(`Vote failed (${res.status})`);
            const updated = await res.json();
            setData((d) => ({
                ...d,
                posts: d.posts.map((p) =>
                    p.pid === pid
                        ? { ...p, upvote: updated.upvote, downvote: updated.downvote, reliability: updated.reliability }
                        : p
                ),
            }));
        } catch (err) {
            setData((d) => ({ ...d, posts: prev }));
            setQueryError((err as Error).message);
        } finally {
            setVotingId(null);
        }
    }

    async function submitComment(pid: number) {
        if (!commentAuthor.trim() || !commentText.trim()) {
            setQueryError('Comment author and text are required.');
            return;
        }
        try {
            setCommenting(true);
            const res = await fetch(`${API_URL}/community/${pid}/comment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ author: commentAuthor.trim(), description: commentText.trim() }),
            });
            if (!res.ok) {
                const body = await res.json().catch(() => ({}));
                throw new Error((body as { error?: string }).error || `Comment failed (${res.status})`);
            }
            const body = await res.json();
            setData((d) => ({
                ...d,
                posts: d.posts.map((p) =>
                    p.pid === pid ? { ...p, comments: [...p.comments, body.comment] } : p
                ),
            }));
            setCommentAuthor('');
            setCommentText('');
            setOpenCommentPid(null);
        } catch (err) {
            setQueryError((err as Error).message);
        } finally {
            setCommenting(false);
        }
    }

    return (
        <div className="container">
            <h1>Posts</h1>
            <div className='main-grp-bg'>
                <h3 className="main-grp"><i className="fa fa-location-arrow" aria-hidden="true"></i> {city}</h3>
            </div>

            <form className="filters" onSubmit={onSearch}>
                <input
                    aria-label="Search posts"
                    placeholder="Search title, text, author"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    maxLength={100}
                />
                <select aria-label="Sort posts" value={sort} onChange={(e) => { setSort(e.target.value as SortMode); setOffset(0); }}>
                    <option value="new">Newest</option>
                    <option value="old">Oldest</option>
                    <option value="top">Top voted</option>
                </select>
                <select aria-label="Filter by reliability" value={relFilter} onChange={(e) => { setRelFilter(e.target.value as ReliabilityFilter); setOffset(0); }}>
                    <option value="">All reliability</option>
                    <option value="new">New</option>
                    <option value="reliable">Reliable</option>
                    <option value="unsure">Unsure</option>
                    <option value="unreliable">Unreliable</option>
                </select>
                <button type="submit">Search</button>
            </form>

            {queryError && <p role="alert">{queryError}</p>}
            {loading ? (
                <p>Loading posts...</p>
            ) : data.posts.length === 0 ? (
                <div>
                    <p>No posts yet. Be the first to share.</p>
                    {queryError && <p>Is the backend running at {API_URL}?</p>}
                </div>
            ) : (
                <>
                    {data.posts.map((post) =>
                        <article key={post.pid} className="card">
                            <div className="author">
                                <i className="fa fa-microphone" aria-hidden="true"></i> &nbsp; {post.author}
                                {post.created_at && <span className="time"> - {timeAgo(post.created_at)}</span>}
                            </div>
                            <span className='reliability'>{post.reliability}</span>
                            <div className="title">{post.title}</div>
                            <div className="description">{post.description}</div>
                            <span>
                                <button aria-label={`Upvote post ${post.pid}`} onClick={() => vote(post.pid, 'up')} disabled={votingId === post.pid}>
                                    <i className="fas fa-arrow-up">&nbsp;</i>
                                </button>
                                {post.upvote} &nbsp;
                                <button aria-label={`Downvote post ${post.pid}`} onClick={() => vote(post.pid, 'down')} disabled={votingId === post.pid}>
                                    <i className="fas fa-arrow-down">&nbsp;</i>
                                </button>
                                {post.downvote}
                            </span>
                            {post.comments.length > 0 && (
                                <div className="comments">
                                    {post.comments.map((c, i) => (
                                        <p key={c.id ?? i}>
                                            <strong>{c.author}:</strong> {c.description}
                                            {c.created_at && <span className="time"> ({timeAgo(c.created_at)})</span>}
                                        </p>
                                    ))}
                                </div>
                            )}
                            {openCommentPid === post.pid ? (
                                <div className="comment-form">
                                    <input
                                        aria-label="Comment author"
                                        placeholder="Your name"
                                        value={commentAuthor}
                                        onChange={(e) => setCommentAuthor(e.target.value)}
                                        maxLength={80}
                                    />
                                    <input
                                        aria-label="Comment text"
                                        placeholder="Write a comment"
                                        value={commentText}
                                        onChange={(e) => setCommentText(e.target.value)}
                                        maxLength={1000}
                                    />
                                    <div>
                                        <button onClick={() => submitComment(post.pid)} disabled={commenting}>
                                            {commenting ? 'Posting...' : 'Post comment'}
                                        </button>
                                        <button type="button" onClick={() => setOpenCommentPid(null)}>Cancel</button>
                                    </div>
                                </div>
                            ) : (
                                <button onClick={() => setOpenCommentPid(post.pid)}>Comment</button>
                            )}
                        </article>
                    )}
                    <div className="pagination">
                        <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>Prev</button>
                        <span>{offset + 1}-{Math.min(offset + PAGE_SIZE, total)} of {total}</span>
                        <button disabled={offset + PAGE_SIZE >= total} onClick={() => setOffset(offset + PAGE_SIZE)}>Next</button>
                    </div>
                </>
            )}
            <Link to="/community/new" aria-label="Add new post">
                <div className="btn-new">
                    <i className="fa fa-plus" aria-hidden="true"></i>
                </div>
            </Link>
        </div>
    )
}

export default Community;
