Debug local run : 
 - python -m flask --app app run --debug 

After importing any module run this command after: 
 - pip freeze > requirements.txt  

This will save in the requirements.txt all the modules that are installed in this env.
When creating this prohect from scratch you can simple run :
 - pip install -r requirements.txt

To get all the necessary modules installed


Regarding database migration, follow this steps:
- flask db init
- flask db migrate -m "create core tables"
- flask db upgrade


Usefull git command to clean branches besides master
git branch | ForEach-Object { $_.Replace('*','').Trim() } | Where-Object { $_ -and $_ -ne 'master' } | ForEach-Object { git branch -D $_ }


Usefull command to get the test coverage of the system (keep it above 95%)
pytest --cov=app --cov-report=term-missing --cov-report=html

Project is only considered finished if this command passes
pytest --cov=app --cov-fail-under=95