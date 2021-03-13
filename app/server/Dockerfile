FROM node:15
# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)

WORKDIR /usr/app
COPY package*.json  /usr/app
RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
COPY . /usr/app
CMD [ "node", "webServer.js" ]