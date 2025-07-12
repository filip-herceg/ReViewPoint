import React, { useState } from "react";
import { useUploadStore } from "@/lib/store/uploadStore";
import { getErrorMessage } from "@/lib/utils/errorHandling";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload } from "lucide-react";

const initialState = { name: "", status: "pending", progress: 0 };

const UploadForm: React.FC = () => {
  const [form, setForm] = useState(initialState);
  const { createUpload, loading, error } = useUploadStore();
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    try {
      await createUpload({ ...form, status: "pending", progress: 0 });
      setForm(initialState);
    } catch (err) {
      setLocalError(getErrorMessage(err));
    }
  };

  return (
    <Card className="bg-background border border-border hover-lift">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-foreground">
          <Upload className="h-5 w-5 text-primary" />
          Upload Document
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          Add a new document to the review system
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="upload-name" className="text-foreground">
              File Name
            </Label>
            <Input
              id="upload-name"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Enter document name..."
              required
            />
          </div>

          <div className="flex gap-2">
            <Button
              type="submit"
              className="flex-1 group hover-lift"
              disabled={loading || !form.name}
            >
              {loading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-transparent border-t-primary" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4 text-primary transition-transform group-hover:scale-110" />
                  Add Upload
                </>
              )}
            </Button>
          </div>

          {(error || localError) && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20">
              <p className="text-sm text-destructive-foreground">
                Error: {getErrorMessage(error || localError)}
              </p>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
};

export default UploadForm;
