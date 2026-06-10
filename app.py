import os
import re
import subprocess
import whisper
import threading
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

class VideoSplitterApp:
    def __init__(self, root):
        self.root = root
        self.language_var = StringVar(value="uk")
        self.translations = {
            "title": {"uk": "🎥 Розділювач Відео за Розмірами Одягу", "en": "🎥 Video Splitter by Size"},
            "video_section": {"uk": "1. Вибір матеріалу", "en": "1. Choose source"},
            "video_label": {"uk": "Відео:", "en": "Video:"},
            "video_none": {"uk": "Не вибрано...", "en": "No video selected..."},
            "browse_video": {"uk": "📂 Вибрати відео", "en": "📂 Select video"},
            "music_label": {"uk": "Фонова музика:", "en": "Background music:"},
            "music_none": {"uk": "Не вибрана...", "en": "None selected..."},
            "browse_music": {"uk": "🎵 Вибрати музику", "en": "🎵 Select music"},
            "output_section": {"uk": "2. Папка збереження", "en": "2. Save folder"},
            "output_browse": {"uk": "📂", "en": "📂"},
            "params_section": {"uk": "3. Параметри", "en": "3. Settings"},
            "min_segment": {"uk": "Мін. довжина маркера (сек):", "en": "Min marker length (sec):"},
            "volume": {"uk": "Гучність музики:", "en": "Music volume:"},
            "model_label": {"uk": "Модель розпізнавання:", "en": "Recognition model:"},
            "subtitles_option": {"uk": "🎬 Додати субтитри на відео", "en": "🎬 Add subtitles to video"},
            "progress": {"uk": "Прогрес:", "en": "Progress:"},
            "start_button": {"uk": "▶ Почати", "en": "▶ Start"},
            "clear_button": {"uk": "🗑 Очистити", "en": "🗑 Clear"},
            "log_label": {"uk": "Лог:", "en": "Log:"},
            "select_video_error": {"uk": "Будь ласка, оберіть відео!", "en": "Please select a video!"},
            "processing_warning": {"uk": "Обробка вже йде...", "en": "Processing is already running..."},
            "processing_title": {"uk": "🎥 РОЗДІЛЮВАЧ ВІДЕО ЗА РОЗМІРАМИ ОДЯГУ", "en": "🎥 VIDEO SPLITTER BY SIZE"},
            "transcribing": {"uk": "📢 Крок 1: Розпізнавання мови у відео...\n", "en": "📢 Step 1: Transcribing audio...\n"},
            "found_segments": {"uk": "✓ Знайдено {count} сегментів тексту\n", "en": "✓ Found {count} text segments\n"},
            "searching_markers": {"uk": "🔍 Крок 2: Пошук маркерів розмірів...\n", "en": "🔍 Step 2: Searching for size markers...\n"},
            "prepare_subtitles": {"uk": "✏️ Підготовка тексту для субтитрів...\n", "en": "✏️ Preparing subtitle text...\n"},
            "cutting_video": {"uk": "✂️  Крок 3: Нарізання відео...\n", "en": "✂️  Step 3: Cutting video...\n"},
            "process_complete": {"uk": "\n✅ Готово! Файли збережено.", "en": "\n✅ Done! Files saved."},
            "success_title": {"uk": "Успіх", "en": "Success"},
            "error_title": {"uk": "Помилка", "en": "Error"},
            "processing_error": {"uk": "Сталася помилка:\n{msg}", "en": "An error occurred:\n{msg}"},
            "loading_model": {"uk": "Завантаження моделі Whisper...", "en": "Loading Whisper model..."},
            "analyzing": {"uk": "Аналіз відеофіксації...", "en": "Analyzing video..."},
            "created_folder": {"uk": "📁 Створена папка: {folder}\n", "en": "📁 Created folder: {folder}\n"},
            "duration": {"uk": "📹 Загальна тривалість: {duration:.2f}с\n", "en": "📹 Total duration: {duration:.2f}s\n"},
            "fragment": {"uk": "🎬 Фрагмент {current}/{total}", "en": "🎬 Clip {current}/{total}"},
            "subtitles_creating": {"uk": "   📝 Створення субтитрів...", "en": "   📝 Creating subtitles..."},
            "music_adding": {"uk": "   🎵 Накладання музики...", "en": "   🎵 Adding music..."},
            "done_saving": {"uk": "✅ Усі файли збережено в: {folder}/", "en": "✅ All files saved in: {folder}/"},
            "warning_metadata": {"uk": "⚠️  Помилка при додаванні метаданих: {msg}", "en": "⚠️  Metadata add error: {msg}"},
            "warning_srt": {"uk": "⚠️  Помилка при створенні SRT: {msg}", "en": "⚠️  Error creating SRT: {msg}"},
            "warning_subtitles": {"uk": "⚠️  Помилка при накладанні субтитрів: {msg}", "en": "⚠️  Error overlaying subtitles: {msg}"},
            "warning_adjust": {"uk": "⚠️  Помилка при коригуванні SRT: {msg}", "en": "⚠️  Error adjusting SRT: {msg}"},
            "language_menu": {"uk": "Мова", "en": "Language"},
            "language_uk": {"uk": "Українська", "en": "Ukrainian"},
            "language_en": {"uk": "Англійська", "en": "English"},
            "editor_title": {"uk": "Редагування тексту субтитрів", "en": "Subtitle text editor"},
            "editor_info": {"uk": "Відредагуйте текст для кожного фрагмента перед додаванням субтитрів:", "en": "Edit the text for each clip before adding subtitles:"},
            "editor_segment": {"uk": "Текст фрагмента:", "en": "Clip text:"},
            "editor_save": {"uk": "Зберегти і продовжити", "en": "Save and continue"},
            "no_markers": {"uk": "❌ Маркери розмірів не знайдені.", "en": "❌ No size markers found."},
            "select_music_cancel": {"uk": "Музика скасована", "en": "Music canceled"},
            "video_selected": {"uk": "Обраний файл: {path}", "en": "Selected video: {path}"},
            "music_selected": {"uk": "Обрана музика: {path}", "en": "Selected music: {path}"},
            "folder_selected": {"uk": "Папка збереження: {path}", "en": "Output folder: {path}"}
        }
        self.language_menu_index = None
        self.menu_bar = None
        self.language_menu = None
        self.video_path = StringVar()
        self.music_path = StringVar()
        self.output_folder = StringVar(value="output_clips")
        self.music_volume = DoubleVar(value=0.3)  # 30% за замовчуванням
        self.subtitles_var = BooleanVar(value=False)
        self.is_running = False

        self.root.title(self.t("title"))
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        self.root.option_add('*tearOff', FALSE)

        self.menu_bar = Menu(self.root)
        self.language_menu = Menu(self.menu_bar, tearoff=0)
        self.language_menu.add_radiobutton(label=self.t("language_uk"), variable=self.language_var, value="uk", command=self.update_ui_language)
        self.language_menu.add_radiobutton(label=self.t("language_en"), variable=self.language_var, value="en", command=self.update_ui_language)
        self.menu_bar.add_cascade(label=self.t("language_menu"), menu=self.language_menu)
        self.language_menu_index = self.menu_bar.index("end")
        self.root.config(menu=self.menu_bar)

        self.setup_ui()
        
    def setup_ui(self):
        """Створює інтерфейс програми."""
        # Заголовок
        title_frame = Frame(self.root, bg="#2c3e50", pady=15)
        title_frame.pack(fill=X)
        
        self.title_label = Label(
            title_frame,
            text=self.t("title"),
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.title_label.pack()
        
        # Основна панель з двома колонами
        main_frame = Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # === ЛІВА КОЛОНА ===
        left_frame = Frame(main_frame, bg="#f0f0f0")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # Вибір відео
        self.video_label = Label(left_frame, text=self.t("video_section"), font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.video_label.pack(anchor=W, pady=(0, 10))
        
        video_box = Frame(left_frame, bg="white", relief=SUNKEN, bd=1, padx=10, pady=10)
        video_box.pack(fill=X, pady=(0, 15))
        
        Label(video_box, text=self.t("video_label"), font=("Arial", 10, "bold"), bg="white").pack(anchor=W)
        
        self.video_display = Label(
            video_box,
            text=self.t("video_none"),
            font=("Arial", 9),
            bg="white",
            fg="#666",
            wraplength=400,
            justify=LEFT
        )
        self.video_display.pack(fill=X, pady=(5, 10), anchor=W)
        
        self.browse_btn = Button(
            video_box,
            text=self.t("browse_video"),
            command=self.select_video,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief=FLAT
        )
        self.browse_btn.pack(anchor=W, pady=(0, 10))
        
        # Музика
        self.music_label = Label(video_box, text=self.t("music_label"), font=("Arial", 10, "bold"), bg="white")
        self.music_label.pack(anchor=W, pady=(10, 0))

        self.music_display = Label(
            video_box,
            text=self.t("music_none"),
            font=("Arial", 9),
            bg="white",
            fg="#666",
            wraplength=400,
            justify=LEFT
        )
        self.music_display.pack(fill=X, pady=(5, 10), anchor=W)
        
        self.music_btn = Button(
            video_box,
            text=self.t("browse_music"),
            command=self.select_music,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief=FLAT
        )
        self.music_btn.pack(anchor=W)
        
        # Папка збереження
        self.output_label = Label(left_frame, text=self.t("output_section"), font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.output_label.pack(anchor=W, pady=(10, 10))
        
        output_frame = Frame(left_frame, bg="white", relief=SUNKEN, bd=1, padx=10, pady=10)
        output_frame.pack(fill=X, pady=(0, 15))
        
        output_entry = Entry(
            output_frame,
            textvariable=self.output_folder,
            font=("Arial", 9),
            relief=SUNKEN,
            bd=0
        )
        output_entry.pack(fill=X, side=LEFT, expand=True, padx=(0, 5))
        
        self.output_btn = Button(
            output_frame,
            text=self.t("output_browse"),
            command=self.select_output_folder,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            padx=8,
            pady=5,
            relief=FLAT
        )
        self.output_btn.pack(side=LEFT)
        
        # === ПРАВА КОЛОНА ===
        right_frame = Frame(main_frame, bg="#f0f0f0")
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))
        
        # Параметри
        self.params_label = Label(right_frame, text=self.t("params_section"), font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.params_label.pack(anchor=W, pady=(0, 10))
        
        params_frame = Frame(right_frame, bg="white", relief=SUNKEN, bd=1, padx=15, pady=15)
        params_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Мінімальна довжина маркера
        self.min_seg_label = Label(params_frame, text=self.t("min_segment"), font=("Arial", 10), bg="white")
        self.min_seg_label.pack(anchor=W, pady=(0, 5))
        
        self.min_segment = DoubleVar(value=7.0)
        min_seg_scale = Scale(
            params_frame,
            from_=1.0,
            to=30.0,
            orient=HORIZONTAL,
            variable=self.min_segment,
            bg="white",
            fg="#2c3e50"
        )
        min_seg_scale.pack(fill=X, pady=(0, 20))
        
        # Гучність музики
        self.volume_label = Label(params_frame, text=self.t("volume"), font=("Arial", 10), bg="white")
        self.volume_label.pack(anchor=W, pady=(0, 5))
        
        volume_frame = Frame(params_frame, bg="white")
        volume_frame.pack(fill=X, pady=(0, 20))
        
        self.volume_scale = Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=HORIZONTAL,
            variable=self.music_volume,
            command=lambda v: self.update_volume_label(float(v)/100),
            bg="white",
            fg="#9b59b6"
        )
        self.volume_scale.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        self.volume_percent = Label(volume_frame, text="30%", font=("Arial", 10, "bold"), bg="white", fg="#9b59b6", width=5)
        self.volume_percent.pack(side=LEFT)
        
        # Модель Whisper
        self.model_label = Label(params_frame, text=self.t("model_label"), font=("Arial", 10), bg="white")
        self.model_label.pack(anchor=W, pady=(0, 10))
        
        self.model_var = StringVar(value="small")
        model_frame = Frame(params_frame, bg="white")
        model_frame.pack(fill=X)
        
        for model in ["tiny", "small", "base", "medium"]:
            rb = Radiobutton(
                model_frame,
                text=model,
                variable=self.model_var,
                value=model,
                bg="white",
                font=("Arial", 9)
            )
            rb.pack(side=LEFT, padx=(0, 15))
        
        # Субтитри
        self.subtitles_var = BooleanVar(value=False)
        self.subtitles_cb = Checkbutton(
            params_frame,
            text=self.t("subtitles_option"),
            variable=self.subtitles_var,
            bg="white",
            font=("Arial", 10),
            pady=10
        )
        self.subtitles_cb.pack(anchor=W)
        
        # === НИЖНЯ ПАНЕЛЬ ===
        bottom_frame = Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Прогрес і логи в один рядок
        progress_frame = Frame(bottom_frame, bg="#f0f0f0")
        progress_frame.pack(fill=BOTH, expand=True)
        
        # Ліва частина - прогрес
        progress_left = Frame(progress_frame, bg="#f0f0f0")
        progress_left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        self.progress_label = Label(progress_left, text=self.t("progress"), font=("Arial", 11, "bold"), bg="#f0f0f0")
        self.progress_label.pack(anchor=W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_left,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(fill=X, pady=(0, 10))
        
        # Права частина - кнопки
        button_frame = Frame(progress_frame, bg="#f0f0f0")
        button_frame.pack(side=RIGHT, fill=BOTH, expand=False)
        
        self.start_btn = Button(
            button_frame,
            text=self.t("start_button"),
            command=self.start_processing,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=FLAT
        )
        self.start_btn.pack(side=LEFT, padx=(0, 8))
        
        self.clear_btn = Button(
            button_frame,
            text=self.t("clear_button"),
            command=self.clear_log,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=10,
            relief=FLAT
        )
        self.clear_btn.pack(side=LEFT)
        
        # Логи (під прогресом)
        self.log_label = Label(bottom_frame, text=self.t("log_label"), font=("Arial", 11, "bold"), bg="#f0f0f0")
        self.log_label.pack(anchor=W, pady=(10, 5))
        
        self.status_text = Text(
            bottom_frame,
            height=6,
            font=("Arial", 9),
            relief=SUNKEN,
            bd=1,
            bg="white"
        )
        self.status_text.pack(fill=BOTH, expand=True)
    
    def t(self, key, **kwargs):
        value = self.translations.get(key, {}).get(self.language_var.get(), key)
        return value.format(**kwargs)

    def update_ui_language(self):
        self.root.title(self.t("title"))
        self.menu_bar.entryconfig(self.language_menu_index, label=self.t("language_menu"))
        self.language_menu.entryconfig(0, label=self.t("language_uk"))
        self.language_menu.entryconfig(1, label=self.t("language_en"))
        self.title_label.config(text=self.t("title"))
        self.video_label.config(text=self.t("video_section"))
        self.music_btn.config(text=self.t("browse_music"))
        self.music_label.config(text=self.t("music_label"))
        self.output_label.config(text=self.t("output_section"))
        self.output_btn.config(text=self.t("output_browse"))
        self.params_label.config(text=self.t("params_section"))
        self.min_seg_label.config(text=self.t("min_segment"))
        self.volume_label.config(text=self.t("volume"))
        self.model_label.config(text=self.t("model_label"))
        self.subtitles_cb.config(text=self.t("subtitles_option"))
        self.progress_label.config(text=self.t("progress"))
        self.start_btn.config(text=self.t("start_button"))
        self.clear_btn.config(text=self.t("clear_button"))
        self.log_label.config(text=self.t("log_label"))
        self.video_display.config(text=self.t("video_none"))
        self.music_display.config(text=self.t("music_none"))

    def select_video(self):
        """Вибирає файл відео."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Відеофайли", "*.mp4 *.avi *.mov *.mkv"), ("Усі файли", "*.*")]
        )
        if file_path:
            self.video_path.set(file_path)
            file_name = os.path.basename(file_path)
            self.video_display.config(text=f"✓ {file_name}")
            self.log(self.t("video_selected", path=file_path))
    
    def select_music(self):
        """Вибирає файл музики."""
        file_path = filedialog.askopenfilename(
            filetypes=[("MP3 файли", "*.mp3"), ("Аудіофайли", "*.mp3 *.wav *.aac *.flac"), ("Усі файли", "*.*")]
        )
        if file_path:
            self.music_path.set(file_path)
            file_name = os.path.basename(file_path)
            self.music_display.config(text=f"✓ {file_name}")
            self.log(self.t("music_selected", path=file_path))
        else:
            self.music_path.set("")
            self.music_display.config(text=self.t("music_none"))
            self.log(self.t("select_music_cancel"))
    
    def update_volume_label(self, value):
        """Оновлює текст гучності."""
        self.volume_percent.config(text=f"{int(value*100)}%")
    
    def select_output_folder(self):
        """Вибирає папку для збереження."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
            self.log(self.t("folder_selected", path=folder))
    
    def log(self, message):
        """Додає повідомлення в лог."""
        self.status_text.insert(END, message + "\n")
        self.status_text.see(END)
        self.root.update()
    
    def clear_log(self):
        """Очищує лог."""
        self.status_text.delete(1.0, END)
    
    def start_processing(self):
        """Запускає обробку в окремому потоці."""
        if not self.video_path.get():
            messagebox.showerror(self.t("error_title"), self.t("select_video_error"))
            return
        
        if self.is_running:
            messagebox.showwarning(self.t("error_title"), self.t("processing_warning"))
            return
        
        self.is_running = True
        self.start_btn.config(state=DISABLED)
        self.progress_bar.start()
        
        # Запускаємо обробку в окремому потоці
        thread = threading.Thread(target=self.process_video)
        thread.daemon = True
        thread.start()
    
    def process_video(self):
        """Основна логіка обробки відео."""
        try:
            self.log("=" * 60)
            self.log("🎥 РОЗДІЛЮВАЧ ВІДЕО ЗА РОЗМІРАМИ ОДЯГУ")
            self.log("=" * 60 + "\n")
            
            video_path = self.video_path.get()
            output_folder = self.output_folder.get()
            min_segment_length = self.min_segment.get()
            model_name = self.model_var.get()
            add_subtitles = self.subtitles_var.get()
            
            # 1. Розпізнавання мови
            self.log(self.t("transcribing"))
            segments = self.transcribe_video(video_path, model_name)
            self.log(self.t("found_segments", count=len(segments)))
            
            # 2. Пошук маркерів
            self.log(self.t("searching_markers"))
            split_points = self.extract_split_points(segments, min_segment_length)
            
            # 2.5. Якщо потрібні субтитри, даємо можливість відредагувати текст
            if add_subtitles and split_points:
                self.log(self.t("prepare_subtitles"))
                edit_done_event = threading.Event()
                self.root.after(0, lambda: self.open_subtitles_editor(split_points, edit_done_event))
                edit_done_event.wait()
                self.log(self.t("found_segments", count=len(split_points)))
            
            # 3. Нарізання
            self.log(self.t("cutting_video"))
            self.cut_video_by_timestamps(video_path, split_points, output_folder, add_subtitles)
            
            self.log(self.t("process_complete"))
            messagebox.showinfo(self.t("success_title"), self.t("process_complete"))
            
        except Exception as e:
            self.log(f"\n❌ {self.t('processing_error', msg=str(e))}")
            messagebox.showerror(self.t("error_title"), self.t("processing_error", msg=str(e)))
        
        finally:
            self.is_running = False
            self.progress_bar.stop()
            self.start_btn.config(state=NORMAL)
    
    def transcribe_video(self, video_path, model_name="small"):
        """Розпізнає текст у відео."""
        self.log(self.t("loading_model"))
        model = whisper.load_model(model_name)
        
        self.log(self.t("analyzing"))
        result = model.transcribe(video_path, fp16=False, language="uk")
        return result["segments"]
    
    def is_age_marker(self, text):
        """Перевіряє, чи містить текст маркер віку."""
        months_pattern = r"\b(?:0-6|3-6|6-9|9-12|6-12)\b"
        years_keywords = r"(?:роч|рок|год|року|років|рочки|рочок)"
        word_numbers = r"(?:півтора|рік|два|три|чотири|п'ять|шість|сім|вісім|дев'ять|десять|одинадцять)"
        
        has_months = re.search(months_pattern, text, re.IGNORECASE)
        has_years_keyword = re.search(years_keywords, text, re.IGNORECASE)
        has_word_number = re.search(word_numbers, text, re.IGNORECASE)
        
        if has_months:
            return True, "вік (місяці)"
        if has_years_keyword:
            return True, "вік (роки)"
        if has_word_number:
            return True, "вік (словами)"
        
        range_pattern = r"\b(\d+)\s*[-–—]\s*(\d+)\b"
        match = re.search(range_pattern, text)
        
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            
            if start > 20 or end > 20:
                return False, None
            
            if (start in [0, 3, 6] and end in [6, 9, 12]) or \
               (start in [9, 12] and end >= 12):
                return True, "вік (місяці)"
            
            if start <= 10 and end <= 10 and (start < end):
                return True, "вік (роки)"
        
        return False, None
    
    def extract_split_points(self, segments, min_segment_length=5.0):
        """Шукає таймкоди маркерів."""
        split_points = []
        last_marker_time = -min_segment_length
        
        for seg in segments:
            text = seg["text"].strip()
            start_time = seg["start"]
            
            is_marker, marker_type = self.is_age_marker(text)
            
            if is_marker:
                if start_time - last_marker_time > min_segment_length:
                    split_points.append({
                        "start": start_time,
                        "text": text,
                        "pattern": marker_type,
                        "full_text": ""  # Для накопичування всього тексту
                    })
                    self.log(f"✓ [{start_time:.2f}s] ({marker_type}): «{text}»")
                    last_marker_time = start_time
        
        # Накопичуємо весь текст для кожного фрагменту
        for i, segment in enumerate(segments):
            seg_time = segment["start"]
            seg_text = segment["text"].strip()
            
            # Знаходимо, до якого фрагменту належить цей сегмент
            for j, split_point in enumerate(split_points):
                # Час початку цього фрагменту
                frag_start = split_point["start"]
                # Час початку наступного фрагменту (або кінець відео)
                if j + 1 < len(split_points):
                    frag_end = split_points[j + 1]["start"]
                else:
                    frag_end = float('inf')
                
                # Якщо сегмент належить цьому фрагменту, додаємо текст
                if frag_start <= seg_time < frag_end:
                    if split_point["full_text"]:
                        split_point["full_text"] += " " + seg_text
                    else:
                        split_point["full_text"] = seg_text
                    break
        
        self.log(f"\n📍 Знайдено {len(split_points)} блоків розмірів\n")
        return split_points
    
    def cut_video_by_timestamps(self, video_path, split_points, output_folder="output_clips", add_subtitles=False):
        """Нарізає відео і накладає музику."""
        if not split_points:
            self.log(self.t("no_markers"))
            return
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            self.log(self.t("created_folder", folder=output_folder))
        
        music_path = self.music_path.get()
        
        # Отримуємо тривалість
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
        self.log(f"📹 Загальна тривалість: {duration:.2f}с\n")
        
        timestamps = [p["start"] for p in split_points] + [duration]
        
        for i in range(len(timestamps) - 1):
            start = timestamps[i]
            end = timestamps[i + 1]
            clip_duration = end - start
            
            marker_text = split_points[i]["text"]
            full_text = split_points[i].get("full_text", marker_text)  # Весь текст фрагменту
            
            size_match = re.search(r"(\d+-\d+|\d+\s*(?:роч|рок|лед|год)\w*|\d+)", marker_text)
            if size_match:
                clean_text = size_match.group(1).replace(" ", "")
            else:
                clean_text = "".join(
                    c for c in marker_text[:15] if c.isalnum() or c in " -"
                ).strip()
            
            file_name = f"clip_{i+1:02d}_{clean_text.replace(' ', '_')}.mp4"
            txt_name = f"clip_{i+1:02d}_{clean_text.replace(' ', '_')}.txt"
            srt_name = f"clip_{i+1:02d}_{clean_text.replace(' ', '_')}.srt"
            output_path = os.path.join(output_folder, file_name)
            txt_path = os.path.join(output_folder, txt_name)
            srt_path = os.path.join(output_folder, srt_name)
            
            self.log(f"🎬 Фрагмент {i+1}/{len(timestamps)-1}")
            self.log(f"   {start:.2f}с - {end:.2f}с ({clip_duration:.2f}с)")
            self.log(f"   {file_name}")
            
            # Спочатку нарізаємо без музики
            temp_output = output_path.replace(".mp4", "_temp.mp4")
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start),
                "-to", str(end),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-q:a", "5",
                "-y",
                temp_output
            ]
            
            subprocess.run(cmd, capture_output=True, check=True, timeout=300)
            
            # Якщо потрібні субтитри, створюємо SRT файл
            if add_subtitles:
                self.log(f"   📝 Створення субтитрів...")
                self.create_srt_file(srt_path, full_text, start, end)
                # Накладаємо субтитри на відео
                temp_output_with_subs = temp_output.replace(".mp4", "_subs.mp4")
                self.add_subtitles_to_video(temp_output, temp_output_with_subs, srt_path, start)
                os.remove(temp_output)
                temp_output = temp_output_with_subs
            
            # Якщо музика вибрана, накладаємо її
            if music_path and os.path.exists(music_path):
                self.log(f"   🎵 Накладання музики...")
                self.add_music_to_video(temp_output, music_path, output_path, clip_duration, full_text)
                os.remove(temp_output)  # Видаляємо тимчасовий файл
            else:
                # Просто переіменовуємо
                os.rename(temp_output, output_path)
                # Додаємо метадані
                self.add_metadata_to_video(output_path, full_text)
            
            self.log(f"   ✓ Готово\n")
        
        self.log(f"✅ Усі файли збережено в: {output_folder}/")
    
    def add_music_to_video(self, video_path, music_path, output_path, duration, transcript_text):
        """Накладає музику на відео з регулюванням гучності і додає метадані."""
        # Отримуємо гучність (0.0-1.0)
        volume = self.music_volume.get() / 100.0
        
        # Створюємо фільтр для зацикленої музики з регулюванням гучності
        filter_complex = f"[1:a]aloop=loop=-1:size=2e+06,volume={volume}[music]; [0:a][music]amix=inputs=2:duration=first[audio]"
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[audio]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-q:a", "5",
            "-metadata", f"comment={transcript_text}",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
    
    def add_metadata_to_video(self, video_path, transcript_text):
        """Додає метадані (коментарі) до MP4 файлу."""
        temp_file = video_path.replace(".mp4", "_meta.mp4")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-c", "copy",
            "-metadata", f"comment={transcript_text}",
            "-y",
            temp_file
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=300)
            os.remove(video_path)
            os.rename(temp_file, video_path)
        except Exception as e:
            self.log(self.t("warning_metadata", msg=str(e)))
    
    def create_srt_file(self, srt_path, text, start_time, end_time):
        """Створює SRT файл для субтитрів."""
        # Розбиваємо текст на логічні частини (по реченнях або 15 символів)
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 < 50:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        # Розраховуємо час для кожної строки
        duration = end_time - start_time
        line_duration = duration / len(lines) if lines else duration
        
        srt_content = ""
        for i, line in enumerate(lines):
            line_start = start_time + (i * line_duration)
            line_end = start_time + ((i + 1) * line_duration)
            
            srt_content += f"{i+1}\n"
            srt_content += f"{self.format_time(line_start)} --> {self.format_time(line_end)}\n"
            srt_content += f"{line}\n\n"
        
        try:
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        except Exception as e:
            self.log(self.t("warning_srt", msg=str(e)))

    def open_subtitles_editor(self, split_points, done_event):
        """Відкриває вікно для редагування тексту субтитрів перед підготовкою файлів."""
        editor = Toplevel(self.root)
        editor.title("Редагування тексту субтитрів")
        editor.geometry("950x550")
        editor.transient(self.root)
        editor.grab_set()

        info_label = Label(editor, text="Відредагуйте текст для кожного фрагмента перед додаванням субтитрів:", font=("Arial", 11, "bold"))
        info_label.pack(anchor=W, padx=10, pady=10)

        editor_frame = Frame(editor)
        editor_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        list_frame = Frame(editor_frame)
        list_frame.pack(side=LEFT, fill=Y, padx=(0, 10), pady=5)

        listbox = Listbox(list_frame, width=40, height=24, exportselection=False)
        listbox.pack(fill=Y, expand=True)

        for i, point in enumerate(split_points):
            label = f"{i+1}: [{point['start']:.2f}s] {point['pattern']}"
            listbox.insert(END, label)

        text_frame = Frame(editor_frame)
        text_frame.pack(side=LEFT, fill=BOTH, expand=True, pady=5)

        segment_label = Label(text_frame, text="Текст фрагмента:", font=("Arial", 10, "bold"))
        segment_label.pack(anchor=W)

        text_widget = Text(text_frame, wrap=WORD, font=("Arial", 10), bg="white", relief=SUNKEN, bd=1)
        text_widget.pack(fill=BOTH, expand=True)

        selected_index = {"value": 0}

        def save_current_text():
            idx = selected_index["value"]
            if 0 <= idx < len(split_points):
                split_points[idx]["full_text"] = text_widget.get("1.0", END).strip()

        def load_selected_text(event=None):
            if not listbox.curselection():
                return
            save_current_text()
            idx = listbox.curselection()[0]
            selected_index["value"] = idx
            text_widget.delete("1.0", END)
            text_widget.insert(END, split_points[idx].get("full_text") or split_points[idx].get("text", ""))
            segment_label.config(text=f"Текст фрагмента {idx+1}: {split_points[idx]['pattern']}")

        def finish_editing():
            save_current_text()
            editor.grab_release()
            editor.destroy()
            done_event.set()

        listbox.bind("<<ListboxSelect>>", load_selected_text)
        if split_points:
            listbox.selection_set(0)
            load_selected_text()

        button_frame = Frame(editor)
        button_frame.pack(fill=X, pady=(0, 10), padx=10)

        save_btn = Button(button_frame, text="Зберегти і продовжити", command=finish_editing, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8)
        save_btn.pack(side=RIGHT)

        def on_close():
            finish_editing()

        editor.protocol("WM_DELETE_WINDOW", on_close)

    def format_time(self, seconds):
        """Перетворює секунди у формат SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def add_subtitles_to_video(self, input_video, output_video, srt_path, start_offset):
        """Накладає субтитри на відео."""
        # Коригуємо таймкоди SRT файлу на основі зсуву часу
        adjusted_srt = srt_path.replace(".srt", "_adjusted.srt")
        self.adjust_srt_timing(srt_path, adjusted_srt, -start_offset)
        
        cmd = [
            "ffmpeg",
            "-i", input_video,
            "-vf", f"subtitles={adjusted_srt.replace(chr(92), '/')}",
            "-c:a", "copy",
            "-y",
            output_video
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=300)
            os.remove(adjusted_srt)
        except Exception as e:
            self.log(self.t("warning_subtitles", msg=str(e)))
    
    def adjust_srt_timing(self, input_srt, output_srt, offset):
        """Коригує таймкоди в SRT файлі."""
        try:
            with open(input_srt, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсимо SRT файл і коригуємо часи
            entries = content.split('\n\n')
            adjusted_content = ""
            
            for entry in entries:
                lines = entry.strip().split('\n')
                if len(lines) >= 3:
                    num = lines[0]
                    timing = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    # Парсимо часи
                    times = timing.split(' --> ')
                    if len(times) == 2:
                        start = self.srt_time_to_seconds(times[0]) + offset
                        end = self.srt_time_to_seconds(times[1]) + offset
                        
                        # Переводимо назад в формат SRT
                        new_timing = f"{self.format_time(max(0, start))} --> {self.format_time(max(0, end))}"
                        adjusted_content += f"{num}\n{new_timing}\n{text}\n\n"
            
            with open(output_srt, 'w', encoding='utf-8') as f:
                f.write(adjusted_content)
        except Exception as e:
            self.log(self.t("warning_adjust", msg=str(e)))
    
    def srt_time_to_seconds(self, time_str):
        """Перетворює SRT час (HH:MM:SS,mmm) у секунди."""
        parts = time_str.replace(',', '.').split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds

if __name__ == "__main__":
    root = Tk()
    app = VideoSplitterApp(root)
    root.mainloop()
