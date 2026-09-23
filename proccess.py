import os
from PIL import Image

def normalize_icon(input_path, output_path, target_size=(200, 200), padding_ratio=0.95, alpha_threshold=16):
    # 1. Відкриваємо зображення
    img = Image.open(input_path).convert("RGBA")

    # 2. Знаходимо обмежувальну рамку (bbox) видимих пікселів (не прозорих).
    # getbbox() рахує контентом навіть альфу=1, тому ледь помітний ореол
    # навколо об'єкта роздував рамку до країв полотна — відсікаємо його порогом.
    mask = img.getchannel("A").point(lambda p: 255 if p > alpha_threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        # Якщо картинка повністю прозора, просто пропускаємо
        return

    # Обрізаємо пусті поля навколо іконки
    cropped_img = img.crop(bbox)

    # 3. Обчислюємо новий розмір для іконки з урахуванням відступів (padding)
    src_width, src_height = cropped_img.size
    scale_factor = min(
        target_size[0] * padding_ratio / src_width,
        target_size[1] * padding_ratio / src_height,
    )
    new_width = max(1, round(src_width * scale_factor))
    new_height = max(1, round(src_height * scale_factor))

    # Змінюємо розмір самої іконки
    resized_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 4. Створюємо нове прозоре полотно 200х200
    new_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
    
    # Обчислюємо координати для центрування
    paste_x = (target_size[0] - new_width) // 2
    paste_y = (target_size[1] - new_height) // 2
    
    # Вставляємо іконку по центру
    new_img.paste(resized_img, (paste_x, paste_y), resized_img)
    
    # 5. Зберігаємо результат
    new_img.save(output_path)

if __name__ == "__main__":
    input_folder = "in"      # Папка з вихідними іконками
    output_folder = "out"    # Папка для оброблених іконок

    # Перевіряємо чи існує папка з вхідними файлами
    if not os.path.exists(input_folder):
        print(f"❌ Помилка: папка '{input_folder}' не знайдена!")
        exit(1)

    os.makedirs(output_folder, exist_ok=True)

    png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]

    if not png_files:
        print(f"⚠️  У папці '{input_folder}' не знайдено файлів PNG")
        exit(0)

    processed_count = 0
    for filename in png_files:
        try:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            normalize_icon(
                input_path,
                output_path,
                target_size=(100, 100),
                padding_ratio=1
            )
            processed_count += 1
            print(f"✅ {filename}")
        except Exception as e:
            print(f"❌ Помилка при обробці {filename}: {e}")

    print(f"\n✨ Обробка завершена! Опрацьовано {processed_count} файлів.")
