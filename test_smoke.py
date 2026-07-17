import unittest
import os
import shutil
from PIL import Image, ImageFont
from unittest.mock import patch
from sagrada_generator import CardGenerator

# Load the default font ONCE before any mock is applied.
# This avoids the RecursionError where load_default() calls the patched truetype().
DEFAULT_FONT = ImageFont.load_default(size=42)

def fake_truetype(*args, **kwargs):
    """Dynamically return the pre-loaded default font to bypass missing TTF files."""
    return DEFAULT_FONT

class TestSmoke(unittest.TestCase):
    def setUp(self):
        # Create a contained test directory structure
        self.test_dir = 'test_env'
        self.assets_dir = os.path.join(self.test_dir, 'assets_remastered')
        self.output_path = os.path.join(self.test_dir, 'smoke_output')
        
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Create valid dummy images exactly where the generator expects them
        colors = ['R', 'G', 'B', 'Y', 'P', 'W', 'O', 'A']
        for c in colors:
            img = Image.new('RGB', (10, 10), color='white')
            filename = os.path.join(self.assets_dir, f"{c}.png")
            img.save(filename)
            
        # Create card.txt
        self.card_file = os.path.join(self.test_dir, 'smoke_card.txt')
        with open(self.card_file, 'w') as f:
            f.write("Smoke Test\n")
            f.write("1\n") 
            f.write("RGBRY\n")
            f.write("RGBRY\n")
            f.write("RGBRY\n")
            f.write("RGBRY\n")
            f.write("smoke_output\n")
            f.write("\n") # Next label empty to stop generation

    def tearDown(self):
        # Clean up everything at once by removing the test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('sagrada_generator.ImageFont.truetype', side_effect=fake_truetype)
    def test_end_to_end(self, mock_truetype):
        generator = CardGenerator(
            font_path='georgia.ttf',
            output_path=self.output_path,
            card_file=self.card_file,
            assets_dir=self.assets_dir
        )
        
        # Run end-to-end generation
        generator.generate_cards()
        
        # Verify output exists
        expected_file = os.path.join(self.output_path, 'smoke_output.jpg')
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify it's a real image that was successfully compiled
        with Image.open(expected_file) as img:
            self.assertIsNotNone(img)
            self.assertGreater(img.width, 0)
            self.assertGreater(img.height, 0)

if __name__ == '__main__':
    unittest.main()