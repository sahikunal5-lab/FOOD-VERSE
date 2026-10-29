
import cv2
import numpy as np


def preprocess_food_image(
    image_path: str,
    target_size: tuple = (224, 224)
) -> tuple:
    """
    Preprocess a food image and extract visual features.

    Args:
        image_path: Path to the input image.
        target_size: Output size in (width, height) format.

    Returns:
        processed_image: Normalized NumPy image array.
        features: JSON-compatible dictionary of visual features.
    """

    # 1. Validate target dimensions
    if (
        len(target_size) != 2
        or not all(isinstance(x, int) and x > 0 for x in target_size)
    ):
        raise ValueError("target_size must contain two positive integers.")

    # 2. Load the image
    image_bgr = cv2.imread(image_path)

    if image_bgr is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    # 3. Convert BGR to RGB
    image_rgb = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2RGB
    )

    # 4. Resize image
    resized = cv2.resize(
        image_rgb,
        target_size,
        interpolation=cv2.INTER_AREA
    )

    # 5. Reduce noise while preserving useful image details
    denoised = cv2.GaussianBlur(
        resized,
        (3, 3),
        0
    )

    # 6. Normalize pixels to [0, 1]
    processed_image = (
        denoised.astype(np.float32) / 255.0
    )

    # 7. Extract RGB color statistics
    color_statistics = {}

    for index, channel in enumerate(("red", "green", "blue")):
        channel_data = resized[:, :, index].astype(np.float32)

        color_statistics[channel] = {
            "mean": round(float(np.mean(channel_data)), 4),
            "std": round(float(np.std(channel_data)), 4)
        }

    # 8. Extract normalized color histograms
    color_histograms = {}

    for index, channel in enumerate(("red", "green", "blue")):
        histogram = cv2.calcHist(
            [resized],
            [index],
            None,
            [16],
            [0, 256]
        ).flatten()

        histogram /= max(float(histogram.sum()), 1.0)

        color_histograms[channel] = [
            round(float(value), 6)
            for value in histogram
        ]

    # 9. Convert the image to grayscale for texture analysis
    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_RGB2GRAY
    )

    # 10. Detect edges
    edges = cv2.Canny(gray, 100, 200)

    edge_density = float(
        np.count_nonzero(edges) / edges.size
    )

    # 11. Measure grayscale intensity variation
    grayscale_std = float(
        np.std(gray.astype(np.float32))
    )

    # 12. Measure local image detail / sharpness
    laplacian_variance = float(
        cv2.Laplacian(gray, cv2.CV_64F).var()
    )

    # 13. Create structured, JSON-compatible features
    features = {
        "image_size": {
            "width": target_size[0],
            "height": target_size[1]
        },
        "color_statistics": color_statistics,
        "color_histograms": color_histograms,
        "texture_features": {
            "grayscale_std": round(grayscale_std, 4),
            "edge_density": round(edge_density, 6),
            "laplacian_variance": round(
                laplacian_variance, 4
            )
        }
    }

    return processed_image, features