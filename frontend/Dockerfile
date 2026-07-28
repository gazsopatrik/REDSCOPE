FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci || npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5173

# Nginx config for client-side routing
RUN echo 'server { listen 5173; location / { root /usr/share/nginx/html; index index.html index.htm; try_files $uri $uri/ /index.html; } location /api/ { proxy_pass http://backend:8000; } }' > /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
