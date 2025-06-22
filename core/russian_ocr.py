from core.utils import load_images_from_file, extract_text_from_image, preprocess_russian_image


def process(input_file):
    if input_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = preprocess_russian_image(input_file)
        text = extract_text_from_image(image, lang='rus+eng', config=r'--oem 3 --psm 6')
    else:
        images = load_images_from_file(input_file)
        text_blocks = [extract_text_from_image(img, lang='rus+eng', config=r'--oem 3 --psm 6')
                       for img in images]
        text = "\n".join(text_blocks).strip()

    return 'ru', text