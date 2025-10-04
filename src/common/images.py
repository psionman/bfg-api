"""Provide images for BfG functions."""
import os
import io
import base64
from PIL import Image as PilImage

from bridgeobjects import CALLS, CARD_NAMES

BASE_DIRECTORY = 'locale/en_GB'
IMAGE_DIRECTORY = 'images'
CARD_IMAGE_DIRECTORY = 'card_images'
CALL_IMAGE_DIRECTORY = 'call_images'
IMAGE_EXTENSION = 'png'

CURSOR = 'question_white'
CALLS_EXTENSION = [CURSOR, 'blank', 'alert', 'stop', 'right', 'wrong']
CALLS_REMOVE = ['A']


class BaseImage():
    """Base class for images."""
    def __init__(self, name, source_directory, rotate):
        self.name = name
        image_directory = os.path.join(BASE_DIRECTORY,
                                       IMAGE_DIRECTORY,
                                       source_directory)
        image_path = os.path.join(image_directory, f'{name}.{IMAGE_EXTENSION}')
        image = PilImage.open(image_path)
        if rotate:
            image = image.rotate(90, expand=1)
        self.image = self._encode_image(image)

    @staticmethod
    def _encode_image(image):
        """Return image encoded to base64 from a PIL.Image.Image."""
        io_buffer = io.BytesIO()
        image.save(io_buffer, format='PNG')
        saved_image = io_buffer.getvalue()
        encoded_image = ''.join(['data:image/jpg;base64,',
                                 base64.b64encode(saved_image).decode()])
        return encoded_image


class CardImage(BaseImage):
    """Defines a single card image."""
    def __init__(self, name, rotate=False):
        super().__init__(name, CARD_IMAGE_DIRECTORY, rotate)

    def __repr__(self):
        return f'CardImage("{self.name}")'

    def __str__(self):
        return f"CardImage: {self.name}"

    @staticmethod
    def get_images():
        """Return a dict of call images."""
        images = {}
        for card in CARD_NAMES:
            images[card] = CardImage(card).image
        images['back'] = CardImage('back').image
        images['back_rotated'] = CardImage('back', rotate=True).image
        images['blank'] = CardImage('blank').image
        return images


class CallImage(BaseImage):
    """Defines a single call image."""
    def __init__(self, name, rotate=False):
        super().__init__(name, CALL_IMAGE_DIRECTORY, rotate)

    def __repr__(self):
        return f'BidImage("{self.name}")'

    def __str__(self):
        return f"BidImage: {self.name}"

    @staticmethod
    def get_images():
        """Return a dict of call images."""
        images = {}
        calls = [call for call in CALLS if call not in CALLS_REMOVE]
        calls.extend(CALLS_EXTENSION)
        for call in calls:
            images[call] = CallImage(call).image
        return images


# call_images is a dict that contains all the valid calls
CALL_IMAGES = CallImage.get_images()

# card_images is a dict that contains all the valid cards
CARD_IMAGES = CardImage.get_images()
