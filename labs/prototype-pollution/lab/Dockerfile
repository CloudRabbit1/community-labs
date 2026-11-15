FROM node:20-slim

WORKDIR /app

COPY app.js /app/app.js

# Generate flag at container start and launch the app
CMD ["sh", "-c", "node -e \"process.stdout.write('POC{' + require('crypto').randomBytes(16).toString('hex') + '}\\n')\" > /flag.txt && node /app/app.js"]
