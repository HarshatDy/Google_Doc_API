# Google Doc to HTML Converter

This Python script fetches content from Google Docs using the Google Docs API and converts it to structured pages using Google's Gemini API.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Docs API**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Docs API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file and save it as `credentials.json` in the project directory

3. **Set up Gemini API**:
   - Go to the [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Create a `.env` file in the project directory with the following content:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Usage

Run the script with the following command:

```bash
python gemini_doc_fetch.py --doc_id YOUR_DOCUMENT_ID --output output.html
```

Parameters:
- `--doc_id`: The ID of the Google Document (required)
  - You can find this in the URL of your Google Doc: `https://docs.google.com/document/d/YOUR_DOCUMENT_ID/edit`
- `--output`: Path to save the HTML output (optional)
- `--credentials`: Path to the credentials.json file (default: credentials.json)

## Example

```bash
python gemini_doc_fetch.py --doc_id 1AbCdEfGhIjKlMnOpQrStUvWxYz12345 --output blog_post.html
```

## Features

- Authenticates with Google Docs API
- Fetches document content
- Uses Gemini AI to convert the document to structured HTML
- Saves the HTML output to a file or prints it to the console

## Notes

- The first time you run the script, it will open a browser window to authenticate with Google
- The authentication token will be saved for future use
- The Gemini API is used to intelligently convert the document content to HTML 