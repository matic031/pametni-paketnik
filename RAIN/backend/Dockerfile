FROM node:18-alpine

RUN apk add --no-cache python3 make g++ gcc

WORKDIR /app

COPY package*.json ./

RUN npm install bcrypt --build-from-source
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "./bin/www"]