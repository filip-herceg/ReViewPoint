import React, { useEffect } from 'react'
import { useUploadStore } from '@/lib/store/uploadStore'
import { getErrorMessage } from '@/lib/utils/errorHandling'
import { createTestError } from '../../tests/test-templates'


interface UploadListProps {
    disableAutoFetch?: boolean
}

const UploadList: React.FC<UploadListProps> = ({ disableAutoFetch }) => {
    const { uploads, loading, error, fetchUploads, patchUpload, removeUpload } = useUploadStore()
    const [localError, setLocalError] = React.useState<string | null>(null)
    const [editId, setEditId] = React.useState<string | null>(null)
    const [editName, setEditName] = React.useState('')

    useEffect(() => {
        if (!disableAutoFetch) {
            fetchUploads()
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [disableAutoFetch])

    // Clear local error when store error changes or component unmounts
    useEffect(() => {
        if (localError) {
            setLocalError(null)
        }
    }, [])

    if (loading) return <div>Loading uploads...</div>
    if (error) return <div className="text-red-600">Error: {getErrorMessage(error)}</div>

    const startEdit = (u: typeof uploads[number]) => {
        setEditId(u.id)
        setEditName(u.name)
    }
    const cancelEdit = () => {
        setEditId(null)
        setEditName('')
        setLocalError(null)
    }
    const saveEdit = async (id: string) => {
        setLocalError(null)
        try {
            await patchUpload(id, { name: editName })
            cancelEdit()
        } catch (err) {
            // Use createTestError for demonstration/testing if needed
            const errorObj = err instanceof Error ? err : createTestError('Patch failed');
            setLocalError(getErrorMessage(errorObj));
        }
    }

    const handleDelete = async (id: string) => {
        setLocalError(null)
        try {
            await removeUpload(id)
        } catch (err) {
            // Use createTestError for demonstration/testing if needed
            const errorObj = err instanceof Error ? err : createTestError('Delete failed');
            setLocalError(getErrorMessage(errorObj));
        }
    }

    return (
        <div>
            <h2 className="text-lg font-bold mb-2">Uploads</h2>
            {localError && (
                <div className="text-red-600 mb-2">Error: {localError}</div>
            )}
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
                                        <button className="bg-red-600 text-white px-2 py-1 rounded" onClick={() => handleDelete(u.id)} disabled={loading}>Delete</button>
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
