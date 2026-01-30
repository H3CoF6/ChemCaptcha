import random
import io
from PIL import Image, ImageDraw


class NoiseUtils:
    @staticmethod
    def add_interference(img_bytes: bytes, density: int = 2) -> bytes:
        """
        给图片添加干扰线和噪点
        :param img_bytes: 原图字节流
        :param density: 干扰密度等级 (1-5)
        :return: 加噪后的字节流
        """
        image = Image.open(io.BytesIO(img_bytes))

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        draw = ImageDraw.Draw(image)
        width, height = image.size

        line_count = density * 3
        for _ in range(line_count):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)

            fill_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100), 200)
            width_px = random.randint(1, 2)
            draw.line([(x1, y1), (x2, y2)], fill=fill_color, width=width_px)

        point_count = density * 50
        for _ in range(point_count):
            x = random.randint(0, width)
            y = random.randint(0, height)

            fill_color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150), 255)
            draw.point((x, y), fill=fill_color)


        out_stream = io.BytesIO()
        image.save(out_stream, format='PNG')
        return out_stream.getvalue()