# Hydroponic System Controller

## Overview
This project is designed to support and automate a hydroponic system, managing growth cycles and various hardware components. The system is built using Python, Ruby, and C# and is intended to run on a Raspberry Pi with an Arduino for analog hardware control. The software also includes functionality for development on Mac or PC.

## Components
### Raspberry Pi (Controller)
- Language: Python
- Files: nakama_controller.py
- Description: Acts as the brain of the system, controlling the hydroponic hardware and running the state machine and user interface. It handles digital sensors directly connected to the Raspberry Pi.

### Arduino (Hardware Control)
- Language: C#
- Description: Manages analog hardware components such as pumps, lights, and other actuators. It communicates with the Raspberry Pi via the Ruby server.
### Ruby Server (Middleware & Remote Database)
- Language: Ruby
- Files: nakama_server.rb
- Description: Serves as a remote database and middleware, facilitating communication between the Raspberry Pi and the Arduino. It exposes API endpoints for data exchange.

## Installation
### Prerequisites
- Raspberry Pi
- Arduino
- Mac or PC for development
- Python 3
- Ruby
- Required libraries for Python (detailed in nakama_dependency_list.py)

### Steps
1. Clone the repo
   ```sh
   git clone https://github.com/MarcAntoineJean01/hydro-system.git
   cd hydro-system
   ```
2. Install Python dependencies
   ```sh
   WIP
   ```
4. Install Ruby dependencies
   ```sh
   WIP

## Usage
### Running the Server
To run the Ruby server, use:
   ```sh
   ruby nakama_server.rb
   ```
### Running the Controller and UI
To run the Python controller and UI, use:
   ```sh
   python3 nakama_controller.py
   ```
## Development
The software can also be run on a Mac or PC for development purposes. Follow the same installation steps and use the commands above to run the server and controller/UI.

## Work in Progress
This project is a work in progress.