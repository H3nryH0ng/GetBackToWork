import customtkinter as ctk
import random
from typing import Callable

# --- Point System Class ---
class PointSystem:
    def __init__(self, initial_points=100):
        self.points = initial_points

    def get_points(self):
        return self.points

    def add_points(self, amount):
        self.points += amount

    def deduct_points(self, amount):
        self.points = max(0, self.points - amount)

# --- Casino Window Class ---
class CasinoWindow(ctk.CTkToplevel):
    def __init__(self, parent, point_system, on_points_update: Callable[[int], None]):
        super().__init__(parent)
        self.point_system = point_system
        self.on_points_update = on_points_update

        # Window setup
        self.title("Gamble Your Points Casino")
        self.geometry("400x500")
        self.configure(bg='#2C3E50')

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Current points label
        self.points_label = ctk.CTkLabel(
            self,
            text=f"Current Points: {point_system.get_points()}",
            text_color="white",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.points_label.pack(pady=20)

        # Slot machine display
        self.slot_frame = ctk.CTkFrame(self, fg_color="#2C3E50")
        self.slot_frame.pack(pady=20)

        self.slots = []
        for i in range(3):
            slot = ctk.CTkLabel(
                self.slot_frame,
                text="?",
                font=ctk.CTkFont(size=32, weight="bold"),
                width=50,
                text_color="white"
            )
            slot.pack(side="left", padx=10)
            self.slots.append(slot)

        # Spin button
        self.spin_button = ctk.CTkButton(
            self,
            text="SPIN! (Costs 10 points)",
            command=self.spin,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1ABC9C",
            hover_color="#16A085"
        )
        self.spin_button.pack(pady=20)

        # Result display
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            wraplength=350,
            justify="center",
            text_color="white",
            font=ctk.CTkFont(size=14)
        )
        self.result_label.pack(pady=20)

        # Possible outcomes
        self.outcomes = [
            ("🎯", "Extra Focus Points!", self.give_points),
            ("💡", "Productivity Tip!", self.show_tip),
            ("😳", "Dare Time!", self.show_dare),
            ("💀", "All Points Lost!", self.lose_all_points)
        ]

        # Productivity tips
        self.tips = [
            "Take a 5-minute break every 25 minutes (Pomodoro Technique)",
            "Use the 2-minute rule: if a task takes less than 2 minutes, do it now",
            "Start your day with the most important task",
            "Use the Eisenhower Matrix to prioritize tasks",
            "Practice deep work: focus on one task for 90 minutes",
            "Use the 80/20 rule: focus on the 20% of tasks that yield 80% of results",
            "Create a 'not-to-do' list to avoid distractions",
            "Use the 'eat the frog' method: tackle your hardest task first",
            "Batch similar tasks together",
            "Use the 'touch it once' rule: handle each task only once"
        ]

        # Dares
        self.dares = [
            "Text your mom you love her. No context.",
            "Post 'I love productivity!' on your social media",
            "Send a voice message to a friend saying 'I'm being productive!'",
            "Take a selfie with your most productive face and send it to a friend",
            "Record yourself doing a productivity dance and send it to a friend",
            "Call a friend and tell them about your productivity goals",
            "Post a screenshot of your current task on social media",
            "Send a motivational quote to 3 friends",
            "Record yourself saying 'I am a productivity machine!' and send it to a friend",
            "Take a video of yourself organizing your workspace and send it to a friend"
        ]

        # Disable spin button if not enough points
        self.update_spin_button()

    def update_spin_button(self):
        if self.point_system.get_points() < 10:
            self.spin_button.configure(state='disabled')
        else:
            self.spin_button.configure(state='normal')

    def spin(self):
        if self.point_system.get_points() < 10:
            return

        # Deduct points
        self.point_system.deduct_points(10)
        self.points_label.configure(text=f"Current Points: {self.point_system.get_points()}")
        self.update_spin_button()

        # Disable spin button during animation
        self.spin_button.configure(state='disabled')

        # Animate slots
        self.animate_slots()

    def animate_slots(self, iteration=0):
        if iteration < 20:  # Number of animation frames
            for slot in self.slots:
                outcome = random.choice(self.outcomes)
                slot.configure(text=outcome[0])
            self.after(100, lambda: self.animate_slots(iteration + 1))
        else:
            # Final result
            outcome = random.choice(self.outcomes)
            for slot in self.slots:
                slot.configure(text=outcome[0])

            # Show result
            self.result_label.configure(text=outcome[1])

            # Execute outcome
            outcome[2]()

            # Re-enable spin button
            self.update_spin_button()

    def give_points(self):
        points = random.randint(20, 50)
        self.point_system.add_points(points)
        self.points_label.configure(text=f"Current Points: {self.point_system.get_points()}")
        self.result_label.configure(
            text=f"{self.result_label.cget('text')}\nYou won {points} points!"
        )
        self.on_points_update(self.point_system.get_points())

    def show_tip(self):
        tip = random.choice(self.tips)
        self.result_label.configure(
            text=f"{self.result_label.cget('text')}\n\nProductivity Tip:\n{tip}"
        )

    def show_dare(self):
        dare = random.choice(self.dares)
        self.result_label.configure(
            text=f"{self.result_label.cget('text')}\n\nYour Dare:\n{dare}"
        )

    def lose_all_points(self):
        points = self.point_system.get_points()
        self.point_system.deduct_points(points)
        self.points_label.configure(text=f"Current Points: {self.point_system.get_points()}")
        self.result_label.configure(
            text=f"{self.result_label.cget('text')}\n\nYou lost all {points} points!"
        )
        self.on_points_update(self.point_system.get_points())

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Optional: "light", "dark", or "system"
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()

    point_system = PointSystem()

    def on_points_update(new_points):
        print(f"Updated points: {new_points}")

    app = CasinoWindow(root, point_system, on_points_update)
    root.mainloop()
