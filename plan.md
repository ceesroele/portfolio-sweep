# Plan

## Minimum Viable Product

### First iteration

1. General application
   - [x] Rewrite generation of individual charts as plugins
   - [x] Make configurable what charts are displayed in a report
   - [ ] Make template location configurable (so all can create their own "branded" templates)
        (skipped, non-trivial and not so relevant now)
   - [x] Create a separate configuration for development (minimize everything that is not under current development)

2. Features of reports
   - [x] Add time spent reporting in overview
   - [x] Add estimations reporting in overview
   - [x] Create timeline chart display estimations and time spent (total estimations, growth up of time spent)


### Second iteration

1. General application
    - [x] Use pandas for data transfer between collection and visualization for one chart
    - [ ] Based on experience with first chart: use pandas for all current charts where this makes sense
    - [ ] Create a new chart straight from pandas

2. Features of reports
    - [ ] Create backlog report with ranked overview of all issues
    - [ ] Add dependencies and their status (Open/Closed) to the backlog report
    - [ ] Add tree diagram for Initiatives