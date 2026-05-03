import json
import os
from datetime import datetime

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from .exercise_catalog import EXERCISE_CATALOG


class WorkoutTracker(BoxLayout):
    workouts = ListProperty([])
    exercise_categories = ListProperty([])
    category_selected = StringProperty("")
    exercise_options = ListProperty([])
    exercise_selected = StringProperty("")
    exercise_type = StringProperty("strength")
    exercises = []
    archive_data = []
    new_exercise_modal = ObjectProperty(None)
    archive_modal = ObjectProperty(None)
    delete_confirm_modal = ObjectProperty(None)
    archive_to_delete_id = StringProperty("")
    selected_archive_id = StringProperty("")
    new_exercise_name = StringProperty("")
    new_exercise_category = StringProperty("")
    new_exercise_type = StringProperty("strength")
    reps_input = StringProperty("")
    sets_input = StringProperty("")
    duration_input = StringProperty("")
    status_message = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_workouts()
        self.load_exercises()
        self.update_exercise_options()

    def get_storage_path(self):
        app = App.get_running_app()
        data_dir = app.user_data_dir if app else os.getcwd()
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "workouts.json")

    def get_exercises_path(self):
        app = App.get_running_app()
        data_dir = app.user_data_dir if app else os.getcwd()
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "exercises.json")

    def load_workouts(self):
        path = self.get_storage_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    self.workouts = json.load(handle)
            except Exception:
                self.workouts = []
        else:
            self.workouts = []

    def save_workouts(self):
        path = self.get_storage_path()
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.workouts, handle, indent=2)

    def get_archive_path(self):
        app = App.get_running_app()
        data_dir = app.user_data_dir if app else os.getcwd()
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "archives.json")

    def load_archives(self):
        path = self.get_archive_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
            except Exception:
                return []
        return []

    def save_archives(self, archives):
        path = self.get_archive_path()
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(archives, handle, indent=2)

    def end_session(self):
        if not self.workouts:
            self.status_message = "No workouts to archive."
            return

        archives = self.load_archives()
        session_data = {
            "id": int(datetime.now().timestamp() * 1000),
            "ended_at": datetime.now().isoformat(),
            "workouts": self.workouts,
        }
        archives.append(session_data)
        self.save_archives(archives)

        self.workouts = []
        self.save_workouts()
        self.update_workout_list()
        self.status_message = "Session archived. New session started."

    def open_archive_popup(self):
        if self.archive_modal is None:
            self.archive_modal = Factory.ArchiveModal()
        self.archive_data = self.load_archives()
        self.selected_archive_id = str(self.archive_data[0]["id"]) if self.archive_data else ""
        self.update_archive_list()
        self.update_archive_details()
        self.archive_modal.open()

    def update_archive_list(self):
        if self.archive_modal and "archive_list" in self.archive_modal.ids:
            self.archive_modal.ids.archive_list.data = [
                {
                    "session_id": str(session["id"]),
                    "session_label": f"{session['ended_at'][:19].replace('T', ' ')} — {len(session['workouts'])} workouts",
                    "is_selected": str(session["id"]) == self.selected_archive_id,
                }
                for session in self.archive_data
            ]
            try:
                self.archive_modal.ids.archive_list.refresh_from_data()
            except Exception:
                pass

    def update_archive_details(self):
        if not self.archive_modal or "archive_details" not in self.archive_modal.ids:
            return
        selected_session = next(
            (session for session in self.archive_data if str(session["id"]) == self.selected_archive_id),
            None,
        )
        if selected_session is None:
            self.archive_modal.ids.selected_archive_label.text = "Select a session to view details"
            self.archive_modal.ids.archive_details.data = []
            return

        self.archive_modal.ids.selected_archive_label.text = (
            f"Session ended {selected_session['ended_at'][:19].replace('T', ' ')} — {len(selected_session['workouts'])} workouts"
        )
        self.archive_modal.ids.archive_details.data = [
            {
                "detail_text": (
                    f"{workout['timestamp'][:19].replace('T', ' ')} — {workout['exercise_name']}"
                    + (
                        f" — {workout['reps']} reps x {workout['sets']} sets"
                        if workout['exercise_type'] == 'strength'
                        else f" — {workout['duration']} sec"
                    )
                )
            }
            for workout in sorted(
                selected_session['workouts'],
                key=lambda item: item['timestamp'],
                reverse=True,
            )
        ]

    def select_archive(self, session_id):
        self.selected_archive_id = str(session_id)
        self.update_archive_list()
        self.update_archive_details()
        if self.archive_modal and "archive_list" in self.archive_modal.ids:
            try:
                self.archive_modal.ids.archive_list.refresh_from_data()
            except Exception:
                pass

    def restore_archive(self, session_id):
        archives = self.load_archives()
        for session in archives:
            if str(session["id"]) == str(session_id):
                self.workouts = session["workouts"].copy()
                self.save_workouts()
                self.update_workout_list()
                self.status_message = "Archived session restored."
                if self.archive_modal:
                    self.archive_modal.dismiss()
                return
        self.status_message = "Archived session not found."

    def confirm_delete_archive(self, session_id):
        self.archive_to_delete_id = str(session_id)
        if self.delete_confirm_modal is None:
            self.delete_confirm_modal = Factory.DeleteConfirmModal()
        self.delete_confirm_modal.ids.confirm_text.text = (
            "Are you sure you want to delete this archived session? This cannot be undone."
        )
        self.delete_confirm_modal.open()

    def delete_archive(self):
        if not self.archive_to_delete_id:
            return
        archives = self.load_archives()
        archives = [s for s in archives if str(s["id"]) != self.archive_to_delete_id]
        self.save_archives(archives)
        self.archive_data = [s for s in self.archive_data if str(s["id"]) != self.archive_to_delete_id]
        if self.selected_archive_id == self.archive_to_delete_id:
            self.selected_archive_id = str(self.archive_data[0]["id"]) if self.archive_data else ""
        self.update_archive_list()
        self.update_archive_details()
        self.status_message = "Archived session deleted."
        if self.delete_confirm_modal:
            self.delete_confirm_modal.dismiss()

    def load_exercises(self):
        path = self.get_exercises_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    self.exercises = json.load(handle)
            except Exception:
                self.exercises = EXERCISE_CATALOG.copy()
        else:
            self.exercises = EXERCISE_CATALOG.copy()

        categories = sorted({item["category"] for item in self.exercises})
        self.exercise_categories = categories
        self.category_selected = categories[0] if categories else ""

    def save_exercises(self):
        path = self.get_exercises_path()
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.exercises, handle, indent=2)

    def update_exercise_options(self):
        options = [
            item["name"]
            for item in self.exercises
            if item["category"] == self.category_selected
        ]
        self.exercise_options = options or ["No exercises"]
        if self.exercise_selected not in self.exercise_options:
            self.exercise_selected = self.exercise_options[0]
            self.exercise_type = self.get_exercise_type(self.exercise_selected)

    def get_exercise_type(self, name):
        for item in self.exercises:
            if item["name"] == name:
                return item["type"]
        return "strength"

    def on_category_selected(self, *args):
        selected = args[-1] if args else self.category_selected
        self.category_selected = selected
        self.update_exercise_options()
        self.status_message = ""

    def on_exercise_selected(self, *args):
        selected = args[-1] if args else self.exercise_selected
        self.exercise_selected = selected
        self.exercise_type = self.get_exercise_type(selected)
        self.status_message = ""

    def on_exercise_type(self, *args):
        selected_type = args[-1] if args else self.new_exercise_type
        self.new_exercise_type = selected_type

    def open_new_exercise_popup(self):
        self.new_exercise_name = ""
        self.new_exercise_category = self.category_selected
        self.new_exercise_type = "strength"
        if self.new_exercise_modal is None:
            self.new_exercise_modal = Factory.NewExerciseModal()
        self.new_exercise_modal.open()

    def save_new_exercise(self):
        name = self.new_exercise_name.strip()
        if not name:
            self.status_message = "Enter a new exercise name."
            return

        if any(item["name"].lower() == name.lower() for item in self.exercises):
            self.status_message = "Exercise already exists."
            return

        new_exercise = {
            "name": name,
            "category": self.new_exercise_category,
            "type": self.new_exercise_type,
        }
        self.exercises.append(new_exercise)
        self.save_exercises()
        self.category_selected = self.new_exercise_category
        self.update_exercise_options()
        self.exercise_selected = name
        self.exercise_type = new_exercise["type"]
        self.new_exercise_name = ""
        self.new_exercise_type = "strength"
        self.status_message = "New exercise saved."
        if self.new_exercise_modal:
            self.new_exercise_modal.dismiss()

    def clear_form(self):
        self.reps_input = ""
        self.sets_input = ""
        self.duration_input = ""
        self.status_message = "Workout saved."

    def add_workout(self):
        exercise_name = self.exercise_selected
        exercise_type = self.exercise_type
        if not exercise_name:
            self.status_message = "Enter a custom exercise name."
            return

        reps = 0
        sets = 0
        duration = 0

        if exercise_type == "strength":
            try:
                reps = int(self.reps_input)
                sets = int(self.sets_input)
            except ValueError:
                self.status_message = "Enter valid reps and sets."
                return
            if reps <= 0 or sets <= 0:
                self.status_message = "Reps and sets must be greater than 0."
                return
        else:
            try:
                duration = int(self.duration_input)
            except ValueError:
                self.status_message = "Enter a valid duration in seconds."
                return
            if duration <= 0:
                self.status_message = "Duration must be greater than 0."
                return

        workout = {
            "id": int(datetime.now().timestamp() * 1000),
            "exercise_name": exercise_name,
            "exercise_type": exercise_type,
            "reps": reps,
            "sets": sets,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "completed": False,
        }
        self.workouts.insert(0, workout)
        self.save_workouts()
        self.update_workout_list()
        self.clear_form()

    def delete_workout(self, workout_id):
        self.workouts = [item for item in self.workouts if item["id"] != workout_id]
        self.save_workouts()
        self.status_message = "Workout deleted."

    def toggle_workout_complete(self, workout_id):
        for item in self.workouts:
            if item["id"] == workout_id:
                item["completed"] = not item.get("completed", False)
                status = "completed" if item["completed"] else "marked incomplete"
                self.status_message = f"Workout {status}."
                break
        self.save_workouts()
        self.update_workout_list()

    def build_row_text(self, workout):
        if workout["exercise_type"] == "strength":
            detail = f"{workout['reps']} reps x {workout['sets']} sets"
        else:
            detail = f"{workout['duration']} sec"
        return f"{workout['exercise_name']} — {detail} — {workout['timestamp'][:19].replace('T', ' ')}"

    def update_workout_list(self):
        if "workout_list" in self.ids:
            def sort_key(item):
                timestamp = datetime.fromisoformat(item["timestamp"]).timestamp()
                return (item.get("completed", False), -timestamp)

            sorted_items = sorted(self.workouts, key=sort_key)
            self.ids.workout_list.data = [
                {
                    "workout_text": self.build_row_text(workout),
                    "workout_id": workout["id"],
                    "workout_done": workout.get("completed", False),
                    "workout_button_text": "Undo" if workout.get("completed", False) else "Done",
                }
                for workout in sorted_items
            ]

    def on_workouts(self, instance, value):
        self.update_workout_list()

    def on_kv_post(self, base_widget):
        self.update_workout_list()


class MyWorkoutTrackerApp(App):
    def build(self):
        Builder.load_file(os.path.join(os.path.dirname(__file__), "workouttracker.kv"))
        root = WorkoutTracker()
        return root


if __name__ == "__main__":
    MyWorkoutTrackerApp().run()
