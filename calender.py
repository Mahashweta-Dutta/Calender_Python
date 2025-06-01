import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import calendar
from datetime import datetime, timedelta
import json
import os

REMINDER_FILE = "reminders.json"

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return {}
    with open(REMINDER_FILE, 'r') as f:
        return json.load(f)

def save_reminders(reminders):
    with open(REMINDER_FILE, 'w') as f:
        json.dump(reminders, f, indent=4)

def get_today_reminders(reminders):
    today = datetime.today()
    date_str = today.strftime("%Y-%m-%d")
    today_weekday = today.weekday()  # 0 = Monday
    matches = []

    for date, data in reminders.items():
        if date == date_str:
            matches.append((date, data["text"]))
        elif data.get("repeat") == "daily":
            matches.append((date, data["text"]))
        elif data.get("repeat") == "weekly":
            original_date = datetime.strptime(date, "%Y-%m-%d")
            if original_date.weekday() == today_weekday:
                matches.append((date, data["text"]))
        elif data.get("repeat") == "monthly":
            original_date = datetime.strptime(date, "%Y-%m-%d")
            if original_date.day == today.day:
                matches.append((date, data["text"]))
    return matches

class CalendarApp:
    def __init__(self, master):
        self.master = master
        self.master.title("📅 Monthly Calendar with Smart Reminders")
        self.reminders = load_reminders()

        self.today = datetime.today()
        self.current_year = self.today.year
        self.current_month = self.today.month

        self.header = tk.Label(master, text="", font=("Arial", 16))
        self.header.pack(pady=10)

        nav_frame = tk.Frame(master)
        nav_frame.pack()

        tk.Button(nav_frame, text="<<", command=self.prev_month).grid(row=0, column=0)
        tk.Button(nav_frame, text=">>", command=self.next_month).grid(row=0, column=1)
        tk.Button(nav_frame, text="🔍 Search", command=self.search_reminders).grid(row=0, column=2)
        tk.Button(nav_frame, text="📤 Export", command=self.export_reminders).grid(row=0, column=3)

        self.calendar_frame = tk.Frame(master)
        self.calendar_frame.pack()

        self.draw_calendar()

        # Notify today's reminders
        today_notes = get_today_reminders(self.reminders)
        if today_notes:
            note_text = "\n".join([f"{d}: {t}" for d, t in today_notes])
            messagebox.showinfo("🔔 Reminders for Today", note_text)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for idx, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold")).grid(row=0, column=idx)

        month_calendar = calendar.monthcalendar(self.current_year, self.current_month)
        for row_idx, week in enumerate(month_calendar, start=1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    tk.Label(self.calendar_frame, text="").grid(row=row_idx, column=col_idx)
                else:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    btn_text = str(day)
                    if date_str in self.reminders:
                        btn_text += " 🔔"
                    btn = tk.Button(
                        self.calendar_frame,
                        text=btn_text,
                        width=5,
                        command=lambda d=date_str: self.open_reminder_dialog(d)
                    )
                    btn.grid(row=row_idx, column=col_idx)

    def open_reminder_dialog(self, date_str):
        current = self.reminders.get(date_str, {})
        existing_text = current.get("text", "")
        existing_repeat = current.get("repeat", "none")

        text = simpledialog.askstring("Set Reminder", f"Reminder for {date_str}:\n(Current: {existing_text})")
        if text is None:
            return

        if text.lower() == "delete":
            if date_str in self.reminders:
                del self.reminders[date_str]
                messagebox.showinfo("Deleted", "Reminder deleted.")
        else:
            repeat = simpledialog.askstring("Repeat", "Repeat? (none/daily/weekly/monthly):", initialvalue=existing_repeat)
            self.reminders[date_str] = {"text": text, "repeat": repeat or "none"}
            messagebox.showinfo("Saved", "Reminder saved.")

        save_reminders(self.reminders)
        self.draw_calendar()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.draw_calendar()

    def search_reminders(self):
        keyword = simpledialog.askstring("Search", "Enter date (YYYY-MM-DD) or keyword:")
        if not keyword:
            return

        results = []
        for date, data in self.reminders.items():
            if keyword in date or keyword.lower() in data.get("text", "").lower():
                results.append(f"{date}: {data['text']} (Repeat: {data.get('repeat', 'none')})")

        if results:
            messagebox.showinfo("Search Results", "\n".join(results))
        else:
            messagebox.showinfo("No Results", "No matching reminders found.")

    def export_reminders(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        with open(file_path, 'w') as f:
            for date, data in sorted(self.reminders.items()):
                f.write(f"{date} | {data['text']} | Repeat: {data.get('repeat', 'none')}\n")
        messagebox.showinfo("Exported", "Reminders exported successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
