# Proof of Concept

# Details
Include core elements of the reporting system for a single Initiative.

Elements of the Proof of Concept:
- [x] Connect to Jira
- [x] Retrieve Initiatives from Jira
- [x] Generate a report with an overview of Initiatives
- [x] Generate a report with detailed data per Initiative
- [x] Retrieve Issues for Initiative
- [x] Cache issues in SQL database
- [x] Include overview of issues in detailed data per Initiative
- [x] Include dependencies for Initiatives (GD)
- [x] Include dependencies for Issues
- [x] Create burn up chart with timeline displaying open and closed issues per Initiative
- [x] Create pie chart with issue types per initiative
- [x] Create cumulative flow chart per Initiative

Jira projects:
* PORT - portfolio, including Initiatives and Sagas (where a Saga is an Epic of Initiatives)
* PLAN - Jira project for creating this application
* GD - Jira project for UI/UX for this application (overkill, but it helps creating data on dependencies)

# Findings

1. Proof of Concept is technically successful
2. Need to use two python Jira libraries: neither offers all
3. Will need more than plotly.py as graphical library as it doesn't offer decent tree diagrams
4. Templating system works so well that extension with template configuration seems an easy next step
5. Need to find an alternative for "Teams" and "Accounts" which are notions from the "Tempo" system