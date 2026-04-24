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
## Run

```bash
javac -cp ".:sqlite-jdbc.jar" LMS_Full.java
java -cp ".:sqlite-jdbc.jar" LMS_Full

