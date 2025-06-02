import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import whisper
import threading

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import whisper
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies using PowerShell"""
    ps_script = """
    <#
      .SYNOPSIS
        Installs development tools without admin privileges.
      .DESCRIPTION
        This script installs:
        - Git
        - Chocolatey (portable)
        - Python 3.11.9
        - FFmpeg (via Chocolatey)
        - openai-whisper (via PIP)
      .NOTES
        File Name      : Install-DevTools.ps1
        Prerequisite   : PowerShell 5.1+
        No admin rights required
    #>

    # Set Error Action Preference
    $ErrorActionPreference = "Stop"

    # Function to add to PATH if not already present
    function Add-ToPath {
        param (
            [string]$PathToAdd
        )
    
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$PathToAdd*") {
            $newPath = $currentPath + [IO.Path]::PathSeparator + $PathToAdd
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            $env:PATH += [IO.Path]::PathSeparator + $PathToAdd
        }
    }

    # 1. Install Git (standalone portable version)
    Write-Host "Downloading and installing Git..." -ForegroundColor Cyan
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/PortableGit-2.45.1-64-bit.7z.exe"
    $gitInstaller = "$env:TEMP\PortableGit.7z.exe"
    $gitInstallDir = "$env:USERPROFILE\git"

    try {
        # Download Git portable
        (New-Object System.Net.WebClient).DownloadFile($gitUrl, $gitInstaller)
    
        # Extract to user directory
        if (-not (Test-Path $gitInstallDir)) {
            New-Item -ItemType Directory -Path $gitInstallDir | Out-Null
        }
    
        # Using 7z to extract (built into Windows 10+)
        Start-Process -Wait -FilePath $gitInstaller -ArgumentList "-o$gitInstallDir -y"
    
        # Add to PATH
        Add-ToPath -PathToAdd "$gitInstallDir\bin"
    
        Write-Host "Git installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to install Git: $_" -ForegroundColor Red
        exit 1
    }

    # 2. Install Chocolatey (portable)
    Write-Host "Installing Chocolatey (portable)..." -ForegroundColor Cyan
    $chocoInstallDir = "$env:USERPROFILE\chocoportable"
    $env:ChocolateyInstall = $chocoInstallDir

    try {
        # Create installation directory if it doesn't exist
        if (-not (Test-Path $chocoInstallDir)) {
            New-Item -ItemType Directory -Path $chocoInstallDir | Out-Null
        }
    
        # Set execution policy for this process
        Set-ExecutionPolicy Bypass -Scope Process -Force
    
        # Install Chocolatey
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
        # Add Chocolatey to PATH
        Add-ToPath -PathToAdd "$chocoInstallDir\bin"
    
        Write-Host "Chocolatey installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to install Chocolatey: $_" -ForegroundColor Red
        exit 1
    }

    # 3. Install Python 3.11.9 (user installation)
    Write-Host "Installing Python 3.11.9..." -ForegroundColor Cyan
    $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-3.11.9.exe"

    try {
        # Download Python installer
        (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $pythonInstaller)
    
        # Install Python for current user
        $pythonInstallArgs = @(
        "/quiet",
        "InstallAllUsers=0",
        "PrependPath=1",
        "Include_test=0",
        "Include_launcher=0",
        "SimpleInstall=1"
    )
    
    Start-Process -Wait -FilePath $pythonInstaller -ArgumentList $pythonInstallArgs
    
    Write-Host "Python 3.11.9 installed successfully" -ForegroundColor Green
    
    # Refresh PATH to ensure Python is available
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    }
    catch {
        Write-Host "Failed to install Python: $_" -ForegroundColor Red
        exit 1
    }

    # 4. Install FFmpeg using Chocolatey
    Write-Host "Installing FFmpeg via Chocolatey..." -ForegroundColor Cyan
    try {
        & "$chocoInstallDir\bin\choco.exe" install ffmpeg -y --no-progress
        Write-Host "FFmpeg installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to install FFmpeg: $_" -ForegroundColor Red
        exit 1
    }

    # 5. Install openai-whisper using pip
    Write-Host "Installing openai-whisper via pip..." -ForegroundColor Cyan
    try {
        # Ensure pip is up to date
        python -m pip install --upgrade pip
    
        # Install whisper
        python -m pip install git+https://github.com/openai/whisper.git
    
        Write-Host "openai-whisper installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to install openai-whisper: $_" -ForegroundColor Red
        exit 1
    }

    Write-Host "All components installed successfully!" -ForegroundColor Green
    """
    
    try:
        # Save PS script to temp file
        temp_ps = os.path.join(os.environ['TEMP'], 'install_whisper.ps1')
        with open(temp_ps, 'w') as f:
            f.write(ps_script)
        
        # Execute PowerShell script
        subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-File', temp_ps
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Installation Error", f"Failed to install dependencies: {e}")
        return False
"""Run the Whisper GUI application"""
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
    if not check_dependencies():
        root = tk.Tk()
        root.withdraw()  # Hide main window
        if messagebox.askyesno(
            "Install Dependencies",
            "Required components not found. Install them now? (This may take a while)"
        ):
            if install_dependencies():
                messagebox.showinfo("Success", "Installation completed successfully!")
                # Restart the application
                python = sys.executable
                os.execl(python, python, *sys.argv)
            else:
                sys.exit(1)
        else:
            sys.exit(0)
    
    # Run the GUI if dependencies are installed
    root = tk.Tk()
    app = WhisperTranscriberApp(root)
    root.mainloop()
