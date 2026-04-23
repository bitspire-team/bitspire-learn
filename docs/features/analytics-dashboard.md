# Analytics Dashboard

## Overview
The Analytics Dashboard allows the visual representation of bulk JSON request logs inside a simple Python UI.

## Technical Decisions

### Tooling Choice
*   **Streamlit**: Chosen for the simple UI capabilities and dataframe rendering.
*   **Pandas**: Chosen instead of a distributed system (like Apache Spark) as a lightweight, built-in Spark-like dataframe capability. It is fast, easy to install inside a virtual environment (`.venv`), and seamlessly integrates with Streamlit's `st.dataframe()` for UI visualization.

### Implementation Details
*   Used standard libraries `glob` and `json` to batch load `.json` log files from the `requests/` directory. 
*   `pandas.json_normalize()` was implemented to flatten hierarchical structures within the request logs.
*   Utilized the `logging` package (over `print`) to log script executions explicitly in English for better traceability.
