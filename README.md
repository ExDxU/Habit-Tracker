# HABIT TRACKER 🦆
#### Video Demo: https://youtube.com/shorts/3c7CGSrUMyw?is=1BL1Mwvb5ecbmCSb

#### Description:
The **Habit Tracker 🦆** is a lightweight, responsive, and user-friendly web application designed to help users build, maintain, and monitor daily habits over time. Built with Python using the Flask framework, HTML5, CSS3, Bootstrap 5, and SQLite3, the platform offers a streamlined experience for personal development. The main core of the project relies on calculating real-time daily activity streaks, preventing duplicate task completions on the same day, and offering clean visual feedback on user performance.

Developing consistent daily habits can be challenging. Many habit-tracking applications are overcomplicated with unnecessary settings and overwhelming interface options. This application solves that problem by focusing purely on simplicity, speed, and immediate clarity: users log in, see what habits need attention today, mark them done with a single click, and watch their consistency streak grow.

---

### Project Structure & File Breakdown

The project follows a standard Flask web application architecture integrated with the CS50 SQL library. Below is a detailed summary of each file created and its role in the overall ecosystem:

* **`app.py`**: The main application controller. It initializes the Flask server, sets up session configurations, and interfaces directly with the SQLite database (`habits.db`). It contains all HTTP route handlers (`/`, `/register`, `/login`, `/logout`, `/add`, `/delete`, and `/complete`) as well as core backend logic functions such as `calculate_streak(habit_id)`.
* **`helpers.py`**: Contains helper functions and middle-layer decorators to improve maintainability and code structure:
  * `apology(message, code)`: Handles user input validation errors by storing danger-styled alerts via Flask's `flash()` function and redirecting the user back gracefully without losing site context.
  * `login_required(f)`: A custom view decorator that protects private application routes, ensuring unauthenticated users are redirected back to the `/login` screen.
* **`habits.db`**: SQLite database containing three interconnected tables:
  * `users`: Stores unique account credentials with hashed password strings generated via Werkzeug security tools (`id`, `username`, `hash`).
  * `habits`: Stores registered habits linked to specific accounts via foreign keys (`id`, `user_id`, `title`, `frequency`).
  * `habit_logs`: Tracks historical habit completions using ISO-formatted date strings (`id`, `habit_id`, `user_id`, `completed_at`).
* **`templates/layout.html`**: The master Jinja2 layout template. It defines the HTML5 document framework, imports Bootstrap 5 styles, builds the top navigation bar, and renders flash message alert containers dynamically.
* **`templates/index.html`**: The main dashboard page. Displays all habits belonging to the logged-in user, their active streak represented by a fire badge (🔥), interactive status completion buttons ("Concluir" / "✓ Feito hoje!"), and habit deletion triggers.
* **`templates/add.html`**: Form template for registering new habits with title validation and frequency choices.
* **`templates/login.html`** & **`templates/register.html`**: User authentication forms for registration and login handling with client-side and server-side checks.

---

### Key Features & Design Choices

During the development process, several architectural decisions were debated to ensure data integrity and optimal user experience:

#### 1. Streak Calculation Algorithm
The streak system had to be precise, resilient, and immune to skipped days. Instead of relying on static counters stored directly in the database table (which can become desynchronized), the `calculate_streak` function dynamically computes streaks upon request:
* It queries historical completion logs ordered chronologically in descending order using `SELECT DISTINCT completed_at`.
* It verifies whether the most recent log matches either **today** or **yesterday**. If the last entry is older than yesterday, the active streak resets to zero.
* It iterates sequentially backwards through historical completion dates using `datetime.timedelta(days=1)`. The streak counter increments as long as consecutively earlier dates are present in the dataset and breaks as soon as a gap is detected.

#### 2. Duplicate Submission Prevention
To protect database storage and prevent user manipulation (such as spamming the completion button to inflate stats), two layers of security were implemented:
* The SQL query inside `calculate_streak` uses `DISTINCT` to treat multiple logs recorded on the exact same calendar date as a single valid completion.
* The `/complete` route executes a pre-check query (`SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND completed_at = ?`). If a log already exists for the current day, additional insertions are ignored.

#### 3. User Feedback & Flash Alerts
Rather than redirecting users to an isolated error page (as seen in standard CS50 distribution code templates), the application overrides the traditional `apology` rendering behavior. It leverages Flask's `flash()` notification system and Bootstrap `alert-dismissible` components directly within `layout.html`. Errors redirect users smoothly back to their previous page (`request.referrer`), preserving form inputs and enhancing the user interface flow.
