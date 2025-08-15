# Airline Market Demand Analyzer

**Live Demo:** [**https://airline-market-demand-analyzer-beta.vercel.app/**](https://airline-market-demand-analyzer-beta.vercel.app/)

![Application Screenshot](.assets/insignts.png)
![Application Screenshot](.assets/data-table.png)

## Overview

This project is a full-stack web application designed for a group of hostels in Australia to analyze market demand trends in the airline industry. It provides actionable insights by fetching and processing flight data from multiple sources, helping non-technical users make informed decisions about pricing, promotions, and staffing during peak travel periods.

The application was built as part of a skills assessment to demonstrate proficiency in Python, API integration, web scraping, and modern full-stack development practices, with a focus on delivering a robust and user-friendly tool under a tight deadline.

## Core Features

-   🚀 **Multi-Source Data Aggregation:** Users can choose to fetch data from two distinct sources:
    -   **Amadeus API:** A reliable, industry-standard API for real-time flight offer data.
    -   **Web Scraper:** A resilient fallback that scrapes Google Flights (via SerpApi) to ensure data availability even if the primary API is down.
-   🧠 **AI-Powered Insights:** Fetched data is sent to a Large Language Model (Groq/Llama 3) with a carefully engineered prompt. The AI acts as a market analyst, generating a concise, bullet-point summary of key trends, competitive pricing, and actionable recommendations for the hostel managers.
-   📊 **Data Visualization:** The application displays price trends over time using Chart.js, providing a clear, visual representation of high and low-demand periods.
-   🛡️ **Resilient & Robust:** The application is built with graceful degradation in mind. It can handle API failures, empty data states, and malformed responses without crashing, ensuring a smooth user experience.
-   🎨 **Modern Frontend:** A clean, responsive, and intuitive user interface built with modern CSS and a card-based design for a professional look and feel.

## Tech Stack

| Category         | Technology                                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------------------- |
| **Frontend**     | `HTML5`, `CSS3`, `Vanilla JavaScript (ES6+)`, `Chart.js`                                                     |
| **Backend**      | `Python 3`, `FastAPI`, `Uvicorn`                                                                            |
| **Data Sources** | `Amadeus Self-Service API` (Flight Offers & Cheapest Dates), `SerpApi` (Google Flights Scraper)                 |
| **AI / LLM**     | `Groq API` (Llama 3)                                                                                         |
| **Deployment**   | **Backend:** `Render` <br> **Frontend:** `Vercel`                                                             |
| **Tooling**      | `Git`, `GitHub`, `Visual Studio Code`, `python-dotenv`                                                        |

## Getting Started Locally

To run this project on your local machine, follow these steps:

### 1. Prerequisites

-   Python 3.8+
-   A code editor (like VS Code) with a terminal
-   Git installed on your machine

### 2. Clone the Repository

```bash
git clone https://github.com/devanshmayatra/airline-market-demand-analyzer.git
cd airline-market-demand-analyzer
```

### 3. Set Up the Backend

1.  **Create and activate a Python virtual environment:**
    ```bash
    # For Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a file named `.env` in the root of the project directory. Copy the contents of `.env.example` (or the block below) into it and fill in your own API keys.

    ```
    # .env file
    AMADEUS_API_KEY="YOUR_AMADEUS_API_KEY"
    AMADEUS_SECRET_KEY="YOUR_AMADEUS_SECRET_KEY"
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    SERPAPI_API_KEY="YOUR_SERPAPI_API_KEY"
    ```

4.  **Run the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend API will now be running at `http://127.0.0.1:8000`.

### 4. Run the Frontend

1.  Open the `frontend` folder in your code editor.
2.  The easiest way to serve the `index.html` file is with a live server extension. For example, the **Live Server** extension for VS Code.
3.  Right-click on `index.html` and select "Open with Live Server".
4.  The application will open in your browser, typically at `http://127.0.0.1:5500`.

## Deployment

The application follows a modern, decoupled architecture:
-   The **FastAPI backend** is deployed as a Web Service on **Render**. It automatically builds and deploys from the `main` branch upon each push. Environment variables are configured securely in the Render dashboard.
-   The **static frontend** is deployed on **Vercel**. It is configured to serve the contents of the `/frontend` directory and is automatically rebuilt and deployed upon each push to the `main` branch. The production API URL is hardcoded in the `script.js` file for Vercel's environment.

## Key Learnings

This project served as an excellent exercise in real-world problem-solving:

-   **Graceful Degradation:** The initial Amadeus API for price trends was unreliable, returning `500` errors. The application was re-engineered to handle this failure gracefully, logging the error but proceeding with the available data rather than crashing.
-   **Handling AI Hallucinations:** When the web scraper initially returned no data, the AI would "hallucinate" a plausible-sounding report based on its persona. A guard clause was implemented on the frontend to prevent calling the AI with empty data, making the system more robust and reliable.
-   **Data Structure Adaptation:** The JSON structure from the web scraper was different from the API. This required creating a "translator" layer in the backend to normalize the data into a consistent format that the rest of the application could reliably consume.
