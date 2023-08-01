# RNaught Server Side

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

## Introduction

RNaught is a contact tracing and infection prediction application developed under the guidance of "Mar Athanasius College of Engineering". This repository contains the server-side code for the Flask API, which efficiently processes data and serves requests from the RNaught mobile application.

## Credits

This project is built and maintained under the auspices of "Mar Athanasius College of Engineering".

## Contributors

- [Nowfir](https://github.com/Nowfir)

## Installation

1. Clone the repository:

    git clone https://github.com/your-username/rnaught-server.git
	cd rnaught-server

2.  Install the required dependencies:

bashCopy code

`pip install -r requirements.txt`

## Getting Started

1.  Set up the environment variables:

Create a `.env` file in the root directory and define the following variables:

plaintextCopy code

`FLASK_APP=app.py FLASK_ENV=development`

2.  Run the Flask development server:

bashCopy code

`flask run`

By default, the server will run on `http://127.0.0.1:5000/`.

## API Endpoints

|Endpoint  | Method | Description  |
|--|--|--|
| `/api/contact` | POST | Store direct contact details |
| `/api/contacts` | GET | Retrieve direct contacts for a user |
| `/api/prediction` | POST | Get infection prediction for a user |

## Database

RNaught uses a Neo4j graph database to efficiently store contact details. Make sure you have a Neo4j instance set up and update the connection settings in `app.py` if necessary.

## Tech Stack

-   Python 3.8+: Programming language for the server-side code.
-   Flask: Micro web framework to build the API.
-   Neo4j: Graph database to store contact details.

## Contributing

We welcome contributions to RNaught! If you find any issues or want to suggest improvements, please create a new issue or submit a pull request.

Before submitting a pull request, make sure to:

-   Test your changes thoroughly.
-   Follow the coding style and best practices.
-   Update the README and documentation as needed.

## License

This project is licensed under the MIT License - see the [LICENSE](https://chat.openai.com/LICENSE) file for details.
