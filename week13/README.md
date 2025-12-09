# Developer Portal for Books API

This project is a simple developer portal for a REST API that manages a collection of books. The portal provides an interface for users to interact with the API, view documentation, and manage books.

## Project Structure

```
week13
├── api
│   ├── __init__.py
│   ├── server.py
│   └── books-api.yaml
├── portal
│   ├── __init__.py
│   ├── app.py
│   ├── static
│   │   └── css
│   │       └── style.css
│   └── templates
│       ├── base.html
│       ├── docs.html
│       └── index.html
├── requirements.txt
└── README.md
```

## API Overview

The API provides endpoints for:

- User authentication (register and login)
- Managing books (CRUD operations)
- Serving API documentation via Swagger UI

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd week13
   ```

2. **Install dependencies**:
   Make sure you have Python and pip installed. Then run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the API server**:
   Navigate to the `api` directory and run:
   ```
   python server.py
   ```

4. **Run the developer portal**:
   Navigate to the `portal` directory and run:
   ```
   python app.py
   ```

5. **Access the portal**:
   Open your web browser and go to `http://localhost:5000` to access the developer portal.

## Usage

- Use the portal to register and log in as a user.
- Explore the API documentation to understand the available endpoints and their usage.
- Manage the book collection through the provided interfaces.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.