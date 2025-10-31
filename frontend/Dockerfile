FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --silent
COPY . .
RUN npm run build
# serve with simple static server
RUN npm install -g serve
CMD ["serve","-s","build","-l","3000"]
EXPOSE 3000
