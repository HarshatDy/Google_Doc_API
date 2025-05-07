from gemini_doc_fetch import GeminiDocFetch

def main():
    # Initialize the GeminiDocFetch class
    doc_fetcher = GeminiDocFetch(credentials_path='credentials.json')
    
    # Example document ID (replace with your actual document ID)
    document_id = "1AbCdEfGhIjKlMnOpQrStUvWxYz12345"
    
    # Fetch and convert the document
    html_content = doc_fetcher.fetch_and_convert(
        document_id=document_id,
        output_path="blog_post.html"
    )
    
    print(f"Document successfully converted to HTML and saved to blog_post.html")
    
    # If you want to process the HTML content further, you can do so here
    # For example, you could add custom CSS, modify the HTML, etc.
    
if __name__ == "__main__":
    main() 