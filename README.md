# LMS GUI Project

## Requirements
- Java 11+
- SQLite JDBC


## Setup

1. Download sqlite-jdbc.jar
2. Place in project folder
   
```bash
curl -L -o sqlite-jdbc.jar https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.36.0.3/sqlite-jdbc-3.36.0.3.jar
```
### The LMS.db is not the actual db
Just a dummy db to check and verify codes for creating GUI
Once everything looks good, need to update changes to database created in part 2 phase 2

## Run

```bash
javac -cp ".:sqlite-jdbc.jar" LMS_Full.java
java -cp ".:sqlite-jdbc.jar" LMS_Full


---
```


Whenever you change code:

```bash
git add .
git commit -m "Updated feature"
git push
