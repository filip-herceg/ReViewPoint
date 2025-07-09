import React, { useState } from 'react'
import { useUploadStore } from '@/lib/store/uploadStore'
import { getErrorMessage } from '@/lib/utils/errorHandling'

const initialState = { name: '', status: 'pending', progress: 0 }

const UploadForm: React.FC = () => {
    const [form, setForm] = useState(initialState)
    const { createUpload, loading, error } = useUploadStore()
    const [localError, setLocalError] = useState<string | null>(null)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLocalError(null)
        try {
            await createUpload({ ...form, status: 'pending', progress: 0 })
            setForm(initialState)
        } catch (err) {
            setLocalError(getErrorMessage(err))
        }
    }

    return (
        <form onSubmit={handleSubmit} className="mb-4 space-y-2">
            <div>
                <label htmlFor="upload-name" className="block mb-1 font-medium">File Name</label>
                <input
                    id="upload-name"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    className="border rounded px-2 py-1 w-full"
                    required
                />
            </div>
            <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-1 rounded disabled:opacity-50"
                disabled={loading || !form.name}
            >
                {loading ? 'Uploading...' : 'Add Upload'}
            </button>
            {error && <div className="text-red-600">Error: {getErrorMessage(error)}</div>}
            {localError && <div className="text-red-600">Error: {localError}</div>}
        </form>
    )
}

export default UploadForm
