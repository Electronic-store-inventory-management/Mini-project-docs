

\# US-24 Performance and Load Testing



\## 1. Overview



This directory contains the Locust load-testing script, database seeding script, performance reports and test results.



The performance test uses:

\- 10 concurrent users

\- 10,000 component records

\- 2-minute load test

\- Locust for load generation

\- Waitress as the Django application server

\- MySQL isolated database: `electronics\_inventory\_perf`



\*\*Important:\*\* Never run performance data seeding against the normal `electronics\_inventory` database.



\## 2. Install dependencies



Activate the project environment or use the commands below:



```cmd

.venv\\Scripts\\python.exe -m pip install -r requirements.txt

.venv\\Scripts\\python.exe -m pip install locust waitress

```



Ensure MySQL is running and the project's `.env` contains valid database connection credentials.



\## 3. Create the isolated performance database



Using a MySQL administrative account, execute:



```sql

CREATE DATABASE electronics\_inventory\_perf

CHARACTER SET utf8mb4

COLLATE utf8mb4\_unicode\_ci;



GRANT ALL PRIVILEGES ON electronics\_inventory\_perf.\*

TO 'inventory\_user'@'localhost';



FLUSH PRIVILEGES;

```



The MySQL account must match the database user configured in `.env`. Adjust the grant username and host if necessary.



This creates a separate database and does not require deleting or modifying the normal inventory database.



\## 4. Select and verify performance settings



Open a new Windows CMD terminal in the project root:



```cmd

set DJANGO\_SETTINGS\_MODULE=config.performance\_settings

```



The performance settings module overrides the database name to `electronics\_inventory\_perf`.



Verify both the configured database and actual MySQL connection:



```cmd

.venv\\Scripts\\python.exe manage.py shell -c "from django.conf import settings; from django.db import connection; print('Configured database:', settings.DATABASES\['default']\['NAME']); c=connection.cursor(); c.execute('SELECT DATABASE()'); print('Connected database:', c.fetchone()\[0]); c.close()"

```



Both values must be:



```text

electronics\_inventory\_perf

```



Stop if either value is different.



\## 5. Apply migrations



In the same terminal, with performance settings selected:



```cmd

.venv\\Scripts\\python.exe manage.py migrate

```



This creates the application tables in the isolated performance database.



\## 6. Configure and seed test data



Set the dedicated test account credentials:



```cmd

set PERF\_TEST\_USERNAME=perf\_staff

set PERF\_TEST\_PASSWORD=YOUR\_LOCAL\_TEST\_PASSWORD

```



Replace `YOUR\_LOCAL\_TEST\_PASSWORD` with a password of your choice. Use the same password in the application-server and Locust terminals.



Run the seed script:



```cmd

.venv\\Scripts\\python.exe performance\_tests\\seed\_data.py

```



The script forces `config.performance\_settings` regardless of an inherited settings-module environment variable.



Before modifying records, it verifies:

1\. The configured Django database name.

2\. The actual MySQL database selected by the connection.

3\. That no unexpected non-performance component records exist.



It then creates 10,000 records with the `PERFLOAD` prefix and creates or updates the dedicated `perf\_staff` test account.



The script refuses to proceed if the database is not `electronics\_inventory\_perf`.



\## 7. Start the Django application



Open a second CMD terminal in the project root.



Set the same performance settings and test credentials:



```cmd

set DJANGO\_SETTINGS\_MODULE=config.performance\_settings

set PERF\_TEST\_USERNAME=perf\_staff

set PERF\_TEST\_PASSWORD=YOUR\_LOCAL\_TEST\_PASSWORD

```



Start the application using Waitress:



```cmd

.venv\\Scripts\\waitress-serve.exe --listen=127.0.0.1:8000 --threads=12 config.wsgi:application

```



Keep this terminal running during the load test.



\## 8. Run the Locust load test



Open a third CMD terminal in the project root.



Configure the same test credentials:



```cmd

set PERF\_TEST\_USERNAME=perf\_staff

set PERF\_TEST\_PASSWORD=YOUR\_LOCAL\_TEST\_PASSWORD

```



Run:



```cmd

.venv\\Scripts\\locust.exe -f performance\_tests\\locustfile.py --host http://127.0.0.1:8000 --users 10 --spawn-rate 2 --run-time 2m --headless --csv performance\_tests/results/us24\_reproduced --html performance\_tests/results/us24\_reproduced.html

```



Locust authenticates using the dedicated test account and sends requests to the running Django application.



The Locust process does not connect directly to MySQL. The Django application uses `config.performance\_settings` to connect to the isolated database.



\## 9. Performance acceptance criteria



The performance test validates:

\- Up to 10 concurrent users.

\- Inventory containing 10,000 component records.

\- Representative dashboard and inventory operations.

\- p90 response time within 3 seconds.

\- Request failures and response-time bottlenecks.



The recorded final test results are available in the `results` directory.



\## 10. Important safety notes



\- Never seed the normal `electronics\_inventory` database.

\- Do not change the project's `.env` to point the normal application at the performance database.

\- Use `config.performance\_settings` for migrations and the application server.

\- The seeding script forces the performance settings and checks the database before writing.

\- Locust requires the same test username and password used during seeding.

\- Do not commit local passwords or database credentials.

\- Keep the performance database separate from application and production data.
