Debug local run : 
 - python -m flask --app app run --debug 

After importing any module run this command after: 
 - pip freeze > requirements.txt  

This will save in the requirements.txt all the modules that are installed in this env.
When creating this prohect from scratch you can simple run :
 - pip install -r requirements.txt

To get all the necessary modules installed