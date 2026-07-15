from PIL import Image, ImageDraw, ImageFont, ImageOps
import os


class CardGenerator:
    DPI = 300

    # Final printed card dimensions
    CARD_WIDTH_MM = 90
    CARD_HEIGHT_MM = 80

    # Grid configuration
    TOP_MARGIN_MM = 2
    SIDE_MARGIN_MM = 2.5
    SQUARE_GAP_MM = 2

    SQUARE_SIZE_MM = (
        CARD_WIDTH_MM
        - (
            SIDE_MARGIN_MM * 2
            + SQUARE_GAP_MM * 4
        )
    ) / 5

    print(f"Square size: {SQUARE_SIZE_MM} mm")

    # Distance between the bottom of the grid and the text
    TEXT_TOP_MARGIN_MM = 3

    # Circle configuration
    BALL_DIAMETER_MM = 2.5

    ROWS = 4
    COLUMNS = 5

    # Accepted source image formats
    IMAGE_EXTENSIONS = (
        ".jpg",
        ".jpeg",
        ".JPG",
        ".JPEG",
        ".png",
        ".PNG",
    )

    def __init__(
        self,
        assets_dir,
        font_path,
        output_path,
        card_file
    ):
        self.assets_dir = assets_dir
        self.font_path = os.path.join(
            assets_dir,
            font_path
        )
        self.output_path = output_path
        self.card_file = card_file

        ball_diameter_px = self.mm_to_px(
            self.BALL_DIAMETER_MM
        )

        self.ball_size = (
            ball_diameter_px,
            ball_diameter_px
        )

        # Gap between circles in pixels
        self.ball_spacing = 6

        # Right margin in pixels
        self.ball_right_margin = 50

    @classmethod
    def mm_to_px(cls, millimetres):
        """
        Convert millimetres to pixels at the configured DPI.
        """
        return round(
            millimetres * cls.DPI / 25.4
        )

    def create_ball(self):
        """
        Create a fully white circle with transparency.
        """
        ball = Image.new(
            mode="RGBA",
            size=self.ball_size,
            color=(0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(ball)

        draw.ellipse(
            (
                0,
                0,
                self.ball_size[0] - 1,
                self.ball_size[1] - 1
            ),
            fill=(255, 255, 255, 255)
        )

        return ball

    def find_tile_path(self, tile_letter):
        """
        Find a tile using JPG, JPEG, or PNG.
        JPG is checked first.
        """
        for extension in self.IMAGE_EXTENSIONS:
            tile_path = os.path.join(
                self.assets_dir,
                f"{tile_letter}{extension}"
            )

            if os.path.isfile(tile_path):
                return tile_path

        supported = ", ".join(self.IMAGE_EXTENSIONS)

        raise FileNotFoundError(
            f"No image found for tile '{tile_letter}'. "
            f"Supported extensions: {supported}"
        )

    def prepare_square_image(
        self,
        image,
        square_size
    ):
        """
        Crop the image to a centered square without distortion,
        then resize it to the required dimensions.
        """
        # Apply the orientation stored by phones and cameras
        image = ImageOps.exif_transpose(image)

        # Convert to RGB because JPEG does not support transparency
        if image.mode == "RGBA":
            background = Image.new(
                "RGB",
                image.size,
                "black"
            )

            background.paste(
                image,
                mask=image.getchannel("A")
            )

            image = background
        else:
            image = image.convert("RGB")

        return ImageOps.fit(
            image,
            (square_size, square_size),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )

    def create_card(
        self,
        label,
        parameter_file
    ):
        card_width = self.mm_to_px(
            self.CARD_WIDTH_MM
        )

        card_height = self.mm_to_px(
            self.CARD_HEIGHT_MM
        )

        square_size = self.mm_to_px(
            self.SQUARE_SIZE_MM
        )

        square_gap = self.mm_to_px(
            self.SQUARE_GAP_MM
        )

        top_margin = self.mm_to_px(
            self.TOP_MARGIN_MM
        )

        text_top_margin = self.mm_to_px(
            self.TEXT_TOP_MARGIN_MM
        )

        img = Image.new(
            mode="RGB",
            size=(card_width, card_height),
            color="black"
        )

        canvas = ImageDraw.Draw(img)

        font = ImageFont.truetype(
            self.font_path,
            42
        )

        text = label

        total_balls_line = parameter_file.readline()

        if not total_balls_line:
            raise ValueError(
                f"Missing ball count for card '{text}'."
            )

        total_balls = int(
            total_balls_line.strip()
        )

        grid_width = (
            self.COLUMNS * square_size
            + (self.COLUMNS - 1) * square_gap
        )

        grid_height = (
            self.ROWS * square_size
            + (self.ROWS - 1) * square_gap
        )

        left_margin = (
            card_width - grid_width
        ) // 2

        for row in range(self.ROWS):
            row_line = (
                parameter_file
                .readline()
                .strip()
            )

            if len(row_line) < self.COLUMNS:
                raise ValueError(
                    f"Row {row + 1} for card '{text}' "
                    f"must contain at least "
                    f"{self.COLUMNS} characters."
                )

            for column in range(self.COLUMNS):
                tile_letter = row_line[column].upper()

                tile_path = self.find_tile_path(
                    tile_letter
                )

                with Image.open(tile_path) as tile_image:
                    tile_image = self.prepare_square_image(
                        tile_image,
                        square_size
                    )

                    tile_x = (
                        left_margin
                        + column
                        * (
                            square_size
                            + square_gap
                        )
                    )

                    tile_y = (
                        top_margin
                        + row
                        * (
                            square_size
                            + square_gap
                        )
                    )

                    # No transparency mask is necessary for RGB images
                    img.paste(
                        tile_image,
                        (tile_x, tile_y)
                    )

        file_card_name = (
            parameter_file
            .readline()
            .strip()
        )

        if not file_card_name:
            raise ValueError(
                f"Missing output filename for card '{text}'."
            )

        text_bbox = canvas.textbbox(
            (0, 0),
            text,
            font=font
        )

        text_width = (
            text_bbox[2] - text_bbox[0]
        )

        text_height = (
            text_bbox[3] - text_bbox[1]
        )

        grid_bottom = (
            top_margin + grid_height
        )

        visible_text_top = (
            grid_bottom + text_top_margin
        )

        text_x = (
            (card_width - text_width) / 2
            - text_bbox[0]
        )

        text_y = (
            visible_text_top
            - text_bbox[1]
        )

        text_center_y = (
            visible_text_top
            + text_height / 2
        )

        ball_y = round(
            text_center_y
            - self.ball_size[1] / 2
        )

        ball = self.create_ball()

        ball_start_x = (
            card_width
            - self.ball_right_margin
            - self.ball_size[0]
        )

        for n_ball in range(total_balls):
            ball_x = (
                ball_start_x
                - n_ball
                * (
                    self.ball_size[0]
                    + self.ball_spacing
                )
            )

            img.paste(
                ball,
                (ball_x, ball_y),
                ball
            )

        canvas.text(
            (text_x, text_y),
            text,
            font=font,
            fill="white"
        )

        # Save the generated card as JPG
        path_card = os.path.join(
            self.output_path,
            f"{file_card_name}.jpg"
        )

        img.save(
            path_card,
            format="JPEG",
            quality=100,
            subsampling=0,
            optimize=True,
            dpi=(self.DPI, self.DPI)
        )

        print(
            "{filename:>16s}:\t{cardname}".format(
                filename=file_card_name,
                cardname=text
            )
        )

        next_label = (
            parameter_file
            .readline()
            .strip()
        )

        if next_label:
            self.create_card(
                next_label,
                parameter_file
            )

    def generate_cards(self):
        os.makedirs(
            self.output_path,
            exist_ok=True
        )

        with open(
            self.card_file,
            mode="r",
            encoding="utf-8"
        ) as file:
            first_label = (
                file
                .readline()
                .strip()
            )

            if first_label:
                self.create_card(
                    first_label,
                    file
                )

        print("✓ Finished")


if __name__ == "__main__":
    card_generator = CardGenerator(
        font_path="georgia.ttf",
        assets_dir="assets_remastered",
        output_path="sagrada_output",
        card_file="card.txt"
    )

    card_generator.generate_cards()