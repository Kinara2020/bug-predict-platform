🔍 AI Software Bug Prediction & Code Quality Platform

Hi! I’m Kinara 👋

I built this project to explore how AI and machine learning can help developers find potential problems in their code before those problems become bigger issues.

While working on this idea, I wanted to bring a few things together in one place: bug-risk prediction, code quality checks, security scanning, and AI-assisted fixes. Instead of switching between different tools and manually reviewing every finding, the goal is to make the process easier to understand and manage.

This project is still evolving, and I’m using it to learn more about how these technologies can work together in a practical software development workflow.

🤔 What does this project do?

The idea is pretty simple: when code changes, the platform analyzes it and helps identify areas that might need attention.

Here’s what I’ve worked on:

* Bug prediction: Uses machine learning and code metrics to estimate how risky a file might be.
* Code quality checks: Uses Radon to measure code complexity and maintainability.
* Security scanning: Uses Bandit and Semgrep to find potentially unsafe code patterns.
* AI code review: Uses Google Gemini to review selected findings and provide additional context.
* AI-assisted fixes: Can suggest changes for selected issues and prepare them on a separate Git branch.
* Dashboard: Displays the analysis results so they’re easier to review.

The idea isn’t to let AI make every decision. I want developers to understand the findings, review the suggested changes, and decide what should happen next.

🔄 How does it work?

Here’s the basic flow:

1. A developer pushes code to GitHub or starts a scan manually.
2. The backend fetches the relevant files from the repository.
3. The analysis pipeline checks the code using Radon, Bandit, and Semgrep.
4. A machine learning model estimates bug risk using code metrics.
5. Gemini provides an additional review of selected findings.
6. The results appear on the React dashboard.
7. If a fix is requested, the system can prepare a proposed change on a separate branch for review.

GitHub
   ↓
FastAPI Backend
   ↓
Code Analysis
   ↓
ML Bug-Risk Prediction
   ↓
Gemini Review
   ↓
React Dashboard
   ↓
Review Findings
   ↓
Proposed Fix → Separate Branch

🧰 Tech stack

These are the main technologies used in the project:

* Frontend: React, Recharts
* Backend: FastAPI, PyGithub
* Workflow: LangGraph
* Machine learning: Python, scikit-learn, Gradient Boosting
* Code analysis: Radon
* Security scanning: Bandit, Semgrep
* AI integration: Google Gemini
* Version control: Git and GitHub APIs

🧠 A little about the machine learning part

One part of this project that interested me was using code metrics to estimate bug risk.

The model uses features such as lines of code, cyclomatic complexity, maintainability index, and comment ratio to make predictions.

The current version was trained using a modeled dataset based on assumed relationships between code complexity and defects. The reported evaluation results are approximately:

Metric	Result
Accuracy	0.83
F1 score	0.81
ROC-AUC	0.64

These results are from the current modeled dataset, so they shouldn’t be taken as proof of how well the model will perform on real-world code. Testing it on a properly labeled software-defect dataset is one of the improvements I’d like to make.

🛡️ Why keep a developer involved?

I didn’t want the system to automatically change code and push it directly into the main branch.

Instead, the intended workflow allows developers to review the findings, choose which files need attention, and inspect proposed changes before merging them.

AI-generated fixes can be incorrect, so keeping the changes separate makes them easier to check and test.

⚙️ Running the project locally

What you’ll need

* Python 3.10+
* Node.js 18+
* Git
* A GitHub token with the required permissions
* A Google Gemini API key

1. Clone the repository

git clone https://github.com/Kinara2020/bug-predict-platform.git
cd bug-predict-platform

2. Start the backend

cd backend
python -m venv venv

On Windows:

venv\Scripts\activate

On macOS or Linux:

source venv/bin/activate

Install the dependencies:

pip install -r requirements.txt

Configure the required environment variables using the project’s .env.example, if available. Add your GitHub token, Gemini API key, and webhook secret as needed. Keep your actual credentials private.

If you need to train the model:

python models/train_model.py

Start the backend:

uvicorn main:app --reload --port 8000

3. Start the frontend

Open another terminal from the project root:

cd frontend
npm install
npm run dev

Open the local URL shown in your terminal, usually http://localhost:5173.

Note: These instructions assume the folders and scripts are present at these locations in the current version of the repository.

📂 Project structure

bug-predict-platform/
├── backend/
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── fix_agent.py
│   ├── github_utils.py
│   ├── analysis/
│   │   ├── static_analysis.py
│   │   ├── semgrep_scan.py
│   │   ├── ml_bug_predictor.py
│   │   └── llm_review.py
│   └── models/
│       ├── train_model.py
│       └── bug_risk_model.pkl
└── frontend/
    └── src/
        └── App.jsx

🚧 What’s next?

There are a few things I’d like to improve as I continue working on this project:

* Test the bug-risk model on real-world datasets.
* Improve the reliability of risk predictions.
* Reduce false positives in code analysis.
* Improve the testing and verification of AI-generated fixes.
* Add more useful information to the dashboard.
* Explore automated feedback on pull requests.

💭 Final thoughts

This project has been a way for me to explore the practical side of combining machine learning, static analysis, and generative AI.

There’s still room to improve it, especially when it comes to evaluating the model on real-world data and making sure suggested fixes are reliable. But that’s also what makes the project interesting to work on.

Thanks for stopping by! 😊

Made by Kinara Patel

GitHub Repository
