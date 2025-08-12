import os
import sys
import math
import subprocess
import threading
from pathlib import Path

# PyQt5 imports - minimal required
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QSpinBox, QGroupBox, QGridLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoSplitterWorker(QThread):
    """Worker thread for video splitting operations."""
    progress_updated = pyqtSignal(int)  # Progress percentage
    log_updated = pyqtSignal(str)       # Log message
    finished = pyqtSignal(bool, str)    # Success, message
    
    def __init__(self, video_path, output_dir, segment_minutes, segment_seconds):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.segment_duration = segment_minutes * 60 + segment_seconds  # Convert to total seconds
        self.is_running = True
        
    def run(self):
        try:
            self.log_updated.emit(f"Starting video split: {os.path.basename(self.video_path)}")
            
            # Get video duration
            duration = self.get_video_duration()
            if duration <= 0:
                self.finished.emit(False, "Could not determine video duration")
                return
                
            total_segments = math.ceil(duration / self.segment_duration)
            self.log_updated.emit(f"Video duration: {self.seconds_to_time(duration)}")
            self.log_updated.emit(f"Total segments to create: {total_segments}")
            
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Split video into segments
            video_name = Path(self.video_path).stem
            successful_segments = 0
            
            for i in range(total_segments):
                if not self.is_running:
                    break
                    
                start_time = i * self.segment_duration
                segment_num = i + 1
                
                # Calculate end time (don't exceed video duration)
                end_time = min(start_time + self.segment_duration, duration)
                actual_duration = end_time - start_time
                
                if actual_duration <= 1:  # Skip segments shorter than 1 second
                    continue
                
                self.log_updated.emit(f"Processing segment {segment_num}: {self.seconds_to_time(start_time)} - {self.seconds_to_time(end_time)}")
                
                # Create output filename
                output_filename = f"{video_name}_part_{segment_num:03d}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Split the segment
                success = self.split_segment(start_time, actual_duration, output_path)
                
                if success:
                    successful_segments += 1
                    self.log_updated.emit(f"Segment {segment_num} completed: {output_filename}")
                else:
                    self.log_updated.emit(f"Failed to create segment {segment_num}")
                
                # Update progress
                progress = int((segment_num / total_segments) * 100)
                self.progress_updated.emit(progress)
                
            if self.is_running:
                if successful_segments > 0:
                    self.finished.emit(True, f"Successfully split video into {successful_segments} segments")
                else:
                    self.finished.emit(False, "No segments were created successfully")
            else:
                self.finished.emit(False, "Operation cancelled by user")
                
        except Exception as e:
            self.log_updated.emit(f"Error: {str(e)}")
            self.finished.emit(False, f"Error: {str(e)}")
    
    def get_video_duration(self):
        """Get video duration in seconds using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', self.video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
                return duration
            else:
                # Fallback method using ffmpeg
                return self.get_duration_fallback()
                
        except Exception as e:
            self.log_updated.emit(f"Warning: Could not get precise duration: {e}")
            return self.get_duration_fallback()
    
    def get_duration_fallback(self):
        """Fallback method to get video duration."""
        try:
            cmd = [
                'ffmpeg', '-i', self.video_path, '-f', 'null', '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = result.stderr
            
            # Parse duration from ffmpeg output
            for line in output.split('\n'):
                if 'Duration:' in line:
                    duration_str = line.split('Duration:')[1].split(',')[0].strip()
                    return self.time_to_seconds(duration_str)
                    
            return 0
        except:
            return 0
    
    def split_segment(self, start_time, duration, output_path):
        """Split a single segment from the video."""
        try:
            # Build ffmpeg command
            cmd = ['ffmpeg', '-y']  # -y to overwrite existing files
            
            # Input file with start time
            cmd.extend(['-ss', str(start_time)])
            cmd.extend(['-i', self.video_path])
            
            # Duration
            cmd.extend(['-t', str(duration)])
            
            # Basic quality settings
            cmd.extend(['-c:v', 'libx264', '-crf', '23'])
            cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
            
            # Other settings
            cmd.extend(['-avoid_negative_ts', 'make_zero'])
            cmd.extend(['-movflags', '+faststart'])
            
            # Output file
            cmd.append(output_path)
            
            # Run ffmpeg
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout per segment
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            return result.returncode == 0 and os.path.exists(output_path)
            
        except subprocess.TimeoutExpired:
            self.log_updated.emit("Segment processing timed out")
            return False
        except Exception as e:
            self.log_updated.emit(f"Error processing segment: {e}")
            return False
    
    def time_to_seconds(self, time_str):
        """Convert time string (HH:MM:SS.ms) to seconds."""
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0
    
    def seconds_to_time(self, seconds):
        """Convert seconds to time string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def stop(self):
        """Stop the splitting process."""
        self.is_running = False

class VideoCutter(QMainWindow):
    """Video Cutter GUI."""
    
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.worker = None
        self.output_directory = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Video Cutter MVP")
        self.setMinimumSize(600, 500)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # File input section
        file_group = QGroupBox("Video Input")
        file_layout = QVBoxLayout(file_group)
        
        # Browse button
        self.browse_btn = QPushButton("Browse Video File")
        self.browse_btn.clicked.connect(self.browse_video)
        file_layout.addWidget(self.browse_btn)
        
        # File info
        self.file_info_label = QLabel("No file selected")
        file_layout.addWidget(self.file_info_label)
        
        main_layout.addWidget(file_group)
        
        # Settings section
        settings_group = QGroupBox("Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Segment duration
        settings_layout.addWidget(QLabel("Minutes:"), 0, 0)
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 999)
        self.minutes_spin.setValue(2)
        settings_layout.addWidget(self.minutes_spin, 0, 1)
        
        settings_layout.addWidget(QLabel("Seconds:"), 0, 2)
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setValue(30)
        settings_layout.addWidget(self.seconds_spin, 0, 3)
        
        # Output directory
        settings_layout.addWidget(QLabel("Output:"), 1, 0)
        self.output_btn = QPushButton("Select Output Folder")
        self.output_btn.clicked.connect(self.browse_output_directory)
        settings_layout.addWidget(self.output_btn, 1, 1, 1, 3)
        
        main_layout.addWidget(settings_group)
        
        # Process section
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout(process_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Cutting")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_cutting)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_cutting)
        button_layout.addWidget(self.stop_button)
        
        process_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        process_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(process_group)
        
        # Log section
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a video file to begin")
    
    def browse_video(self):
        """Browse for video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*)"
        )
        if file_path:
            self.load_video(file_path)
    
    def load_video(self, video_path):
        """Load a video file."""
        try:
            if not os.path.exists(video_path):
                QMessageBox.warning(self, "Error", "Video file does not exist!")
                return
            
            self.current_video = video_path
            filename = os.path.basename(video_path)
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            self.file_info_label.setText(f"File: {filename}\nSize: {file_size:.1f} MB")
            self.start_button.setEnabled(True)
            
            # Set default output directory
            if not self.output_directory:
                self.output_directory = os.path.join(os.path.dirname(video_path), "video_segments")
            
            self.statusBar().showMessage(f"Video loaded: {filename}")
            self.log_text.append(f"Video loaded: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load video:\n{str(e)}")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory",
            os.path.dirname(self.current_video) if self.current_video else ""
        )
        if directory:
            self.output_directory = directory
            self.statusBar().showMessage(f"Output: {os.path.basename(directory)}")
    
    def start_cutting(self):
        """Start the video cutting process."""
        if not self.current_video:
            QMessageBox.warning(self, "Error", "Please select a video file first!")
            return
        
        # Check if FFmpeg is available
        if not self.check_ffmpeg():
            QMessageBox.critical(
                self, "FFmpeg Required",
                "FFmpeg is required for video processing.\n\n"
                "Please install FFmpeg and make sure it's in your system PATH."
            )
            return
        
        # Get settings
        minutes = self.minutes_spin.value()
        seconds = self.seconds_spin.value()
        
        if minutes == 0 and seconds == 0:
            QMessageBox.warning(self, "Error", "Segment duration must be greater than 0!")
            return
        
        # Use output directory or create default
        output_dir = self.output_directory or os.path.join(
            os.path.dirname(self.current_video), "video_segments"
        )
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Start worker thread
        self.worker = VideoSplitterWorker(
            self.current_video, output_dir, minutes, seconds
        )
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.log_updated.connect(self.log_text.append)
        self.worker.finished.connect(self.cutting_finished)
        self.worker.start()
        
        self.statusBar().showMessage("Processing video...")
    
    def stop_cutting(self):
        """Stop the cutting process."""
        if self.worker:
            self.worker.stop()
            self.log_text.append("Stopping process...")
    
    def cutting_finished(self, success, message):
        """Handle cutting completion."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if success:
            self.progress_bar.setValue(100)
            self.statusBar().showMessage("Completed!")
            QMessageBox.information(self, "Success", message)
        else:
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Failed!")
            QMessageBox.warning(self, "Error", message)
        
        self.worker = None
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return result.returncode == 0
        except:
            return False
    
    def closeEvent(self, event):
        """Handle application close."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "Video processing is in progress. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Video Cutter MVP")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = VideoCutter()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()