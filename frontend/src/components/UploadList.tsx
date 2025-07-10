import React, { useEffect } from 'react'
import { useUploadStore } from '@/lib/store/uploadStore'
import { getErrorMessage } from '@/lib/utils/errorHandling'
import { createTestError } from '../../tests/test-templates'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { FileText, Edit, Trash2, Check, X, Clock, AlertCircle } from 'lucide-react'

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

    if (loading) {
        return (
            <Card className="bg-background border border-border">
                <CardContent className="flex items-center justify-center py-8">
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-transparent border-t-primary" />
                        Loading uploads...
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (error) {
        return (
            <Card className="bg-background border border-destructive/20">
                <CardContent className="flex items-center gap-2 py-4 text-destructive-foreground">
                    <AlertCircle className="h-4 w-4" />
                    Error: {getErrorMessage(error)}
                </CardContent>
            </Card>
        )
    }

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
        <Card className="bg-background border border-border">
            <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                    <FileText className="h-5 w-5 text-primary" />
                    Uploads
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                    Manage your uploaded documents
                </CardDescription>
            </CardHeader>
            <CardContent>
                {localError && (
                    <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20">
                        <p className="text-sm text-destructive-foreground flex items-center gap-2">
                            <AlertCircle className="h-4 w-4" />
                            Error: {localError}
                        </p>
                    </div>
                )}

                {uploads.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                        <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No uploads found.</p>
                        <p className="text-sm">Upload your first document to get started.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {uploads.map((u) => (
                            <div key={u.id} className="p-4 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors border border-border/50">
                                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                                    <div className="flex-1 space-y-2">
                                        {editId === u.id ? (
                                            <div className="flex gap-2">
                                                <Input
                                                    value={editName}
                                                    onChange={e => setEditName(e.target.value)}
                                                    disabled={loading}
                                                    className="flex-1"
                                                />
                                                <Button
                                                    size="sm"
                                                    onClick={() => saveEdit(u.id)}
                                                    disabled={loading}
                                                    className="hover-lift"
                                                >
                                                    <Check className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={cancelEdit}
                                                    disabled={loading}
                                                >
                                                    <X className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        ) : (
                                            <h4 className="font-medium text-foreground">{u.name}</h4>
                                        )}

                                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                            <div className="flex items-center gap-1">
                                                <Badge variant={u.status === 'pending' ? 'secondary' : 'default'}>
                                                    {u.status}
                                                </Badge>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <Clock className="h-3 w-3 text-muted-foreground" />
                                                Progress: {u.progress}%
                                            </div>
                                        </div>
                                    </div>

                                    {editId !== u.id && (
                                        <div className="flex gap-2">
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => startEdit(u)}
                                                disabled={loading}
                                                className="hover-lift"
                                            >
                                                <Edit className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleDelete(u.id)}
                                                disabled={loading}
                                                className="hover-lift text-destructive-foreground hover:text-destructive"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

export default UploadList
