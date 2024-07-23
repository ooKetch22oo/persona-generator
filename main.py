import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from persona_generator import generate_personas

def scrape_website(url: str) -> str:
    """
    Scrape the content of a given URL.
    
    Args:
    url (str): The URL of the website to scrape.
    
    Returns:
    str: The text content of the website.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def main():
    # Load environment variables (including API keys)
    load_dotenv()
    
    # Get user input for the website URL
    url = input("Enter the website URL to generate personas from: ")
    
    # Scrape the website content
    scraped_text = scrape_website(url)
    
    # Generate personas based on the scraped content
    print("\nGenerating personas...")
    personas = generate_personas(scraped_text)
    
    # Output the generated personas
    print("\nGeneration complete. Displaying personas:")
    for i, persona in enumerate(personas, 1):
        print(f"\n\n--- Persona {i} ---")
        print(persona)

if __name__ == "__main__":
    main()
