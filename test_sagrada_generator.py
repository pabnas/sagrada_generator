
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from sagrada_generator import CardGenerator

class TestCardGenerator(unittest.TestCase):
    def setUp(self):
        self.assets_dir = 'assets'
        self.font_path = 'georgia.ttf'
        self.output_path = 'sagrada_output'
        self.card_file = 'card.txt'
        self.generator = CardGenerator(self.assets_dir, self.font_path, self.output_path, self.card_file)

    @patch('sagrada_generator.Image')
    @patch('sagrada_generator.ImageDraw')
    @patch('sagrada_generator.ImageFont')
    @patch('builtins.open', new_callable=mock_open, read_data="Card Label\n5\nRGBRY\nRGBRY\nRGBRY\nRGBRY\noutput_filename\n")
    @patch('os.makedirs')
    @patch('os.path.join')
    def test_create_card(self, mock_path_join, mock_makedirs, mock_file, mock_font, mock_draw, mock_image):
        # Setup mocks
        mock_image.new.return_value = MagicMock()
        mock_image.open.return_value.__enter__.return_value = MagicMock()
        mock_image.open.return_value.__enter__.return_value.size = (100, 100)
        
        mock_font.truetype.return_value = MagicMock()
        mock_draw_instance = mock_draw.Draw.return_value
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 50) # left, top, right, bottom

        # Run the method
        mock_file.return_value.readline.side_effect = [
            "Card Label\n", # For generate_cards
            "1\n",          # total_balls
            "RGBRY\n",      # row 1
            "RGBRY\n",      # row 2
            "RGBRY\n",      # row 3
            "RGBRY\n",      # row 4
            "output_filename\n", # file_card_name
            ""              # next_label (empty to stop)
        ]

        self.generator.generate_cards()

        # Assertions
        mock_makedirs.assert_called_with(self.output_path, exist_ok=True)
        # Verify image creation and saving
        self.assertTrue(mock_image.new.called)
        self.assertTrue(mock_image.open.called)
        
        # Check if save was called on the image object
        mock_img_instance = mock_image.new.return_value
        # The code resizes the image which returns a NEW image instance
        mock_resized_img = mock_img_instance.resize.return_value
        mock_resized_img.save.assert_called()
        
    @patch('sagrada_generator.Image')
    @patch('sagrada_generator.ImageDraw')
    @patch('sagrada_generator.ImageFont')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_generate_cards_minimal(self, mock_makedirs, mock_file, mock_font, mock_draw, mock_image):
        # Test with minimal valid file content
        mock_file.return_value.readline.side_effect = [
            "Card Label\n", # For generate_cards
            "0\n",          # total_balls (0 to minimize loop)
            "RGBRY\n",      # row 1
            "RGBRY\n",      # row 2
            "RGBRY\n",      # row 3
            "RGBRY\n",      # row 4
            "output_filename\n", # file_card_name
            ""              # next_label (empty to stop)
        ]
        
        # Mock textbbox for this test too
        mock_draw_instance = mock_draw.Draw.return_value
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 50)
        
        mock_image.new.return_value.resize.return_value = MagicMock()
        mock_image.open.return_value.__enter__.return_value.size = (100, 100)

        self.generator.generate_cards()
        mock_makedirs.assert_called()

if __name__ == '__main__':
    unittest.main()
