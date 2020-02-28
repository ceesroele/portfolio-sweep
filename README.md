# sweep
Sweep - generate unified reports on a set of differently structured projects in Jira

### New: Jupyter support

Sweep now supports JQL queries which result in a `QueryFrame`, which encapsulates several pandas `DataFrames`.
This allows for more readable operations on the data and for interactive development with Jupyter notebooks.

Check out the [example notebook](src/notebook_to_jira.ipynb)

# Goal
Create unified reports on work planned and done out of Jira for a whole portfolio.

1. Avoid creating "dashboards" per project or team
   - Time consuming to configure and maintain
   - Unlikely to be or remain uniform
   - Relatively hard to navigate to and through

2. No navigation to reports needed (typical in Jira: go to project, go to reports, select the right report, select e.g. version, then see report)

3. Have a single overview of progress for the entire portfolio

4. Use Jupyter and pandas `DataFrames` for comfortable interactive development of new functionality.

# Assumptions
1. An extra Jira project can be created for project meta-data
2. No assumptions on methodology (Scrum or Kanban, storypoints or estimations in time)

# Plan

## Current status

[Proof of Concept](poc.md) is completed. It ties together connecting with the Jira Cloud, caching issues in a local database, using a graphical library to generate a number of charts (line chart, area chart, pie chart), and present the result in generated HTML using a templating system. 

Current development goals can be found in the [plan](plan.md)

Actual changes and the reasons for them can be found in [changes](changes.md)

# Installation & running
Details on installation and running Sweep are in [INSTALL.md](INSTALL.md)

# Other JIRA data analysis projects
[jira metrics extract](https://github.com/rnwolf/jira-metrics-extract)
