# Jira Configuration for Sweep

Sweep requires a number of Jira configurations in order to connect the elements of a portfolio.


# Portfolio project

The different projects worked on are brought together by a Jira portfolio project. This should have at least
the issue types:
* Epic (the Epic is a saga)
* Task (the Task is a project)

Idea: I can automatically generate the project and its custom configuration, so I can really work with 
exactly the right concepts at portfolio level.


# Issue Links

Configure an issue Link

name: parent
outward bound: is parent of
inward bound: is child of

This link is to be used between issues in the PORT project and epics (preferably) that work is really about.	