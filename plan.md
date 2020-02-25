# Plan

## Minimum Viable Product

### Fourth iteration

1. Extend Jupyter support
    - [ ] Add support for worklogs to `QueryFrame`
    - [ ] Implement support for visualizations in code, not just as example in notebook
    - [ ] Add 'closed' date to issuedata dataframe (convert changelog info to field)
    - [ ] Cycle time
    - [ ] Time estimated / Time spent
    - [ ] info() method for `QueryFrame`
    - [ ] Implement slicing of `QueryFrame`

### Third iteration

1. Initial Jupyter support
    - [x] `JQL` query oriented, rather than structure oriented
    - [x] Query results in new `QueryFrame` format, which encapsulates several pandas `DataFrames`
    - [x] Example notebook explaining how to use the Sweep notebook functionality
    - [x] Include example of cumulative flow chart

### Second iteration

1. General application
    - [x] Use pandas for data transfer between collection and visualization for one chart
    - [x] Based on experience with first chart: use pandas for all current charts where this makes sense
    - [ ] Create a new chart straight from pandas

2. Features of reports
    - [ ] Create backlog report with ranked overview of all issues
    - [ ] Add dependencies and their status (Open/Closed) to the backlog report
    - [ ] Add tree diagram for Initiatives
    - [x] Add cycle time chart

### First iteration

1. General application
   - [x] Rewrite generation of individual charts as plugins
   - [x] Make configurable what charts are displayed in a report
   - [x] Make template location configurable (so all can create their own "branded" templates)
   - [x] Create a separate configuration for development (minimize everything that is not under current development)

2. Features of reports
   - [x] Add time spent reporting in overview
   - [x] Add estimations reporting in overview
   - [x] Create timeline chart display estimations and time spent (total estimations, growth up of time spent)



