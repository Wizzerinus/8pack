FROM node:20.2.0-alpine AS compiler
WORKDIR /app

# Install dependencies
COPY package.json ./package.json
COPY package-lock.json ./package-lock.json
RUN npm install

# Copy project
COPY src src
COPY vite.config.js .
COPY tailwind.config.js .
COPY postcss.config.js .
COPY jsconfig.json .
COPY index.html .

# Replace the address in the script with the deployed address
ARG BACKEND_HOST
RUN sed -i "s|http://localhost:8003|${BACKEND_HOST}|g" src/util.js

# Build
RUN npm run build

# frontend isn't a composite app, so we make a compact image
FROM nginx
COPY --from=compiler /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf
