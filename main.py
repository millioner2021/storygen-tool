import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QSpinBox, QComboBox, QListWidget, QFileDialog
)
from PyQt5.QtCore import Qt

class StoryGenApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StoryGen - Consistent Character Tool")
        self.setGeometry(200, 100, 800, 600)

        # API Key
        self.api_label = QLabel("Veo API Key:")
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Paste your Veo API key here...")

        self.check_api_btn = QPushButton("Check API")
        self.check_api_btn.clicked.connect(self.check_api)

        # Story settings
        self.story_label = QLabel("Story Title:")
        self.story_input = QLineEdit()
        self.story_input.setPlaceholderText("Enter your story idea...")

        self.num_label = QLabel("Number of Images:")
        self.num_spin = QSpinBox()
        self.num_spin.setValue(5)
        self.num_spin.setRange(1, 10)

        self.quality_label = QLabel("Quality:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Basic", "Detailed", "HD"])

        # Logs
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        # Preview
        self.preview_list = QListWidget()

        # Buttons
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)

        self.export_btn = QPushButton("Export Prompts")
        self.export_btn.clicked.connect(self.export_prompts)

        self.download_btn = QPushButton("Generate & Download")
        self.download_btn.clicked.connect(self.download_images)

        self.stop_btn = QPushButton("Stop")

        # Layout
        layout = QVBoxLayout()

        api_row = QHBoxLayout()
        api_row.addWidget(self.api_label)
        api_row.addWidget(self.api_input)
        api_row.addWidget(self.check_api_btn)

        story_row = QHBoxLayout()
        story_row.addWidget(self.story_label)
        story_row.addWidget(self.story_input)

        settings_row = QHBoxLayout()
        settings_row.addWidget(self.num_label)
        settings_row.addWidget(self.num_spin)
        settings_row.addWidget(self.quality_label)
        settings_row.addWidget(self.quality_combo)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.export_btn)
        btn_row.addWidget(self.download_btn)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)

        layout.addLayout(api_row)
        layout.addLayout(story_row)
        layout.addLayout(settings_row)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_box)
        layout.addWidget(QLabel("Preview:"))
        layout.addWidget(self.preview_list)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        self.prompts = []
        os.makedirs("outputs", exist_ok=True)

    def log(self, text):
        self.log_box.append(text)

    def check_api(self):
        api_key = self.api_input.text().strip()
        if api_key:
            self.log("✅ API Key loaded.")
        else:
            self.log("❌ No API key provided.")

    def start_processing(self):
        title = self.story_input.text().strip()
        if not title:
            self.log("❌ Please enter a story title.")
            return

        num_images = self.num_spin.value()
        self.prompts = []
        self.preview_list.clear()

        for i in range(num_images):
            prompt = f"Scene {i+1}: Illustration of {title}, consistent character style, cinematic, colorful"
            self.prompts.append(prompt)
            self.preview_list.addItem(f"Prompt {i+1}: {prompt}")
            self.log(f"Generated prompt {i+1}")

    def export_prompts(self):
        if not self.prompts:
            self.log("❌ No prompts to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Prompts", "prompts.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                for p in self.prompts:
                    f.write(p + "\n")
            self.log(f"✅ Prompts exported to {file_path}")

    def download_images(self):
        if not self.prompts:
            self.log("❌ Generate prompts first.")
            return

        api_key = self.api_input.text().strip()
        if not api_key:
            self.log("❌ API key is missing.")
            return

        headers = {"Authorization": f"Bearer {api_key}"}

        for i, prompt in enumerate(self.prompts, start=1):
            data = {"prompt": prompt, "model": "veo-3"}
            try:
                response = requests.post("https://api.veo.com/v1/images", headers=headers, json=data)

                if response.status_code == 200:
                    img_url = response.json()["data"][0]["url"]
                    img_data = requests.get(img_url).content
                    filename = f"outputs/scene_{i}.jpg"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    self.log(f"✅ Downloaded {filename}")
                else:
                    self.log(f"❌ Failed for scene {i}: {response.text}")
            except Exception as e:
                self.log(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StoryGenApp()
    window.show()
    sys.exit(app.exec_())
