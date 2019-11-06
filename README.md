# portfolio-sweep
Portfolio Sweep - generate unified reports on a set of differently structured projects in Jira

# Goal
Create unified reports on work planned and done out of Jira for a whole portfolio.

1. Avoid creating "dashboards" per project or team
   - Time consuming to configure and maintain
   - Unlikely to be or remain uniform
   - Relatively hard to navigate to and through

2. No navigation to reports needed (typical in Jira: go to project, go to reports, select the right report, select e.g. version, then see report)

3. Have a single overview of progress for the entire portfolio

# Assumptions
1. An extra Jira project can be created for project meta-data
2. No assumptions on methodology (Scrum or Kanban, storypoints or estimations in time)

# Plan

## Current status

[Proof of Concept](poc.md) is completed. It ties together connecting with the Jira Cloud, caching issues in a local database, using a graphical library to generate a number of charts (line chart, area chart, pie chart), and present the result in generated HTML using a templating system. 

Current development goals can be found in the [plan](plan.md)

# Installation
Details on installs are in [INSTALL.md](INSTALL.md)
