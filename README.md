# ANT+ to BLE Data Forwarding Application

This application serves as a bridge between ANT+ devices and Bluetooth Low Energy (BLE) devices. It allows for real-time forwarding of data collected from ANT+ sensors to BLE devices, enabling the integration of ANT+ sensor data into BLE-centric environments or applications.

## Features

- **Dynamic Device Scanning**: Automatically scans for ANT+ devices and establishes connections.
- **Data Forwarding**: Forwards data received from ANT+ devices to configured BLE devices in real-time.
- **Flexible Device Configuration**: Supports various ANT+ device types and BLE forwarding strategies.
- **Threaded Operation**: Ensures responsive data handling through multi-threaded architecture.

## Getting Started

### Prerequisites

- Python 3.7 or later
- Compatible ANT+ USB dongle
- Linux environment with Bluetooth Low Energy support

### Installation

1. Clone the repository:
    ```
    git clone https://github.com/magpern/AntBLEProxy.git
    cd AntBLEProxy
    ```

2. Install dependencies:
    TODO: create a requirements.txt
    ```
    pip install -r requirements.txt
    ```

### Usage

1. Start the application:
    ```
    python antserver.py
    ```

2. Use a web browser or a SocketIO client to connect to the server, start scanning for ANT+ devices, and initiate data forwarding to BLE devices.

## Configuration

TODO: Explain any configuration files, environment variables, or command-line arguments required for customizing the application.

## Contributing

We welcome contributions from the community! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Implement your changes.
4. Write or adapt tests as necessary.
5. Ensure your code adheres to the project's style and contribution guidelines.
6. Submit a pull request against the main branch.

## License

If you find it useful. Use it.

## Acknowledgments

- Mention any libraries, technologies, or individuals that played a significant role in the development of this application.
