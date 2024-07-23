# AI-Powered User Persona Generator

## Overview

This application is an AI-powered tool that generates detailed user personas based on website content. It uses GPT-4 to create multiple persona profiles and then selects the top 4 most relevant personas for the given website. This tool is invaluable for marketers, UX designers, and product managers who need to understand their target audience better.

## Features

- Web scraping functionality to extract content from any given URL
- Utilizes OpenAI's GPT-4 model to generate realistic and diverse user personas
- Implements a 5-part prompt chain to create comprehensive persona profiles
- Generates 8 initial personas and selects the top 4 based on relevance and suitability
- Each persona includes:
  - Basic information (name, age, gender, ethnicity, location, occupation, income, education)
  - Psychographics (values, beliefs, challenges, needs, frustrations, goals, behaviors)
  - Habits (preferred brands, purchases, lifestyle, interests, media consumption)
  - Flashmark.insights (decision-making process, metrics for success)
  - "A Day in the Life" narrative

## Requirements

- Python 3.7+
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-persona-generator.git
   cd ai-persona-generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the main script:
   ```
   python main.py
   ```

2. When prompted, enter the URL of the website you want to generate personas for.

3. The script will scrape the website, generate personas, and display the top 4 personas in the console.

## Project Structure

- `main.py`: The entry point of the application. Handles user input and orchestrates the overall process.
- `persona_generator.py`: Contains the logic for generating and evaluating personas using GPT-4.
- `chain.py`: Implements the FusionChain and MinimalChainable classes for managing the prompt chain and persona generation process.
- `requirements.txt`: Lists all the Python packages required for this project.

## How It Works

1. The app scrapes the content from the provided website URL.
2. It generates 8 initial personas using different "seed" personalities (analytical, creative, practical, enthusiastic, ambitious, cautious, social, innovative).
3. For each persona, it uses a 5-part prompt chain to generate detailed information.
4. The generated personas are evaluated based on their relevance and suitability for the website.
5. The top 4 personas are selected and returned as the final output.

## Customization

You can customize the persona generation process by modifying the prompts in the `generate_personas` function within `persona_generator.py`. You can also adjust the number of initial personas generated or the number of top personas selected.

## Limitations

- The quality of the generated personas depends on the quality and relevance of the website content.
- The app requires an active internet connection and a valid OpenAI API key.
- Extensive use may result in significant API costs due to the use of GPT-4.

## Contributing

Contributions to improve the app are welcome. Please feel free to submit issues or pull requests.

## Testing

To run the unit tests for this project, use the following command:

```
python -m unittest test_persona_generator.py
```

Make sure you have all the required dependencies installed before running the tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- The developers of the libraries used in this project (requests, beautifulsoup4, python-dotenv, pydantic)
