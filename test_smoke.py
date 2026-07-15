
import unittest
import os
import shutil
from PIL import Image, ImageDraw
from sagrada_generator import CardGenerator

class TestSmoke(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_env'
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create dummy assets
        self.font_path = 'georgia.ttf'
        # If font doesn't exist (e.g. in CI environment or strict test env), create a dummy one?
        # But for now assume it exists or use default.
        # Pillow default font is loadable via ImageFont.load_default(), but the code uses truetype path.
        # We'll touch a dummy ttf if it doesn't exist, but that might fail to load.
        # Let's mock the font loading ONLY if necessary, but ideally we use real stuff.
        # If the user has the font, we use it. If not, we might fail.
        # The user has 'georgia.ttf' in the root.
        
        # Copy font to test dir or reference it?
        # The code uses relative paths for images usually?
        # The code: Image.open(f'{row_line[column].upper()}.png')
        # It looks in CWD.
        # So we should run tests in a way that CWD has images.
        
        # Let's create dummy images in current directory (or handle cleanup carefully)
        self.created_files = []
        
        colors = ['R', 'G', 'B', 'Y', 'P', 'W', 'O', 'A'] # Add others if needed
        for c in colors:
            img = Image.new('RGB', (10, 10), color='white')
            filename = f"{c}.png"
            if not os.path.exists(filename):
                img.save(filename)
                self.created_files.append(filename)
            
        # Create card.txt
        self.card_file = 'smoke_card.txt'
        with open(self.card_file, 'w') as f:
            f.write("Smoke Test\n")
            f.write("1\n") # 1 ball
            f.write("RGBRY\n")
            f.write("RGBRY\n")
            f.write("RGBRY\n")
            f.write("RGBRY\n")
            f.write("smoke_output\n")
            f.write("") # Next label empty

        self.output_path = 'smoke_output'

    def tearDown(self):
        for f in self.created_files:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(self.card_file):
            os.remove(self.card_file)
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)

    def test_end_to_end(self):
        # This runs the REAL generator with REAL Pillow
        # It requires georgia.ttf to be present in CWD (which it is in the project)
        
        generator = CardGenerator(
            font_path='georgia.ttf', # Assuming this exists in project root
            output_path=self.output_path,
            card_file=self.card_file
        )
        
        generator.generate_cards()
        
        # Verify output exists
        expected_file = os.path.join(self.output_path, 'smoke_output.png')
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify it's an image
        with Image.open(expected_file) as img:
            self.assertIsNotNone(img)
            self.assertGreater(img.width, 0)
            self.assertGreater(img.height, 0)

if __name__ == '__main__':
    unittest.main()
