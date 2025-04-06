# Long Polling Server and Client

A demonstration of long polling communication between a simulated camera client and a server.

## Overview

This project consists of two main components:
- **Camera**: Simulates a device that generates logs and uses long polling to communicate with the server
- **Server**: Handles log collection and provides endpoints for clients to retrieve camera data

## Features

- Real-time log transmission from camera to server
- Long polling implementation for efficient communication
- REST API for retrieving collected logs
- Docker containerization for easy deployment

## Prerequisites

- Docker
- Docker Compose

## Installation and Setup

1. Clone the repository
2. Navigate to the project directory
3. Run `docker compose up` to start the simulated camera and server

## Usage

- Call `GET /logs` using Postman on localhost port 5001 to get logs from the camera.