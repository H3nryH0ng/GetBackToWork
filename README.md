# GetB@ck2Work

A Python desktop productivity app that rewards productive work with entertainment time through a point system.

## Features

- 🎯 Window monitoring to track productive and entertainment applications
- 💰 Point system with rewards and penalties
- 🎮 Entertainment app blocking when points are insufficient
- 📊 Daily statistics and productivity tracking
- 🎨 Modern, clean interface
- 🔔 System notifications
- 🎭 Fun features like Boss Mode and Haiku challenges

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GetB@ck2Work.git
cd GetB@ck2Work
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. The application will start in the system tray. Click the icon to show the main window.

3. Configure your settings:
   - Add/remove applications to productivity/entertainment categories
   - Adjust point rates and time intervals
   - Customize blocking behavior
   - Set up notifications

4. Start being productive! The app will:
   - Award points for productive work
   - Deduct points for entertainment
   - Block entertainment apps when points are insufficient
   - Show motivational messages and statistics

## Features in Detail

### Point System
- Earn 1 point per 5 minutes of productive work
- Lose 1 point per 5 minutes of entertainment
- 10% bonus after 1 hour of continuous productivity
- Daily caps: 100 points earned, 50 points spent

### App Blocking
- Three blocking levels: minimize, hide, terminate
- Anti-cheat detection
- Cross-platform compatibility

### Fun Features
1. Boss Mode: Instantly switch to a fake spreadsheet
2. Meme Punishments: Rick roll, motivational quotes
3. Productivity Police: Random work check-ins
4. Casino Minigame: Gamble your points
5. Pet System: Virtual productivity companion

## Configuration

The application can be configured through the settings window:
- Point rates and intervals
- App categories
- Blocking methods
- Theme and notifications
- Startup options

## Troubleshooting

Common issues and solutions:

1. **App not detecting windows**
   - Ensure you have the required permissions
   - Check if the app is running as administrator

2. **Points not updating**
   - Verify the app is running in the background
   - Check the app categories configuration

3. **Blocking not working**
   - Try a different blocking level
   - Check if the app has necessary permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all the open-source libraries used in this project
- Inspired by productivity apps and gamification techniques