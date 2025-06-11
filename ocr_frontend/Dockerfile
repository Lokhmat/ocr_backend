# Use an official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json (if available) first to install dependencies
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of your application code
COPY . .

# Expose the port that your Next.js app runs on (default is 3000)
EXPOSE 3000

# Set the command to run your Next.js development server
CMD ["npm", "run", "dev"]
