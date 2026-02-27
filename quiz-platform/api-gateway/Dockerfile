FROM nginx:alpine

COPY api-gateway/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]