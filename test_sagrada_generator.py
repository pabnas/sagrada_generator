import unittest
from unittest.mock import MagicMock, patch, mock_open
from sagrada_generator import CardGenerator

class TestCardGenerator(unittest.TestCase):
    def setUp(self):
        self.assets_dir = 'assets'
        self.font_path = 'georgia.ttf'
        self.output_path = 'sagrada_output'
        self.card_file = 'card.txt'
        self.generator = CardGenerator(self.assets_dir, self.font_path, self.output_path, self.card_file)

    # Patch ImageOps to stop it from performing real math on Mock image objects
    @patch('sagrada_generator.ImageOps')
    @patch('sagrada_generator.Image')
    @patch('sagrada_generator.ImageDraw')
    @patch('sagrada_generator.ImageFont')
    @patch('os.makedirs')
    @patch('os.path.isfile') # Bypass find_tile_path FileNotFoundError
    @patch('builtins.open', new_callable=mock_open)
    def test_create_card(self, mock_file, mock_isfile, mock_makedirs, mock_font, mock_draw, mock_image, mock_image_ops):
        # Pretend requested image files always exist
        mock_isfile.return_value = True 
        
        # Setup mocks
        mock_image.new.return_value = MagicMock()
        mock_image.open.return_value.__enter__.return_value = MagicMock()
        
        mock_font.truetype.return_value = MagicMock()
        mock_draw_instance = mock_draw.Draw.return_value
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 50) 

        # Setup file sequence data
        mock_file.return_value.readline.side_effect = [
            "Card Label\n",
            "1\n",
            "RGBRY\n",
            "RGBRY\n",
            "RGBRY\n",
            "RGBRY\n",
            "output_filename\n",
            "" 
        ]

        # Run the method
        self.generator.generate_cards()

        # Assertions
        mock_makedirs.assert_called_with(self.output_path, exist_ok=True)
        self.assertTrue(mock_image.new.called)
        self.assertTrue(mock_image.open.called)
        self.assertTrue(mock_image_ops.fit.called)
        
        # The main card canvas is the instance returned by Image.new
        mock_img_instance = mock_image.new.return_value
        mock_img_instance.save.assert_called()
        
    @patch('sagrada_generator.ImageOps')
    @patch('sagrada_generator.Image')
    @patch('sagrada_generator.ImageDraw')
    @patch('sagrada_generator.ImageFont')
    @patch('os.makedirs')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_cards_minimal(self, mock_file, mock_isfile, mock_makedirs, mock_font, mock_draw, mock_image, mock_image_ops):
        mock_isfile.return_value = True
        
        mock_file.return_value.readline.side_effect = [
            "Card Label\n", 
            "0\n",          
            "RGBRY\n",      
            "RGBRY\n",      
            "RGBRY\n",      
            "RGBRY\n",      
            "output_filename\n", 
            ""             
        ]
        
        mock_draw_instance = mock_draw.Draw.return_value
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 50)
        
        self.generator.generate_cards()
        mock_makedirs.assert_called()

if __name__ == '__main__':
    unittest.main()