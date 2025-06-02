import tkinter as tk
from tkinter import filedialog, messagebox
import whisper
import threading
import os

class WhisperTranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Transcription Tool")
        self.root.geometry("500x250")
        
        # Model loading flag
        self.model_loaded = False
        self.model = None
        
        # Create UI elements
        self.create_widgets()
        
        # Load whisper model in background
        self.load_model_in_background()

    def create_widgets(self):
        # Input file selection
        tk.Label(self.root, text="Input Audio/Video File:").pack(pady=(10, 0))
        self.input_path = tk.StringVar()
        tk.Entry(self.root, textvariable=self.input_path, width=50).pack(pady=5)
        tk.Button(self.root, text="Browse...", command=self.select_input_file).pack()

        # Output file selection
        tk.Label(self.root, text="Output Text File:").pack(pady=(10, 0))
        self.output_path = tk.StringVar()
        tk.Entry(self.root, textvariable=self.output_path, width=50).pack(pady=5)
        tk.Button(self.root, text="Browse...", command=self.select_output_file).pack()

        # Model selection
        tk.Label(self.root, text="Model Size:").pack(pady=(10, 0))
        self.model_size = tk.StringVar(value="base")
        model_options = ["tiny", "base", "small", "medium", "large"]
        tk.OptionMenu(self.root, self.model_size, *model_options).pack()

        # Transcribe button
        self.transcribe_btn = tk.Button(
            self.root, 
            text="Transcribe", 
            command=self.start_transcription_thread,
            state=tk.DISABLED
        )
        self.transcribe_btn.pack(pady=10)

        # Status label
        self.status = tk.StringVar(value="Loading whisper model...")
        tk.Label(self.root, textvariable=self.status).pack()

    def load_model_in_background(self):
        def load_model():
            try:
                self.status.set("Loading whisper model (this may take a while)...")
                self.model = whisper.load_model(self.model_size.get())
                self.model_loaded = True
                self.status.set("Ready to transcribe")
                self.transcribe_btn.config(state=tk.NORMAL)
            except Exception as e:
                self.status.set(f"Error loading model: {str(e)}")
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")

        threading.Thread(target=load_model, daemon=True).start()

    def select_input_file(self):
        filetypes = [
            ("Audio/Video files", "*.mp3 *.wav *.ogg *.flac *.m4a *.mp4 *.avi *.mov"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            # Suggest output filename if not set
            if not self.output_path.get():
                base = os.path.splitext(filename)[0]
                self.output_path.set(f"{base}_transcript.txt")

    def select_output_file(self):
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        filename = filedialog.asksaveasfilename(
            title="Select output file",
            filetypes=filetypes,
            defaultextension=".txt"
        )
        if filename:
            self.output_path.set(filename)

    def start_transcription_thread(self):
        if not self.model_loaded:
            messagebox.showwarning("Warning", "Model is still loading, please wait")
            return

        if not self.input_path.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return

        if not self.output_path.get():
            messagebox.showwarning("Warning", "Please select an output file")
            return

        # Disable button during transcription
        self.transcribe_btn.config(state=tk.DISABLED)
        self.status.set("Starting transcription...")
        
        # Start transcription in background thread
        threading.Thread(target=self.transcribe_audio, daemon=True).start()

    def transcribe_audio(self):
        try:
            self.status.set("Transcribing... (this may take a while)")

            # Perform transcription
            result = self.model.transcribe(self.input_path.get())
            
            # Save to file
            with open(self.output_path.get(), "w", encoding="utf-8") as f:
                f.write(result["text"])

            self.status.set("Transcription completed successfully!")
            messagebox.showinfo("Success", "Transcription completed successfully!")
            
        except Exception as e:
            self.status.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Transcription failed: {str(e)}")
        finally:
            self.transcribe_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperTranscriberApp(root)
    root.mainloop()
