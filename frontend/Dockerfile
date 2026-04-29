FROM nginx:alpine

# Убираем дефолтный конфиг nginx
RUN rm /etc/nginx/conf.d/default.conf

# Кладём наш конфиг
COPY nginx.conf /etc/nginx/conf.d/

# Кладём UI
COPY index.html /usr/share/nginx/html/

EXPOSE 80