# EduMind – AI Learning Assistant

A small Flask web app for students. It uses the Gemini API to explain topics in simple language.

## Run locally
1. Install Python 3.10+.
2. In this folder run: `pip install -r requirements.txt`
3. Set your Gemini API key as an environment variable named `GEMINI_API_KEY`.
4. Run: `python app.py`
5. Open `http://localhost:8080`.

## Deploy to Google Cloud Run
1. Push `app.py`, `requirements.txt`, and `Dockerfile` to a public GitHub repository.
2. In Google Cloud Console, create/select a project and enable billing only after reviewing possible charges.
3. Deploy the repository to Cloud Run using the Dockerfile.
4. In the Cloud Run service configuration, add `GEMINI_API_KEY` as an environment variable or secret. Never commit the key to GitHub.
5. Deploy and open the service URL. Test the learning form.

## Important
The app needs a valid Gemini API key to generate AI answers. Without it, the website still loads but clearly reports that AI is not configured. Do not claim the AI feature works until you have tested it.
