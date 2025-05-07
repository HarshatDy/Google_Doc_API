import os
import io
import json
from typing import Optional, Dict, Any, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv
import time
from datetime import datetime

class GeminiDocFetch:
    """Class to fetch Google Docs and convert them to structured JSON format."""
    
    # If modifying these scopes, delete the token.json file.
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize the GeminiDocFetch class.
        
        Args:
            credentials_path: Path to the credentials.json file
            token_path: Path to store the token.json file
        """
        load_dotenv()  # Load environment variables from .env file
        
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.docs_service = None
        self.gemini_model = None
        
        # Initialize Gemini API
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    
    def init_google_docs_api(self) -> None:
        """Initialize the Google Docs API connection."""
        creds = None
        
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                json.load(open(self.token_path)), self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.docs_service = build('docs', 'v1', credentials=creds)
    
    def fetch_document(self, document_id: str) -> Dict[str, Any]:
        """
        Fetch a Google Doc by its ID.
        
        Args:
            document_id: The ID of the document to fetch
            
        Returns:
            The document content as a dictionary
        """
        if not self.docs_service:
            self.init_google_docs_api()
        
        # Call the Docs API
        document = self.docs_service.documents().get(documentId=document_id).execute()
        return document
    
    def convert_to_json(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a Google Doc to structured JSON format.
        
        Args:
            document: The document content as returned by the Google Docs API
            
        Returns:
            Structured JSON content as a dictionary
        """
        if not self.gemini_model:
            raise ValueError("Gemini API not initialized")
        
        # Extract the title and content from the document
        title = document.get('title', 'Untitled Document')
        
        # Extract text content from the document
        content = ""
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for paragraph_element in element['paragraph'].get('elements', []):
                    if 'textRun' in paragraph_element:
                        content += paragraph_element['textRun'].get('content', '')
        
        # Prepare the prompt for Gemini
        prompt = f"""
        Convert the following Google Doc content into a structured JSON format with the following structure:
        {{
            "slug": "generate-a-url-friendly-slug-from-title",
            "title": "Document Title",
            "category": "Main Category",
            "author": "Author Name",
            "date": "Current Date",
            "readTime": "Estimated Read Time",
            "tags": ["Relevant", "Tags", "From", "Content"],
            "heroImage": "/placeholder.svg?height=600&width=1200",
            "excerpt": "Brief summary of the content",
            "content": [
                {{
                    "type": "paragraph|heading|image|code",
                    "content": "Content text",
                    "url": "Image URL (for image type)",
                    "caption": "Image caption (for image type)",
                    "language": "Programming language (for code type)"
                }}
            ]
        }}

        Document Title: {title}
        
        Document Content:
        {content}
        
        Return only the JSON structure without any explanation.
        """
        
        # Generate JSON using Gemini
        response = self.gemini_model.generate_content(prompt)
        json_content = response.text
        
        # Clean up the response if it contains markdown code blocks
        if "```json" in json_content:
            json_content = json_content.split("```json")[1].split("```")[0].strip()
        elif "```" in json_content:
            json_content = json_content.split("```")[1].split("```")[0].strip()
        
        # Parse the JSON string to a dictionary
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Gemini response as JSON")
    
    def fetch_and_convert(self, document_id: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch a Google Doc and convert it to structured JSON.
        
        Args:
            document_id: The ID of the document to fetch
            output_path: Optional path to save the JSON output
            
        Returns:
            Structured JSON content as a dictionary
        """
        document = self.fetch_document(document_id)
        json_content = self.convert_to_json(document)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_content, f, indent=2)
            print(f"JSON content saved to {output_path}")
        
        return json_content


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch Google Doc and convert to structured JSON')
    parser.add_argument('--doc_id', required=True, help='Google Document ID')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--credentials', default='credentials.json', help='Path to credentials.json file')
    
    args = parser.parse_args()
    
    doc_fetcher = GeminiDocFetch(credentials_path=args.credentials)
    json_content = doc_fetcher.fetch_and_convert(args.doc_id, args.output)
    
    if not args.output:
        print(json.dumps(json_content, indent=2))

    # Save with timestamp
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    with open(f"output_{timestamp}.json", "w") as f:
        json.dump(json_content, f, indent=2)
    
