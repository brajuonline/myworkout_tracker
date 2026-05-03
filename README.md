# MyWorkoutTracker

A simple local-only workout tracker built with Python and Kivy.

## Features
- Add strength workouts (`Push-ups`, `Squats`, or custom strength exercise)
- Add timer workouts (`Plank` or custom timer exercise)
- Save workouts locally in `workouts.json`
- Delete workouts from history

## Run
1. Install Kivy:
   ```bash
   pip install kivy
   ```
2. Run the app from the project root:
   ```bash
   python run.py
   ```

## Project structure
- `app/main.py` — app logic and local storage
- `app/workouttracker.kv` — UI layout
- `run.py` — entry point that starts the app

## Notes
- Data is stored locally in the app user data directory on the device.
- Exercise choices are loaded from an external source in `app/exercise_catalog.py`.
- Custom exercises are stored persistently in `exercises.json`.
- The UI is defined in `app/workouttracker.kv`.

## Android deployment
1. Install Buildozer on a Linux system or WSL environment.
2. From the project root, run:
   ```bash
   buildozer android debug
   ```
3. The generated APK will be in `bin/` when the build finishes.

### Notes for Android
- `main.py` is the Android entrypoint.
- `buildozer.spec` now includes `icon.png` and `presplash.png` for the Android package.
- `android.permissions = INTERNET` is disabled so the app is packaged as offline-only.
- If you want a release build later, use:
   ```bash
   buildozer android release
   ```
