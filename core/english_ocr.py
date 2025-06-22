from core.utils import load_images_from_file, extract_text_from_image


def try_different_configs(image):
    configs = [
        {'oem': 1, 'psm': 1},
        {'oem': 1, 'psm': 3},
        {'oem': 1, 'psm': 4},
        {'oem': 1, 'psm': 6},
        {'oem': 1, 'psm': 11},
        {'oem': 3, 'psm': 1},
        {'oem': 3, 'psm': 3},
        {'oem': 3, 'psm': 4},
        {'oem': 3, 'psm': 6},
        {'oem': 3, 'psm': 11},
    ]

    results = []
    for config in configs:
        try:
            config_str = f"--oem {config['oem']} --psm {config['psm']}"
            text = extract_text_from_image(image, lang='eng', config=config_str)
            if text.strip():
                results.append(text)
        except:
            continue

    return max(results, key=len) if results else ""


def process(input_file):
    images = load_images_from_file(input_file)

    text_blocks = []
    for image in images:
        best_text = try_different_configs(image)
        text_blocks.append(best_text)

    text = "\n".join(text_blocks).strip()
    return 'en', text