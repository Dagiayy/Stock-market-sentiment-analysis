### **README for `task-1` Branch**


---


#### **Branch Overview**
The `task-1` branch encapsulates all work completed during the first phase of the project, focusing on setting up the development environment, performing exploratory data analysis (EDA), and laying the groundwork for subsequent tasks. This branch serves as the foundation for the project and ensures a clean, modular structure for future development.

---

#### **Purpose**
The primary goal of this branch is to:
1. Set up a reproducible Python environment and integrate it with GitHub for version control.
2. Perform an in-depth exploratory data analysis (EDA) on the financial news dataset to uncover patterns, trends, and insights.
3. Document findings and prepare the repository for quantitative and correlation analyses in subsequent tasks.

---

#### **Folder Structure**
The repository follows a structured organization to ensure modularity and ease of navigation. Below is the folder structure used in this branch:

```
├── .vscode/
│   └── settings.json                # IDE-specific settings
├── .github/
│   └── workflows
│       ├── unittests.yml            # GitHub Actions workflow for CI/CD
├── .gitignore                       # Specifies files/directories to ignore in Git
├── requirements.txt                 # List of Python dependencies
├── README.md                        # Project documentation
├── src/
│   ├── __init__.py                  # Placeholder for reusable Python scripts
├── notebooks/
│   ├── __init__.py                  # Placeholder for Jupyter notebooks
│   └── README.md                    # Documentation for notebooks
├── tests/
│   ├── __init__.py                  # Placeholder for unit tests
└── scripts/
    ├── __init__.py                  # Placeholder for standalone scripts
    └── README.md                    # Documentation for scripts
```

---

#### **Key Activities Completed**
1. **Environment Setup**:
   - Created and activated a Python virtual environment.
   - Installed required dependencies listed in `requirements.txt`.
   - Ensured compatibility with Python version 3.8 or higher.

2. **Git Version Control**:
   - Established a GitHub repository to host the codebase.
   - Created the `task-1` branch to isolate work related to EDA.
   - Committed work regularly with descriptive commit messages.

3. **CI/CD Integration**:
   - Configured a `.github/workflows/unittests.yml` file for automated testing using GitHub Actions.
   - Ensured automated checks for code quality and functionality.

4. **Exploratory Data Analysis (EDA)**:
   - **Descriptive Statistics**:
     - Analyzed headline lengths and identified trends in textual data.
     - Counted articles per publisher to identify the most active contributors.
   - **Date and Time Trends**:
     - Explored publication frequency over time (daily, monthly, yearly).
     - Identified spikes in article publications during significant market events.
   - **Text Analysis**:
     - Used Natural Language Processing (NLP) techniques to extract common keywords and topics from headlines.
     - Applied Latent Dirichlet Allocation (LDA) for topic modeling.
   - **Publisher Analysis**:
     - Identified top publishers and extracted unique domains from email-based publisher names.
   - **Visualization**:
     - Created plots to visualize trends, such as publishing times, day-of-week patterns, and topic distributions.

---

#### **How to Use This Branch**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Dagiayy/Stock-market-sentiment-analysis
   cd Week1-Challenge
   ```

2. **Set Up the Environment**:
   - Create and activate a virtual environment:
     ```bash
     python3 -m venv myenv
     source myenv/bin/activate  # On Windows: myenv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run Notebooks**:
   - Navigate to the `notebooks/` folder and open the EDA notebook using Jupyter:
     ```bash
     jupyter notebook
     ```

4. **Run Tests**:
   - Execute unit tests in the `tests/` folder:
     ```bash
     pytest tests/
     ```

5. **Explore Visualizations**:
   - Review the visualizations in the notebooks or re-run the code to generate updated plots.

---

#### **Key Findings**
- **Headline Lengths**: The average headline length was approximately **73 characters**, with most headlines ranging between **47 and 87 characters**.
- **Publishers**: **Benzinga.com** dominated the dataset, accounting for a significant portion of the articles.
- **Publication Trends**:
  - Articles were predominantly published during business hours, with peaks around **9 AM to 10 AM UTC** and **4 PM to 5 PM UTC**.
  - A notable spike in article volume occurred in **2020**, likely due to market volatility during the COVID-19 pandemic.
- **Topics**: LDA identified key themes such as price targets, earnings reports, and market movements.

---

#### **Challenges Encountered**
1. **Missing Values**: A significant portion of the dataset had missing or invalid `date` values, requiring careful handling.
2. **Text Preprocessing**: Cleaning and tokenizing headlines was complex but essential for meaningful topic modeling.
3. **Computational Complexity**: Processing ~1.4 million rows with LDA was resource-intensive.

---

#### **Next Steps**
1. Merge `task-1` into `main` using a Pull Request (PR).
2. Create a new branch (`task-2`) for quantitative analysis using TA-Lib and PyNance.
3. Continue refining the dataset and preparing it for sentiment and correlation analyses.

---

#### **Contributors**
- **Dagmawi Ayenew**: Conducted EDA, implemented text analysis, and documented findings.

---

#### **References**
- [TextBlob Documentation](https://textblob.readthedocs.io/en/dev/)
- [TA-Lib Python Documentation](https://github.com/ta-lib/ta-lib-python)
- [Data Engineering Best Practices](https://www.altexsoft.com/blog/data-engineer-role/)

---

This README provides a comprehensive overview of the `task-1` branch, ensuring clarity and reproducibility for collaborators and reviewers. Let me know if you'd like any additional sections or refinements!