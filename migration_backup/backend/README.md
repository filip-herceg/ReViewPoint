# ...existing code...
4. **Configure environment variables** as needed (see `backend/.env.example` if available).

   - Copy `backend/.env.example` to `backend/.env` and fill in the required values for your environment.
   - The backend will automatically load variables from `.env` using [python-dotenv](https://pypi.org/project/python-dotenv/) and Pydantic Settings.
   - **Never commit your `.env` file to version control.**
   - For CI/CD, set environment variables as secrets in your pipeline or deployment platform.

   Example:
   ```powershell
   # In PowerShell, copy the example file
   Copy-Item backend/.env.example backend/.env
   # Then edit backend/.env to set your secrets and config
   ```

   See the comments in `.env.example` for descriptions of each variable.

   - Optional environment variables for storage (S3/MinIO), email (SMTP), and monitoring (Sentry, Loggly) are now mapped in the backend config for future use. See `.env.example` for details. You can access these via `settings.storage_url`, `settings.email_host`, etc.
# ...existing code...