from PIL import Image, ImageDraw, ImageFont
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
    # The size of each square is calculated to fit 5 squares
    # and 4 gaps in the 90 mm width of the card.
    SQUARE_SIZE_MM = (CARD_WIDTH_MM - ((SIDE_MARGIN_MM*2)+(SQUARE_GAP_MM*4)))/5
    print(f"Square size: {SQUARE_SIZE_MM} mm")

    # Distance between the bottom of the grid and
    # the visible top of the text
    TEXT_TOP_MARGIN_MM = 3

    # Circle configuration
    BALL_DIAMETER_MM = 2.5

    ROWS = 4
    COLUMNS = 5

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

        # Circle diameter converted from 2.5 mm to pixels.
        ball_diameter_px = self.mm_to_px(
            self.BALL_DIAMETER_MM
        )

        self.ball_size = (
            ball_diameter_px,
            ball_diameter_px
        )

        # Keep the existing 6-pixel gap between circles.
        self.ball_spacing = 6

        # Right margin for the last circle.
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
        Create a fully white circle with a transparent background.
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

        # Always convert the complete label to uppercase.
        text = label.strip().upper()

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

        # Center the 83 mm grid horizontally in the 90 mm card.
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

                tile_path = os.path.join(
                    self.assets_dir,
                    f"{tile_letter}.png"
                )

                if not os.path.exists(tile_path):
                    raise FileNotFoundError(
                        f"Tile image not found: {tile_path}"
                    )

                with Image.open(tile_path) as tile_image:
                    tile_image = (
                        tile_image
                        .convert("RGBA")
                        .resize(
                            (
                                square_size,
                                square_size
                            ),
                            Image.Resampling.LANCZOS
                        )
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

                    img.paste(
                        tile_image,
                        (tile_x, tile_y),
                        tile_image
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

        # Calculate the visible bounds of the text.
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

        # Bottom position of the tile grid.
        grid_bottom = (
            top_margin + grid_height
        )

        # Visible top of the text starts 4 mm below the grid.
        visible_text_top = (
            grid_bottom + text_top_margin
        )

        # Center the text horizontally.
        text_x = (
            (card_width - text_width) / 2
            - text_bbox[0]
        )

        # Compensate for the font's internal top bearing.
        text_y = (
            visible_text_top
            - text_bbox[1]
        )

        # Find the vertical center of the visible text.
        text_center_y = (
            visible_text_top
            + text_height / 2
        )

        # Align the center of every circle with the
        # vertical center of the text.
        ball_y = round(
            text_center_y
            - self.ball_size[1] / 2
        )

        ball = self.create_ball()

        # Position the rightmost circle near the right edge.
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

        path_card = os.path.join(
            self.output_path,
            f"{file_card_name}.png"
        )

        img.save(
            path_card,
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
        assets_dir="assets",
        output_path="sagrada_output",
        card_file="card.txt"
    )

    card_generator.generate_cards()
