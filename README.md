# University Advising System

A comprehensive web-based application designed to streamline the academic advising process for students and faculty. Built with **Django**, this system handles complex enrollment logic, role-based access, and real-time validation.

## 🚀 Key Features

*   **Role-Based Access Control (RBAC)**: Distinct dashboards and functionalities for **Students**, **Faculty**, and **Admins**.
*   **Smart Enrollment System**:
    *   **Conflict Detection**: Automatically prevents enrollment in courses with overlapping time slots.
    *   **Credit Limit Enforcement**: Ensures students do not exceed the maximum allowed credits (15 credits).
    *   **Capacity Management**: Real-time tracking of course seat availability.
    *   **Prerequisite Checks**: Prevents retaking of already completed courses.
*   **Faculty Tools**:
    *   View assigned advisees and their details.
    *   Manage course capacities.
    *   Override enrollment rules when necessary (Add/Drop for students).
*   **Admin Panel**:
    *   Manage courses and faculty assignments.
    *   Approve or reject special advising requests.

## 🛠️ Tech Stack

*   **Backend**: Python, Django
*   **Database**: SQLite (Development)
*   **Frontend**: HTML5, CSS3, Bootstrap 5

## ⚙️ Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yousufabdullahnirob/University-Advising-System.git
    cd University-Advising-System
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server**
    ```bash
    python manage.py runserver
    ```

6.  **Access the application**
    Open your browser and go to `http://127.0.0.1:8000/`

## 📝 Usage

*   **Student Login**: Access the student dashboard to view courses, check advising status, and enroll.
*   **Faculty Login**: Manage advisees and courses.
*   **Admin Login**: System-wide management.

---
*Built for CSE302 Project*
