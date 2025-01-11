# Trail Management API

This repository contains the source code for the Trail Management API, a microservice designed to securely manage trail-related data, including CRUD operations for trails, role-based access control, and user authentication. The system integrates an external authenticator API for secure login and utilizes a relational database for managing trails and user roles.

## Features

- **Secure Authentication:** Integrates an external authenticator API to validate user credentials.
- **Role-Based Access Control:** Restricts sensitive operations to Admin users while allowing general users to view trails.
- **CRUD Operations:** Create, Read, Update, and Delete functionality for managing trail data.
- **Relational Database:** SQLAlchemy ORM for efficient database interaction.
- **Interactive Documentation:** Swagger UI for exploring and testing API endpoints.



## API Endpoints

| Endpoint            | Method | Description                   |
|---------------------|--------|-------------------------------|
| `/login`            | POST   | Authenticates a user.         |
| `/logout`           | POST   | Logs out the current user.    |
| `/trails`           | GET    | Retrieves all trails.         |
| `/trails`           | POST   | Creates a new trail (Admin).  |
| `/trails/<trail_id>`| GET    | Retrieves a specific trail.   |
| `/trails/<trail_id>`| PUT    | Updates a trail (Admin).      |
| `/trails/<trail_id>`| DELETE | Deletes a trail (Admin).      |

## Known Issues

Docker deployment is currently unavailable due to a macOS issue falsely flagging Docker Desktop as malware. Refer to this report for details.
=
