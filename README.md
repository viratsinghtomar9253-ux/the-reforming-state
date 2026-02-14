# The Reframing Room

## Setup

1.  **Clone/Download** the repository.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**:
    -   Copy `.env.example` to `.env`.
    -   Add your `GEMINI_API_KEY` and `TWILIO_AUTH_TOKEN`.
4.  **Run the Backend (Flask)**:
    ```bash
    python app.py
    ```
5.  **Expose for Twilio (in a separate terminal)**:
    ```bash
    ngrok http 8000
    ```
    -   Updates the Twilio Sandbox "When a message comes in" URL to `https://<your-ngrok-url>/whatsapp`.
6.  **Run the Frontend (Streamlit)**:
    ```bash
    streamlit run dashboard.py
    ```

## Usage

-   Open the Streamlit dashboard in your browser.
-   Send a WhatsApp message to your Twilio Sandbox number.
-   Watch the message appear on the dashboard, reframed by the AI.
