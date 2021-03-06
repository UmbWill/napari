"""QtTestImage and QtTestImageLayout classes.
"""
from typing import Callable, Tuple

import numpy as np
from qtpy.QtWidgets import QCheckBox, QFrame, QPushButton, QVBoxLayout

from ....utils import config
from .qt_labeled_spin_box import QtLabeledSpinBox
from .test_image import create_tiled_text_array

Callback = Callable[[], None]
IntCallback = Callable[[int], None]

TILE_SIZE_DEFAULT = 64
TILE_SIZE_RANGE = range(1, 4096, 100)

IMAGE_SIZE_DEFAULT = (1024, 1024)  # (width, height)
IMAGE_SIZE_RANGE = range(1, 65536, 100)


class QtTestImageLayout(QVBoxLayout):
    """Controls to a create a new test image layer.

    Parameters
    ----------
    on_create : Callable[[], None]
        Called when the create test image button is pressed.
    """

    def __init__(self, on_create: Callback):
        super().__init__()
        self.addStretch(1)

        # Dimension controls.
        self.width = QtLabeledSpinBox(
            "Image Width", IMAGE_SIZE_DEFAULT[0], IMAGE_SIZE_RANGE
        )
        self.height = QtLabeledSpinBox(
            "Image Height", IMAGE_SIZE_DEFAULT[1], IMAGE_SIZE_RANGE
        )
        self.addLayout(self.width)
        self.addLayout(self.height)

        self.tile_size = QtLabeledSpinBox(
            "Tile Size", TILE_SIZE_DEFAULT, TILE_SIZE_RANGE
        )
        self.addLayout(self.tile_size)

        # Checkbox so we can choose between OctreeImage and regular Image.
        self.octree = QCheckBox("Octree Image")
        self.octree.setChecked(1)
        self.addWidget(self.octree)

        # The create button.
        button = QPushButton("Create Test Image")
        button.setToolTip("Create a new test image")
        button.clicked.connect(on_create)
        self.addWidget(button)

    def get_image_size(self) -> Tuple[int, int]:
        """Return the configured image size.

        Return
        ------
        Tuple[int, int]
            The [width, height] requested by the user.
        """
        return (self.width.spin.value(), self.height.spin.value())

    def get_tile_size(self) -> int:
        """Return the configured tile size.

        Return
        ------
        int
            The requested tile size.
        """
        return self.tile_size.spin.value()


class QtTestImage(QFrame):
    """Frame with controls to create a new test image.

    Parameters
    ----------
    viewer : Viewer
        The napari viewer.
    """

    # This is a class attribute so that we use a unique index napari-wide,
    # not just within in this one QtRender widget, this one layer.
    image_index = 0

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.layout = QtTestImageLayout(self._create_test_image)
        self.setLayout(self.layout)

    def _create_test_image(self) -> None:
        """Create a new test image."""
        # Configure whether viewer.add_image() will create regular Images
        # or OctreeImages.
        config.create_octree_images = self.layout.octree.isChecked()

        image_size = self.layout.get_image_size()

        # We have just one type of test image right now, with the little
        # slice number digits in the image itself.
        images = [
            create_tiled_text_array(x, 16, 16, image_size) for x in range(5)
        ]
        data = np.stack(images, axis=0)

        # Give each layer a unique name.
        unique_name = f"test-image-{QtTestImage.image_index:003}"
        QtTestImage.image_index += 1

        layer = self.viewer.add_image(data, rgb=True, name=unique_name)
        layer.tile_size = self.layout.get_tile_size()
