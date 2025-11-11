# Lệnh chạy
```
newman run Week8.postman_collection.json -e New_Environment.postman_environment.json -r cli,htmlextra --reporter-htmlextra-export test_report.html -n 5
```