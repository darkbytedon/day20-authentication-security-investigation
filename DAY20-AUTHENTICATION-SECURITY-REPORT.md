# Day 20: API Authentication and Session Management Security Investigation

## 1. Objective

Investigate common API authentication and session-management weaknesses using a locally developed Flask application.

The investigation focused on username enumeration, insecure password storage, brute-force attacks, authentication sessions, and logout behavior.

## 2. Scope and Environment

- Application: Python Flask REST API
- Testing environment: Ubuntu WSL
- Target: Localhost (`127.0.0.1`)
- Authentication method: Username and password
- Testing tools: cURL and pytest
- Rate limiting: Flask-Limiter

All testing was performed against a locally controlled application.

## 3. Initial Security Weaknesses

The initial application demonstrated several authentication weaknesses:

1. Username enumeration: Different login responses could reveal whether an account existed.
2. Plaintext password storage: Passwords were stored without secure password hashing.
3. Brute-force exposure: Login attempts were not initially restricted.
4. Session management weaknesses: Authentication state needed to be properly established, protected, and cleared.
5. Secret management: The Flask secret key was initially hardcoded in the application.

## 4. Security Remediation

### 4.1 Preventing Username Enumeration

Changed login failures to return the same response:

`Invalid username or password`

Both unknown usernames and incorrect passwords return HTTP 401.

### 4.2 Secure Password Storage

Implemented Werkzeug password hashing:

- `generate_password_hash()` stores password hashes rather than plaintext passwords.
- `check_password_hash()` verifies submitted passwords against stored hashes.

Password hashes are not decrypted to recover the original passwords.

### 4.3 Brute-Force Protection

Implemented Flask-Limiter:

`@limiter.limit("5 per minute")`

Testing confirmed that the first five failed login attempts returned HTTP 401, while the sixth returned HTTP 429.

### 4.4 Session Management

Implemented Flask session handling:

- Successful authentication creates a session.
- The profile endpoint requires an authenticated session.
- Logout clears the session.
- Permanent session lifetime is configured for 30 minutes.
- Session cookies use HttpOnly and SameSite=Lax.

### 4.5 Secret Key Management

Replaced the hardcoded Flask secret key with an environment variable:

`os.environ["FLASK_SECRET_KEY"]`

This keeps the secret outside the application source code.

## 5. Security Testing Results

Automated tests were executed using pytest.

| Test | Expected result |
|---|---|
| Successful login | HTTP 200 |
| Incorrect password | HTTP 401 |
| Unknown username | HTTP 401 |
| Unauthenticated profile | HTTP 401 |
| Authenticated profile | HTTP 200 |
| Logout | HTTP 200, subsequent profile request HTTP 401 |
| Login rate limit | Five HTTP 401 responses, then HTTP 429 |

**Final result: 7/7 automated tests passed.**

Manual cURL testing also verified login, profile access, and logout behavior.

## 6. Limitations and Production Recommendations

This was a local learning environment, not a production deployment.

- Flask-Limiter currently uses in-memory storage. Production should use a shared backend such as Redis.
- IP-based rate limiting alone is insufficient against distributed attacks.
- The local application uses HTTP, so the Secure cookie flag is disabled. Production must use HTTPS and enable Secure cookies.
- Flask's default session cookies are signed, not encrypted. Sensitive information should not be stored inside them.
- Clearing a default Flask session cookie does not immediately revoke a previously copied valid cookie. Production systems should consider server-side sessions and session revocation.
- The simulated user database is stored in application memory rather than a persistent database.
- The Flask development server and debugger must not be exposed as a production service.

## 7. Conclusion

The investigation demonstrated how weak authentication and session-management practices can expose APIs to account enumeration, password compromise, brute-force attempts, and session-related risks.

The application was improved through generic authentication errors, password hashing, login rate limiting, session controls, logout functionality, and environment-based secret management.

All seven automated security tests passed, providing evidence that the implemented protections behaved as expected in the local lab.
