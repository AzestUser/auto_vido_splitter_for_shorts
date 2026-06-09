import os
import re
import subprocess
import whisper
from pathlib import Path

def transcribe_video(video_path, model_name="small"):
    """Розпізнає текст у відео та повертає сегменти з таймкодами."""
    print("Завантаження моделі Whisper (це може зайняти макс. хвилину)...")
    model = whisper.load_model(model_name)
    print(f"Аналіз відеофіксації для: {video_path}...")
    result = model.transcribe(video_path, fp16=False, language="uk")
    return result["segments"]

def is_age_marker(text):
    """Перевіряє, чи містить текст маркер віку (цифри)."""
    # Діапазони, які явно вказують на місяці (9-12, 0-6, 6-9, 3-6, 6-12)
    #months_pattern = r"\b(?:0-6|3-6|6-9|9-12|6-12)\b"
    
    # Діапазони, які явно вказують на роки (1-2, 2-3, 3-5, 5-7 тощо)
    # або містять слова про роки
    years_keywords = r"(?:роч|рок|год|року|років|рочки|рочок)"
    
    # Словесні числа
    word_numbers = r"(?:півтора|рік|два|три|чотири|п'ять|шість|сім|вісім|дев'ять|десять|одинадцять)"
    
    # Розміри (80-86, 92-98 - це явно розміри, а не вік)
    size_pattern = r"\b(?:\d{2,3}-\d{2,3})\b"
    
    # Перевіряємо логіку
    #has_months = re.search(months_pattern, text, re.IGNORECASE)
    has_years_keyword = re.search(years_keywords, text, re.IGNORECASE)
    has_word_number = re.search(word_numbers, text, re.IGNORECASE)
    
    # Якщо містить явно місяці - це маркер віку
  #  if has_months:
    #    return True, "вік (місяці)"
    
    # Якщо містить слова про роки - це маркер віку
    if has_years_keyword:
        return True, "вік (роки)"
    
    # Якщо містить словесні числа - це маркер віку
    if has_word_number:
        return True, "вік (словами)"
    
    # Якщо є díапазон без слів про роки, перевіряємо логіку:
    # 9-12, 0-6, 6-9 - місяці, 1-2, 2-3, 3-5 - роки
    range_pattern = r"\b(\d+)\s*[-–—]\s*(\d+)\b"
    match = re.search(range_pattern, text)
    
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        
        # Якщо діапазон більший за 20 - це явно розмір, а не вік
        if start > 20 or end > 20:
            return False, None
        
        # Якщо діапазон типу 0-12, 3-12, 6-12 - це місяці
        if (start in [0, 3, 6] and end in [6, 9, 12]) or \
           (start in [9, 12] and end >= 12):
            return True, "вік (місяці)"
        
        # Якщо діапазон типу 1-2, 2-3, 3-5 - це роки
        if start <= 10 and end <= 10 and (start < end):
            return True, "вік (роки)"
    
    return False, None

def extract_split_points(segments, min_segment_length=5.0):
    """Шукає таймкоди на основі регулярних виразів для розмірів та віку."""
    split_points = []
    last_marker_time = -min_segment_length
    
    for seg in segments:
        text = seg["text"].strip()
        start_time = seg["start"]
        
        # Перевіряємо, чи це маркер віку
        is_marker, marker_type = is_age_marker(text)
        
        if is_marker:
            # Захист від занадто частих розрізів
            if start_time - last_marker_time > min_segment_length:
                split_points.append({
                    "start": start_time,
                    "text": text,
                    "pattern": marker_type
                })
                print(f"✓ Маркер [{start_time:.2f}с] ({marker_type}): «{text}»")
                last_marker_time = start_time
            else:
                print(f"  Пропущено (занадто близько) [{start_time:.2f}с]: «{text}»")
    
    print(f"\n📍 Знайдено {len(split_points)} блоків розмірів\n")
    return split_points

def cut_video_by_timestamps(video_path, split_points, output_folder="output_clips"):
    """Нарізає відео за знайденими таймкодами за допомогою FFmpeg."""
    if not split_points:
        print("❌ Маркери розмірів не знайдені. Нарізка скасована.")
        return
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Створена папка: {output_folder}\n")
    
    try:
        # Отримуємо тривалість відео через ffprobe
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1:noprint_wrappers=1",
                video_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        print(f"📹 Загальна тривалість відео: {duration:.2f}с\n")
        
        # Формуємо список усіх точок розрізу
        timestamps = [p["start"] for p in split_points] + [duration]
        
        for i in range(len(timestamps) - 1):
            start = timestamps[i]
            end = timestamps[i + 1]
            clip_duration = end - start
            
            # Формуємо красиве ім'я файлу
            marker_text = split_points[i]["text"]
            # Витягуємо розмір/вік з тексту
            size_match = re.search(r"(\d+-\d+|\d+\s*(?:роч|рок|лед|год)\w*|\d+)", marker_text)
            if size_match:
                clean_text = size_match.group(1).replace(" ", "")
            else:
                clean_text = "".join(
                    c for c in marker_text[:15] if c.isalnum() or c in " -"
                ).strip()
            
            file_name = f"clip_{i+1:02d}_{clean_text.replace(' ', '_')}.mp4"
            output_path = os.path.join(output_folder, file_name)
            
            print(f"🎬 Фрагмент {i+1}/{len(timestamps)-1}")
            print(f"   Час: {start:.2f}с - {end:.2f}с ({clip_duration:.2f}с)")
            print(f"   Маркер: «{marker_text}»")
            print(f"   Файл: {file_name}")
            
            # FFmpeg команда для нарізання
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start),           # Початок сегменту
                "-to", str(end),             # Кінець сегменту
                "-c:v", "libx264",           # Відеокодек
                "-preset", "ultrafast",      # Швидкість кодування
                "-c:a", "aac",               # Аудіокодек
                "-q:a", "5",                 # Якість аудіо
                "-y",                        # Перезаписати без запиту
                output_path
            ]
            
            # Запускаємо FFmpeg (приховуємо вивід)
            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                timeout=300  # Максимум 5 хвилин на фрагмент
            )
            
            print(f"   ✓ Готово\n")
        
        print(f"✅ Усі файли збережено в папку: {output_folder}/")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg помилка: {e}")
        print(f"   Стандартна помилка: {e.stderr.decode() if e.stderr else 'немає'}")
        raise
    except Exception as e:
        print(f"❌ Помилка під час нарізання відео: {str(e)}")
        raise

def main():
    """Головна функція."""
    # Замініть на шлях до вашого файлу
    INPUT_VIDEO = "your_video.mp4"
    OUTPUT_FOLDER = "output_clips"
    
    # Перевіряємо, чи існує вхідний файл
    if not os.path.exists(INPUT_VIDEO):
        print(f"❌ Файл не знайдено: {INPUT_VIDEO}")
        print("Будь ласка, замініть INPUT_VIDEO на правильний шлях до вашого відео.")
        return
    
    print("=" * 60)
    print("🎥 РОЗДІЛЮВАЧ ВІДЕО ЗА РОЗМІРАМИ ОДЯГУ")
    print("=" * 60 + "\n")
    
    try:
        # 1. Розпізнаємо мову
        print("📢 Крок 1: Розпізнання мови у відео...\n")
        segments = transcribe_video(INPUT_VIDEO, model_name="small")
        
        print(f"📝 Знайдено {len(segments)} сегментів тексту\n")
        
        # 2. Шукаємо таймкоди маркерів розмірів
        print("🔍 Крок 2: Пошук маркерів розмірів...\n")
        split_points = extract_split_points(segments, min_segment_length=7.0)
        
        # 3. Ріжемо відео на шматки
        print("✂️  Крок 3: Нарізання відео...\n")
        cut_video_by_timestamps(INPUT_VIDEO, split_points, OUTPUT_FOLDER)
        
    except Exception as e:
        print(f"❌ Критична помилка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
