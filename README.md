# Software-Analysis-Industry-backed-vs-Community-driven
Comparison of code review equitablility between Industry-backed projects and Community-backed projects

# Usage
## GatherData.py
create a .env file with a github token stored under the name `GITHUB_TOKEN`, it should have `repo`, `read:org`, and `read:user` permissions.
run it and it will create a csv file for every repo in repositories. the csv will be empty if anything went wrong with the request
