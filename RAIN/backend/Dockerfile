FROM node:18-alpine

RUN apk add --no-cache python3 make g++ python3-dev

WORKDIR /app

COPY package*.json ./

RUN npm install --verbose

COPY . .

ENV NODE_ENV=development

ENV NODE_OPTIONS="--max-old-space-size=512"

EXPOSE 3000

CMD ["node", "--trace-warnings", "./bin/www"]
