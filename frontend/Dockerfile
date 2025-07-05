# Stage 1: Build the Vue.js application
FROM node:20-alpine as build-stage

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Vue.js application for production
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine as production-stage

# Copy the built Vue.js app from the build-stage to the Nginx html directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80 (standard HTTP port for web servers)
EXPOSE 80

# Command to run Nginx
CMD ["nginx", "-g", "daemon off;"]