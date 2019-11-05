# Plan

## Proof of Concept

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
* EXT - Jira project for work on external libraries, e.g. Plotly (JS and .py)

Epics in PLAN:
* Load from Jira
* Cache data
* Basic data reports (no charts)
* Burnup chart



## Minimum Viable Product

Elements of MVP:
* Create backlog report with ranked overview of all issues
* Add dependencies and their status (Open/Closed) to the backlog report
* Add time spent reporting in overview
* Add estimations reporting in overview
* Create timeline chart display estimations and time spent (total estimations, growth up of time spent)