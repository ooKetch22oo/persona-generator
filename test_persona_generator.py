import unittest
from unittest.mock import patch, MagicMock
from persona_generator import generate_personas, call_openai, evaluate_personas

class TestPersonaGenerator(unittest.TestCase):

    @patch('persona_generator.FusionChain.run')
    @patch('persona_generator.client.chat.completions.create')
    def test_generate_personas(self, mock_create, mock_run):
        # Mock the FusionChain.run method
        mock_run.return_value = MagicMock(
            all_prompt_responses=[
                ['{"name": "John Doe"}', '{"name": "John Doe", "age": 30}', '{"name": "John Doe", "age": 30, "habits": {}}', '{"name": "John Doe", "age": 30, "habits": {}, "insights": {}}', "A day in John's life..."],
                ['{"name": "Jane Smith"}', '{"name": "Jane Smith", "age": 25}', '{"name": "Jane Smith", "age": 25, "habits": {}}', '{"name": "Jane Smith", "age": 25, "habits": {}, "insights": {}}', "A day in Jane's life..."],
            ],
            performance_scores=[0.9, 0.8]
        )

        # Mock the OpenAI API call for evaluate_personas
        mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='[0.9, 0.8]'))])

        result = generate_personas("Sample website content")

        self.assertEqual(len(result), 4)  # Now expecting 4 personas
        self.assertIn("John Doe", result[0])
        self.assertIn("Jane Smith", result[1])

    @patch('persona_generator.client.chat.completions.create')
    def test_call_openai(self, mock_create):
        mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='{"name": "Test Persona"}'))])

        result = call_openai("analytical", "Generate a persona")

        self.assertEqual(result, '{"name": "Test Persona"}')
        mock_create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are creating a analytical persona based on website content."},
                {"role": "user", "content": "Generate a persona"}
            ],
            temperature=0.7,
        )

    @patch('persona_generator.client.chat.completions.create')
    def test_evaluate_personas(self, mock_create):
        mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='[0.8, 0.9]'))])

        personas = ['{"name": "John"}', '{"name": "Jane"}']
        top_response, scores = evaluate_personas(personas)

        self.assertEqual(top_response, '{"name": "Jane"}')
        self.assertEqual(scores, [0.8, 0.9])
        mock_create.assert_called_once()

if __name__ == '__main__':
    unittest.main()
