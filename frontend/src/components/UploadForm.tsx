import React, { useState } from 'react'
import { useUploadStore } from '@/lib/store/uploadStore'

const initialState = { name: '', status: 'pending', progress: 0 }

const UploadForm: React.FC = () => {
    const [form, setForm] = useState(initialState)
    const { createUpload, loading, error } = useUploadStore()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        await createUpload({ ...form, status: 'pending', progress: 0 })
        setForm(initialState)
    }

    return (
        <form onSubmit={handleSubmit} className="mb-4 space-y-2">
            <div>
                <label className="block mb-1 font-medium">File Name</label>
                <input
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
            {error && <div className="text-red-600">Error: {error}</div>}
        </form>
    )
}

export default UploadForm
