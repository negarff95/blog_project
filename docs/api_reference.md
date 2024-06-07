# Views Documentation

This document provides an overview and details of the views implemented in the project.

## Account

### 1. SignUpView

#### Description

The SignUpView is responsible for handling user registration/signup requests.

#### Methods

- **POST**: Processes the user registration request and creates a new user if the provided data is valid.

#### Authentication Classes

- None (No authentication required for user registration).

#### Permission Classes

- None (No specific permissions required for user registration).

#### Endpoint

- `api/account/signup/`

#### Request Body

- `username`: The username of the user.
- `password`: The password of the user.
- `is_active`: (Automatically set to True during user creation)

#### Response

- **Success**: Returns the serialized user data with a status code of 201 CREATED.
- **Failure**: Returns the error message with a status code of 400 BAD REQUEST if the provided data is invalid.

#### Sample cURL Request

```bash
curl -X POST http://{domain_name}/api/account/signup/ -d "username=user&password=pass123"
 
```
#### Sample Response
```bash
{
    "username": "user",
    "is_active": true
}
```


### 2. TokenObtainPairView

#### Description

The TokenObtainPairView is responsible for generating JWT tokens for user authentication.

#### Methods

- **POST**: Processes the user login request and generates JWT tokens if the provided credentials are valid.

#### Authentication Classes

- None (No authentication required for token generation).

#### Permission Classes

- None (No specific permissions required for token generation).

#### Endpoint

- `api/account/login/`

#### Request Body

- `username`: The username of the user.
- `password`: The password of the user.

#### Response

- **Success**: Returns a JSON response containing the generated JWT tokens with a status code of 200 OK.
- **Failure**: Returns an error message with a status code of 401 UNAUTHORIZED if the provided credentials are invalid.

```bash
curl -X POST http://{domain_name}/api/account/login/ -d "username=user&password=pass123"
 
```
#### Sample Response
```bash
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
}
```


### URLs

- `api/account/login/`: Endpoint for user login (TokenObtainPairView).
- `api/account/signup/`: Endpoint for user registration (SignUpView).

---

## Blog

### 1. PostView
#### Description

The `PostView` is responsible for handling requests related to posts, including retrieving posts and their details.

#### Methods

- **GET**: Retrieves posts from the database, optionally filtered by post ID.

#### Authentication Classes

- JWTAuthentication: Token authentication is optional.(required to see user rate on posts)

#### Permission Classes

- IsAuthenticatedOrReadOnly: Allows authenticated users to read, but only authenticated and authorized users to write.

#### Endpoint

- `/api/blog/posts/`

#### Response

- **Success**: Returns a paginated response containing serialized post data with a status code of 200 OK. If the user is not authenticated or does not provide a token, the `user_rate` field will be omitted from the response.

```bash
# Get all posts
curl -X GET http://{domain_name}/api/blog/posts/ 
```
#### Sample Response
```bash
next": "http://{domain_name}/api/blog/posts/?cursor=cD05OTE%3D",
    "previous": null,
    "results": [
        {
            "pk": 1000,
            "title": "name-999",
            "average_rate": 2.5,
            "rate_counts": 301,
            "user_rate": null
        },
        {
            "pk": 999,
            "title": "name-998",
            "average_rate": 3.6,
            "rate_counts": 601,
            "user_rate": null
        },
        {
            "pk": 998,
            "title": "name-997",
            "average_rate": null,
            "rate_counts": 0,
            "user_rate": null
        }
    ]
}
```

### 2. RateView

#### Description

The RateView handles requests for rating posts.

#### Methods

- **POST**: Processes the submission of a rate for a post.

#### Authentication Classes

- JWTAuthentication: Token-based authentication required.

#### Permission Classes

- IsAuthenticated: Only authenticated users are allowed to submit rates.

#### Throttle Classes

- RateThrottle: Limits the rate of rate submissions per user.

#### Endpoint

- `/api/blog/submit-rate/`

#### Request Body

- `score`: The rating score given by the user.
- `post`: The ID of the post being rated.

#### Response

- **Success**: Returns the serialized rate data with a status code of 200 OK.
- **Failure**: Returns an error message with a status code of 400 BAD REQUEST if the provided data is invalid.
- **Failure**: Returns an error message with a status code of 401 UNAUTHORIZED if the user is not authenticated.

```bash
curl -X POST http://yourdomain.com/api/blog/submit-rate/ -H "Authorization: Bearer <access_token>" -d "score=4&post=1"
 
```
#### Sample Response
```bash
{
    "score": 4,
    "post": 1
}

```

### URLs

- `/api/blog/posts/`: Endpoint for retrieving posts (PostView).
- `/api/blog/submit-rate/`: Endpoint for submitting rates (RateView).



