import React, { useEffect } from 'react'
import { useUploadStore } from '@/lib/store/uploadStore'


interface UploadListProps {
    disableAutoFetch?: boolean
}

const UploadList: React.FC<UploadListProps> = ({ disableAutoFetch }) => {
    const { uploads, loading, error, fetchUploads, patchUpload, removeUpload } = useUploadStore()

    useEffect(() => {
        if (!disableAutoFetch) {
            fetchUploads()
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [disableAutoFetch])

    if (loading) return <div>Loading uploads...</div>
    if (error) return <div className="text-red-600">Error: {error}</div>

    const [editId, setEditId] = React.useState<string | null>(null)
    const [editName, setEditName] = React.useState('')

    const startEdit = (u: typeof uploads[number]) => {
        setEditId(u.id)
        setEditName(u.name)
    }
    const cancelEdit = () => {
        setEditId(null)
        setEditName('')
    }
    const saveEdit = async (id: string) => {
        await patchUpload(id, { name: editName })
        cancelEdit()
    }

    return (
        <div>
            <h2 className="text-lg font-bold mb-2">Uploads</h2>
            {uploads.length === 0 ? (
                <div>No uploads found.</div>
            ) : (
                <ul className="space-y-2">
                    {uploads.map((u) => (
                        <li key={u.id} className="border p-2 rounded flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                            <div className="flex-1">
                                {editId === u.id ? (
                                    <input
                                        className="border rounded px-2 py-1 mr-2"
                                        value={editName}
                                        onChange={e => setEditName(e.target.value)}
                                        disabled={loading}
                                    />
                                ) : (
                                    <strong>{u.name}</strong>
                                )}
                                <div>Status: {u.status}</div>
                                <div>Progress: {u.progress}%</div>
                                <div>Created: {u.createdAt}</div>
                            </div>
                            <div className="flex gap-2">
                                {editId === u.id ? (
                                    <>
                                        <button className="bg-green-600 text-white px-2 py-1 rounded" onClick={() => saveEdit(u.id)} disabled={loading || !editName}>Save</button>
                                        <button className="bg-gray-400 text-white px-2 py-1 rounded" onClick={cancelEdit} disabled={loading}>Cancel</button>
                                    </>
                                ) : (
                                    <>
                                        <button className="bg-blue-600 text-white px-2 py-1 rounded" onClick={() => startEdit(u)} disabled={loading}>Edit</button>
                                        <button className="bg-red-600 text-white px-2 py-1 rounded" onClick={() => removeUpload(u.id)} disabled={loading}>Delete</button>
                                    </>
                                )}
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}

export default UploadList
