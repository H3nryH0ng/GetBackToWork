import json
import time
from datetime import datetime, date
from typing import Dict, List, Optional
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PointSystem:
    def __init__(self):
        self.points_data = self._load_points_data()
        self.current_streak = 0
        self.last_activity_time = time.time()
        self.daily_points_earned = 0
        self.daily_points_spent = 0

    def _load_points_data(self) -> Dict:
        """Load points history from JSON file."""
        try:
            with open(settings.POINTS_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Points history file not found. Creating new one.")
            return settings.DEFAULT_POINTS_HISTORY

    def _save_points_data(self):
        """Save points history to JSON file."""
        try:
            with open(settings.POINTS_HISTORY_FILE, 'w') as f:
                json.dump(self.points_data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving points data: {str(e)}")

    def _update_daily_report(self, points_earned: int, points_spent: int, 
                           productive_time: int, entertainment_time: int):
        """Update daily report with activity data."""
        try:
            with open(settings.DAILY_REPORTS_FILE, 'r') as f:
                reports = json.load(f)
        except FileNotFoundError:
            reports = []

        today = date.today().isoformat()
        today_report = next((r for r in reports if r['date'] == today), None)

        if not today_report:
            today_report = settings.DEFAULT_DAILY_REPORT.copy()
            today_report['date'] = today
            reports.append(today_report)

        today_report['points_earned'] += points_earned
        today_report['points_spent'] += points_spent
        today_report['productive_time'] += productive_time
        today_report['entertainment_time'] += entertainment_time
        if points_earned > 0:
            today_report['streaks'] += 1

        with open(settings.DAILY_REPORTS_FILE, 'w') as f:
            json.dump(reports, f, indent=4)

    def calculate_points(self, category: str, time_spent: float) -> int:
        """
        Calculate points based on category and time spent.
        Returns: Points earned (positive) or spent (negative)
        """
        if not category:
            return 0

        # Reset daily counters if it's a new day
        current_date = date.today().isoformat()
        if self.points_data.get('last_date') != current_date:
            self.daily_points_earned = 0
            self.daily_points_spent = 0
            self.points_data['last_date'] = current_date

        # Calculate base points
        intervals = time_spent / settings.TIME_INTERVAL
        base_points = int(intervals * settings.POINTS_PER_INTERVAL)

        # Apply streak bonus for productivity
        if category == 'productivity':
            current_time = time.time()
            if current_time - self.last_activity_time <= settings.MONITOR_INTERVAL * 2:
                self.current_streak += time_spent
                if self.current_streak >= settings.STREAK_THRESHOLD:
                    base_points = int(base_points * (1 + settings.STREAK_BONUS))
            else:
                self.current_streak = 0
            self.last_activity_time = current_time

            # Apply daily cap
            if self.daily_points_earned + base_points > settings.DAILY_POINTS_CAP:
                base_points = settings.DAILY_POINTS_CAP - self.daily_points_earned
            self.daily_points_earned += base_points

        elif category == 'entertainment':
            # Convert to negative points for entertainment
            base_points = -base_points

            # Apply daily entertainment cap
            if abs(self.daily_points_spent + base_points) > settings.DAILY_ENTERTAINMENT_CAP:
                base_points = -(settings.DAILY_ENTERTAINMENT_CAP - self.daily_points_spent)
            self.daily_points_spent += abs(base_points)

        return base_points

    def update_points(self, points: int, category: str, time_spent: float):
        """Update points and history."""
        if points == 0:
            return

        # Update current points
        self.points_data['current_points'] += points

        # Update totals
        if points > 0:
            self.points_data['total_points_earned'] += points
        else:
            self.points_data['total_points_spent'] += abs(points)

        # Add to history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'points': points,
            'category': category,
            'time_spent': time_spent,
            'current_total': self.points_data['current_points']
        }
        self.points_data['history'].append(history_entry)

        # Update daily report
        if category == 'productivity':
            self._update_daily_report(points, 0, time_spent, 0)
        else:
            self._update_daily_report(0, abs(points), 0, time_spent)

        # Save changes
        self._save_points_data()

    def get_current_points(self) -> int:
        """Get current point balance."""
        return self.points_data['current_points']

    def get_daily_stats(self) -> Dict:
        """Get statistics for the current day."""
        try:
            with open(settings.DAILY_REPORTS_FILE, 'r') as f:
                reports = json.load(f)
            today = date.today().isoformat()
            return next((r for r in reports if r['date'] == today), 
                       settings.DEFAULT_DAILY_REPORT)
        except FileNotFoundError:
            return settings.DEFAULT_DAILY_REPORT

    def can_access_entertainment(self) -> bool:
        """Check if user has enough points for entertainment."""
        return self.points_data['current_points'] > 0 