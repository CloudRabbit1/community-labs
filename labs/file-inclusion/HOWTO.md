# HOWTO: File Inclusion Lab

Built from templates/new-lab. No special setup required.

## Test

```bash
docker compose up --build -d
bash test.sh
```

## Verify manually

```bash
curl "http://localhost:8080/?page=about.txt"
curl "http://localhost:8080/?page=../../flag.txt"
```
