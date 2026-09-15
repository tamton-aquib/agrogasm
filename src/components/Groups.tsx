import React, { useState } from 'react';

interface Group {
    id: number;
    name: string;
    description?: string;
}

const Groups = () => {
    const [groups, setGroups] = useState<Group[]>([]);
    const [loading, setLoading] = useState(false);
    const [name, setName] = useState('');
    const [error, setError] = useState<string | null>(null);

    async function loadGroups() {
        try {
            setLoading(true);
            const res = await fetch('/api/groups');
            if (!res.ok) throw new Error('Failed to load groups');
            const data = await res.json();
            setGroups(data.groups);
        } catch (err) {
            setError((err as Error).message);
        } finally {
            setLoading(false);
        }
    }

    async function createGroup(e: React.FormEvent) {
        e.preventDefault();
        if (!name.trim()) return;
        try {
            const res = await fetch('/api/groups/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name.trim() }),
            });
            if (!res.ok) throw new Error('Failed to create group');
            setName('');
            await loadGroups();
        } catch (err) {
            setError((err as Error).message);
        }
    }

    return (
        <div className="container">
            <h2>Groups</h2>
            <form onSubmit={createGroup}>
                <input
                    placeholder="Group name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
                <button type="submit">Create</button>
            </form>
            {error && <div className="error">{error}</div>}
            {loading ? <div>Loading...</div> : (
                <div className="group-list">
                    {groups.map(g => (
                        <div key={g.id} className="group-item">
                            <h3>{g.name}</h3>
                            <p>{g.description}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Groups;
