import os
from dotenv import load_dotenv
import requests
import base64
from typing import Optional, Dict, List
from PIL import Image
import io

load_dotenv()


class InvoiceExtractor:
    """Extract text from invoices using Google Cloud Vision API REST."""
    
    def __init__(self, api_key: Optional[str] = None):
        
        self.api_key = api_key or os.getenv('GOOGLE_CLOUD_VISION_API_KEY')
        if not self.api_key:
            raise ValueError("Google Cloud Vision API key not found. Set GOOGLE_CLOUD_VISION_API_KEY in .env file or pass api_key parameter.")
        
        self.base_url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, any]:
        
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image_base64 = base64.b64encode(content).decode('utf-8')
            
            request_body = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [{"type": "TEXT_DETECTION"}]
                }]
            }
            
            response = requests.post(self.base_url, json=request_body)
            response.raise_for_status()
            
            data = response.json()
            
            if 'responses' in data and data['responses']:
                annotations = data['responses'][0].get('textAnnotations', [])
                
                result = {
                    'full_text': annotations[0]['description'] if annotations else '',
                    'text_blocks': [],
                    'success': True
                }
                
                for annotation in annotations[1:]:
                    result['text_blocks'].append({
                        'text': annotation['description'],
                        'bounding_box': annotation.get('boundingPoly', {})
                    })
                
                return result
            else:
                return {'error': 'No text found in image', 'success': False}
            
        except FileNotFoundError:
            return {'error': f'Image file not found: {image_path}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def extract_text_from_url(self, image_url: str) -> Dict[str, any]:

        try:
            request_body = {
                "requests": [{
                    "image": {"source": {"imageUri": image_url}},
                    "features": [{"type": "TEXT_DETECTION"}]
                }]
            }
            
            response = requests.post(self.base_url, json=request_body)
            response.raise_for_status()
            
            data = response.json()
            
            if 'responses' in data and data['responses']:
                annotations = data['responses'][0].get('textAnnotations', [])
                
                result = {
                    'full_text': annotations[0]['description'] if annotations else '',
                    'text_blocks': [],
                    'success': True
                }
                
                for annotation in annotations[1:]:
                    result['text_blocks'].append({
                        'text': annotation['description'],
                        'bounding_box': annotation.get('boundingPoly', {})
                    })
                
                return result
            else:
                return {'error': 'No text found in image', 'success': False}
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def extract_document_text(self, image_path: str) -> Dict[str, any]:
      
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image_base64 = base64.b64encode(content).decode('utf-8')
            
            request_body = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
                }]
            }
            
            response = requests.post(self.base_url, json=request_body)
            response.raise_for_status()
            
            data = response.json()
            
            if 'responses' in data and data['responses']:
                full_text_annotation = data['responses'][0].get('fullTextAnnotation', {})
                
                result = {
                    'full_text': full_text_annotation.get('text', ''),
                    'pages': [],
                    'success': True
                }
                
                for page in full_text_annotation.get('pages', []):
                    page_data = {
                        'width': page.get('width', 0),
                        'height': page.get('height', 0),
                        'blocks': []
                    }
                    
                    for block in page.get('blocks', []):
                        block_text = ''
                        for paragraph in block.get('paragraphs', []):
                            for word in paragraph.get('words', []):
                                word_text = ''.join([symbol.get('text', '') for symbol in word.get('symbols', [])])
                                block_text += word_text + ' '
                        
                        page_data['blocks'].append({
                            'text': block_text.strip(),
                            'confidence': block.get('confidence', 0)
                        })
                    
                    result['pages'].append(page_data)
                
                return result
            else:
                return {'error': 'No text found in document', 'success': False}
            
        except FileNotFoundError:
            return {'error': f'Image file not found: {image_path}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}


def main():
    """Example usage of the InvoiceExtractor class."""
    # Initialize extractor
    # Option 1: Use environment variable GOOGLE_CLOUD_VISION_API_KEY (from .env file)
    extractor = InvoiceExtractor()
    
    # Option 2: Provide API key directly
    # extractor = InvoiceExtractor(api_key='your-api-key-here')
    
    # Example: Extract text from local image
    # image_path = 'path/to/invoice.jpg'
    # result = extractor.extract_text_from_image(image_path)
    
    # if result['success']:
    #     print("Extracted Text:")
    #     print(result['full_text'])
    #     print(f"\nFound {len(result['text_blocks'])} text blocks")
    # else:
    #     print(f"Error: {result['error']}")
    
    # Example: Extract text from URL
    image_url = 'https://uniformsoftware.com/template/screenshots/wholesale-produce-distributor-invoice.webp'
    result = extractor.extract_text_from_url(image_url)
    if result['success']:
        print("Extracted Text:")
        print(result['full_text'])
        print(f"\nFound {len(result['text_blocks'])} text blocks")
    else:
        print(f"Error: {result['error']}")
    
    # Example: Extract document text (better for invoices with dense text)
    # result = extractor.extract_document_text(image_path)


if __name__ == '__main__':
    main()
