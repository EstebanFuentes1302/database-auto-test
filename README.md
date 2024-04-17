
# Database Automatic Test Script
Script that can be called by a .bat file for daily testing databases listed in a .csv file





## Database Testing

Path where the logic and database testing is located:

```bash
  py\db_test_csv.py
```

Data is called by a .csv file in the data folder (as listed in source code)
## Execution Batch File

Bash file that can be called by the Windows Task Scheduler or another alternative.

```bash
  scripts\run_db_test.bat
```
    
## Data CSV File

#### Data can be called in a created "data" folder with the csv file:

```bash
  data\databaseinfo.csv
```
Database info in csv file must be in this format:

```bash
  service_name,db_user,db_password,host,port
  service_name,db_user,db_password,host,port
  service_name,db_user,db_password,host,port
  service_name,db_user,db_password,host,port
```