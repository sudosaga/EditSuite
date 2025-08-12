#  EditSuite


A professional, modern GUI application for splitting videos into smaller segments with precision and ease.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-latest-green.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-required-red.svg)


##  Overview
 
**EditSuite** is a powerful, user-friendly video splitting tool that allows you to cut large videos into smaller, manageable segments. Whether you're preparing content for social media, creating video tutorials, or organizing your video library, this tool provides professional-grade video processing with an intuitive interface.

### Supported Formats

- **Input**: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V
- **Output**: MP4 (H.264 with AAC audio)

## 🛠 Installation & Setup

### Prerequisites

1. **Python 3.7+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - Required for video processing

#### Installing FFmpeg

**Windows:**
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to your system PATH
4. Verify installation: Open CMD and run `ffmpeg -version`

**macOS:**
```bash
# Using Homebrew
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Python Dependencies

Install required packages:

```bash
pip install PyQt5
```

### Quick Start

1. Clone or download the repository
2. Install dependencies
3. Run the application:

```bash
python EditSuite.py
```
=
##  Building Executable

### Using PyInstaller

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Create Executable**
   ```bash
   pyinstaller --onefile --windowed --name "EditSuite" EditSuite.py
   ```

3. **Advanced Build (Recommended)**
   ```bash
   pyinstaller --onefile --windowed --name "EditSuite" --icon=icon.ico --add-data "README.md;." EditSuite.py
   ```

### Build Options Explained

- `--onefile`: Creates a single executable file
- `--windowed`: Removes console window (GUI only)
- `--name`: Sets the executable name
- `--icon`: Adds custom icon (optional)
- `--add-data`: Includes additional files

### Distribution Notes

- **FFmpeg Requirement**: Users must install FFmpeg separately
- **Executable Size**: ~15-20MB (includes PyQt5)
- **Compatibility**: Windows 10+, macOS 10.14+, Linux (major distros)

## 📁 Project Structure

```
EditSuite/
├── EditSuite.py           # Main application file
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
├── build/                 # PyInstaller build files
├── dist/                  # Generated executables
└── examples/              # Example videos (optional)
```

## 🔧 Configuration

### Default Settings
- **Segment Duration**: 2 minutes 20 seconds
- **Quality**: High (CRF 18)
- **Audio**: Enabled
- **Output**: `video_segments/` folder next to input video

### Environment Variables
- `FFMPEG_PATH`: Custom FFmpeg installation path
- `OUTPUT`: Default output directory

## 🐛 Troubleshooting

### Common Issues

**"FFmpeg not found" Error**
- Ensure FFmpeg is installed and in system PATH
- Test with `ffmpeg -version` in terminal/command prompt

**Application won't start**
- Check Python version (3.7+ required)
- Verify PyQt5 installation: `pip show PyQt5`

**Video processing fails**
- Check video file isn't corrupted
- Ensure sufficient disk space for output segments
- Try a different video format

**Slow processing**
- Lower quality setting for faster processing
- Close other applications to free system resources
- Use SSD storage for better performance

### Performance Tips

- **Use High Quality** only for final outputs
- **Medium Quality** for most use cases
- **Remove Audio** if not needed (faster processing)
- **Larger segments** process faster than many small ones

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Use GitHub Issues to report problems
2. **Feature Requests**: Suggest new functionality
3. **Code Contributions**: Fork, improve, and submit pull requests
4. **Documentation**: Help improve this README


## 📋 Requirements

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for application, additional space for video processing
- **CPU**: Multi-core processor recommended for faster processing

### Python Dependencies
```
PyQt5>=5.15.0
```

### External Dependencies
- **FFmpeg**: Latest version recommended
- **System codecs**: H.264 and AAC support

##  Use Cases

### Content Creation
- **YouTube Videos**: Split long recordings into episodes
- **Social Media**: Create clips for Instagram, TikTok
- **Tutorials**: Break down long tutorials into chapters

### Professional Use
- **Video Editing**: Prepare segments for editing software
- **Archival**: Organize large video files
- **Distribution**: Create smaller files for easier sharing

### Personal Use
- **Home Videos**: Split family recordings by event
- **Backup**: Create manageable backup segments
- **Storage**: Reduce single file sizes for cloud storage

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Initial release
- ✅ Modern PyQt5 interface
- ✅ FFmpeg integration
- ✅ Drag & drop support
- ✅ Real-time progress tracking
- ✅ Quality presets
- ✅ Audio options
- ✅ GitHub integration

### Planned Features (v1.1.0)
- 🔄 Batch file processing
- 🔄 Video preview thumbnails
- 🔄 Custom naming patterns
- 🔄 Resume interrupted processing
- 🔄 Command-line interface

### Developer
- **GitHub**: [@harik0411](https://github.com/harik0411/)
- **Support**: ⭐ Star the repository if you find it useful!
