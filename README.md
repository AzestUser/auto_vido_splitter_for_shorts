# auto-Video-cut

Проєкт `auto_vido_splitter_for_shorts` автоматично розпізнає маркери віку/розмірів у відео й нарізає файл на кліпи за знайденими таймкодами.

## Опис

Цей інструмент призначений для автоматичної обробки відеозаписів із маркуванням одягу за віком або розміром. Він використовує модель Whisper для розпізнавання мови українською та FFmpeg для створення окремих відеофрагментів.

## Файли

- `app.py` - графічний інтерфейс користувача на Tkinter. Дозволяє вибрати відео, музику, папку для збереження та параметри обробки.
- `video_splitter.py` - основна логіка:
  - розпізнавання аудіо за допомогою Whisper,
  - пошук маркерів віку/розміру,
  - формування таймкодів та нарізка відео через FFmpeg.
- `launcher.py` - простий лаунчер, що запускає `app.py` через поточний Python.
- `output_clips/` - стандартна папка для результатів нарізки.
- `export/` - додаткова папка, що може використовуватись для експорту даних.

## Основні можливості

- Зчитування аудіо з відеофайлу й транскрибування українською мовою.
- Виявлення маркерів віку/розміру у тексті (наприклад, згадки про роки чи діапазони `3-5`, `6-12`).
- Нарізка відео на фрагменти за знайденими маркерами.
- Підтримка вибору моделі Whisper (`tiny`, `small`, `base`, `medium`).
- Графічний інтерфейс із налаштуванням гучності, мінімальної довжини сегмента та шляху виводу.

## Встановлення

1. Створіть та активуйте віртуальне середовище Python.
2. Встановіть залежності та підготуйте середовище:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> Якщо у репозиторії немає `requirements.txt`, додайте до нього як мінімум:
> ```text
> whisper
> tkinter
> ```

3. Переконайтеся, що `ffmpeg` та `ffprobe` встановлені і доступні в PATH.

## Запуск

### Графічний інтерфейс

```powershell
python launcher.py
```

або

```powershell
python app.py
```

### Командний рядок

`video_splitter.py` можна викликати безпосередньо, але він також містить приклад використання з жорстко закріпленим шляхом `your_video.mp4`.

## Використання

1. Виберіть відеофайл.
2. За бажанням виберіть фонову музику.
3. Вкажіть папку для збереження кліпів.
4. Налаштуйте мінімальну довжину сегмента та модель Whisper.
5. Натисніть кнопку запуску.

Результат зберігається у папці `output_clips` або в іншій папці, яку ви оберете.

## Обмеження та примітки

- Проєкт покладається на якість розпізнавання Whisper і може пропускати маркери, якщо текст не чіткий.
- Потрібно мати встановлений FFmpeg для нарізки відео.
- У `video_splitter.py` є базові правила для розпізнавання віку/розміру, які можна адаптувати під конкретні маркери та формат запису.
- Рекомендується використовувати відео з чітким аудіо для кращого розпізнавання.

---

# English version

The `auto-Video-cut` project automatically recognizes age/size markers in video audio and cuts the file into clips based on detected timestamps.

## Description

This tool is designed to automatically process footage tagged with clothing age or size markers. It uses Whisper for speech recognition and FFmpeg to create separate video segments.

## Files

- `app.py` - Tkinter graphical user interface. Allows selecting a video, optional background music, output folder, and processing options.
- `video_splitter.py` - main logic:
  - audio transcription with Whisper,
  - detection of age/size markers,
  - timestamp extraction and video cutting with FFmpeg.
- `launcher.py` - simple launcher that runs `app.py` using the current Python interpreter.
- `output_clips/` - default folder for saved clip results.
- `export/` - optional folder for exported data.

## Features

- Reads video audio and transcribes it in Ukrainian.
- Detects age/size markers in text (for example, mentions like `3-5`, `6-12`, or year-related words).
- Cuts the video into clips using the detected markers.
- Supports Whisper model selection (`tiny`, `small`, `base`, `medium`).
- GUI with volume control, minimum segment length, and output path settings.

## Installation

1. Create and activate a Python virtual environment.
2. Install dependencies and prepare the environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> If the repository does not have `requirements.txt`, add at least:
> ```text
> whisper
> tkinter
> ```

3. Make sure `ffmpeg` and `ffprobe` are installed and available in PATH.

## Usage

### Graphical interface

```powershell
python launcher.py
```

or

```powershell
python app.py
```

### Command line

`video_splitter.py` can be run directly, but it currently includes an example with a hardcoded `your_video.mp4` path.

## How to use

1. Select a video file.
2. Optionally select background music.
3. Specify the folder for saving clips.
4. Adjust the minimum segment length and Whisper model.
5. Start the processing.

The output is saved to the `output_clips` folder or another folder you choose.

## Notes and limitations

- The project depends on Whisper transcription quality and may miss markers if the audio is unclear.
- FFmpeg must be installed for video cutting.
- `video_splitter.py` uses basic age/size marker detection rules that can be adapted for specific marker formats.
- It is recommended to use video with clear audio for better recognition.
