# Interview Notes — Vehicle Tracking Assessment

These notes describe the current code and checks in this workspace. The database is **MySQL** as selected and configured in the earlier phases; some pasted assessment text said PostgreSQL, but this implementation was not migrated. FastAPI, MySQL, Mosquitto, and the simulator were exercised together; Flutter could not be built because its SDK is absent from this computer.

## 1. 30-second project explanation

I built a simple vehicle tracking system with a FastAPI backend and a Flutter client. A Python simulator publishes sample bus coordinates over MQTT, and the backend stores each valid point in MySQL so it can return both the latest location and location history. Users log in with JWT, and the backend uses the logged-in user's database assignment to restrict which bus and route they can see.

## 2. One-minute project explanation

The project demonstrates how a small transport tracking app can collect and display bus locations. I used FastAPI for REST endpoints, SQLAlchemy to connect to MySQL, Argon2 password hashes and JWTs for login, and Mosquitto MQTT for GPS messages from a Python simulator. Each demo user is assigned one route and one vehicle. The FastAPI tracking queries always filter using the vehicle loaded from the authenticated user, so a client cannot grant itself access by changing a bus ID. The Flutter app logs in, stores the token for the demo, periodically requests the dashboard data, and shows the latest saved coordinates on an OpenStreetMap-based map. The route polyline itself is sample geometry, while the moving bus marker uses the backend's current GPS record.

## 3. Complete architecture

```text
Python GPS simulator -> Mosquitto broker -> FastAPI MQTT listener -> MySQL gps_data history
Flutter -> FastAPI REST API -> MySQL users/routes/vehicles/gps_data
Flutter map -> OpenStreetMap tile service (internet required)
```

- **GPS simulator:** creates changing example coordinates for BUS-001 and BUS-002; no physical GPS hardware is used.
- **MQTT broker:** Mosquitto receives and forwards messages on topics such as `vehicles/BUS-001/gps`.
- **FastAPI listener:** subscribes to `vehicles/+/gps`, checks the topic and payload, looks up the vehicle, and inserts a GPS row.
- **MySQL:** holds users, route and vehicle assignments, plus all historical GPS rows.
- **FastAPI REST API:** validates JWTs, returns the current user's assignment, and queries only their vehicle's GPS records.
- **Flutter:** logs in and requests protected endpoints using a bearer token; it polls the dashboard every five seconds.
- **Map:** draws sample route geometry and places the vehicle marker from the actual latest point returned by the API.

## 4. WHAT I ACTUALLY IMPLEMENTED

### Backend

- FastAPI application with health checks and REST routers.
- SQLAlchemy models using the existing MySQL database configuration.
- Login endpoint, Argon2 password verification, JWT generation, and protected-user dependency.
- Demo route/vehicle/user seeding.
- APIs for current user, assigned route, assigned vehicle, latest GPS point, and GPS history.
- Backend checks that tracking requests can only refer to the authenticated user's assigned vehicle.

### Database

- MySQL tables for users, routes, vehicles, and GPS data.
- Foreign key relationships between assignments, vehicles/routes, and GPS data.
- GPS history is inserted as new rows; current location is the newest timestamp/ID row.

### MQTT

- Paho MQTT subscriber for `vehicles/+/gps`.
- Payload and topic consistency validation and vehicle lookup before saving a location.
- MQTT connection starts asynchronously so the API can start while a broker is offline.
- Live Mosquitto ingestion was exercised with the simulator and GPS rows were returned by the tracking API.

### GPS simulator

- Python simulator publishes changing sample coordinates for both seeded vehicles every two seconds.
- Simulator source is present and its messages were stored by FastAPI through Mosquitto.

### Flutter

- Dart source for login, dashboard, map, and history screens.
- REST client, bearer token header, JSON model parsing, timeout/connection error messaging, and five-second dashboard refresh.
- Map uses the API GPS point for the bus marker and a static illustrative route line.
- Flutter source/build was not run because Flutter SDK was not installed locally.

### Authentication

- Passwords are hashed with Argon2, not stored as plain text.
- Login returns a signed JWT; protected endpoints read the user ID from the token.
- Flutter stores the token in shared preferences for this demo. This is convenient but not encrypted secure storage.

### Authorization

- The request's user is identified from its JWT.
- Tracking queries use `current_user.vehicle.id` from the database, never a vehicle ID supplied by the client.
- An optional `vehicle_id` query parameter is compared to the user's assigned vehicle and produces `403` on mismatch.

### Map

- Flutter map tiles from OpenStreetMap, with attribution.
- A bus marker displays the backend's latest GPS location when one exists.
- A sample route polyline is selected based on the route name; it is not dynamically loaded from the database.

## 5. Important interview questions

For each question, the first response is a natural spoken answer. The technical note explains what the code does and includes its limits.

### 1. Tell me about your project.
**Say:** I built a vehicle tracking demo where a Python simulator sends bus coordinates through MQTT. FastAPI saves them to MySQL and provides protected tracking APIs, and a Flutter app shows the assigned bus and its latest location.

**Technical:** The code has a simulator, MQTT subscriber, SQLAlchemy models, JWT-protected REST APIs, and Flutter client. The route line is illustrative, while the marker comes from saved GPS data.

### 2. Why did you choose FastAPI?
**Say:** FastAPI let me build a small Python API with request validation and generated interactive API documentation. It also fit the Python simulator and SQLAlchemy code I was already using.

**Technical:** FastAPI uses type hints and Pydantic schemas to validate input/output and exposes Swagger UI at `/docs`. This project uses synchronous SQLAlchemy sessions for straightforward beginner-friendly database operations.

### 3. Why MySQL?
**Say:** I used MySQL because that was the database I had already set up and verified for this project. It stores related users, routes, vehicles, and GPS records with foreign keys.

**Technical:** The connection uses SQLAlchemy with the PyMySQL driver. The updated assessment text mentioned PostgreSQL in a few places, but I preserved the working MySQL setup rather than claiming a database migration.

### 4. Why Flutter?
**Say:** Flutter lets me make the app interface in Dart and use the same code for Android and web-style testing. I used it for the login, tracking dashboard, history, and map screens.

**Technical:** Flutter source is included, but no local build is claimed because this machine did not have the Flutter SDK installed.

### 5. What is MQTT?
**Say:** MQTT is a lightweight messaging protocol where publishers send messages to topics and subscribers receive messages from those topics through a broker. Here it carries GPS updates from the simulator to FastAPI.

**Technical:** Paho subscribes to `vehicles/+/gps`; the plus is a single-level wildcard so it can receive either bus topic. It uses QoS 1 subscription.

### 6. Why MQTT instead of directly calling the REST API?
**Say:** MQTT is a simple fit for frequent small telemetry messages from vehicles. The app still uses REST for user login and for requesting current and historical data.

**Technical:** This separates the simulator's publish operation from the app's request/response API. This demo doesn't add a queueing platform or configure durable replay, so it stays intentionally small.

### 7. What is an MQTT broker?
**Say:** The broker is the middle program that receives messages from publishers and forwards them to subscribers listening to the matching topic. Mosquitto is the broker used by the run instructions.

**Technical:** The listener connects to the configured host and port, subscribes after successful connection, and runs in Paho's network loop.

### 8. What is a topic?
**Say:** A topic is the named channel an MQTT message is published to. This app uses a different topic for each vehicle, like `vehicles/BUS-001/gps`.

**Technical:** The wildcard subscription is `vehicles/+/gps`; the listener checks that the topic's vehicle code matches the payload's `vehicle_id`.

### 9. Who publishes GPS data?
**Say:** In this assessment, a Python GPS simulator acts as BUS-001 and BUS-002. I do not have a physical GPS device connected.

**Technical:** `gps_simulator.py` periodically creates changing sample coordinates and publishes JSON to the local broker.

### 10. Who subscribes to GPS data?
**Say:** The MQTT listener inside the FastAPI process subscribes to the vehicle GPS topics. It processes each message and writes a valid location to MySQL.

**Technical:** The Paho on-message callback validates through the `GPSUpdate` Pydantic model and opens a separate SQLAlchemy session for its database work.

### 11. How does GPS data reach the database?
**Say:** The simulator publishes JSON to Mosquitto, FastAPI receives it, validates the coordinates and vehicle, then inserts a new GPS record. Each point remains in history.

**Technical:** The subscriber maps the external vehicle code to the internal `vehicles.id`, then adds a `GPSData` row and commits. Unknown vehicles and invalid messages are logged and ignored.

### 12. How does Flutter get the GPS location?
**Say:** Flutter calls the protected current-location endpoint with its JWT. FastAPI finds the user's assigned bus and returns that bus's latest saved point.

**Technical:** Dashboard refreshes every five seconds and uses the JSON `latitude`, `longitude`, `speed`, and `recorded_at`; the API query filters by the assigned internal vehicle ID.

### 13. What is a REST API?
**Say:** A REST API exposes resources through HTTP methods and URLs. The Flutter app uses HTTP requests to log in and retrieve its route, vehicle, and tracking data.

**Technical:** Login is `POST /auth/login`; the read endpoints use GET. The protected GET requests include a bearer authorization header.

### 14. What is JWT?
**Say:** A JWT is a signed token the server gives the client after login. The client sends it with later requests so the backend can identify the user.

**Technical:** This app signs tokens with HS256 and an expiry. A JWT is signed, not encrypted, so secret data should not be put in its claims.

### 15. How does authentication work?
**Say:** The backend finds the account by email, verifies the submitted password against its stored Argon2 hash, and returns a JWT if valid. Protected endpoints decode the token to identify the user.

**Technical:** Missing, invalid, or expired tokens are rejected with `401`. Demo accounts use a known seed password and are only for local assessment use.

### 16. What is authorization?
**Say:** Authentication identifies who is signed in; authorization decides what that signed-in user is allowed to see. The API only returns the route and bus assigned to that user.

**Technical:** The assignment is loaded through the authenticated SQLAlchemy `User`, and GPS database queries filter on that user's `vehicle.id`.

### 17. How did you implement authorization?
**Say:** I get the current user from the JWT dependency and use the route and vehicle linked to that database user. The client cannot choose another bus to change the records returned.

**Technical:** The tracking router calls `check_requested_vehicle`, then queries GPS by the authenticated user's vehicle primary key. Optional mismatch query parameters get `403`.

### 18. How do you prevent User A from seeing User B's bus?
**Say:** The tracking query is scoped to the vehicle assigned to User A in the database. If User A asks for BUS-002, the backend rejects the mismatch instead of trusting that input.

**Technical:** Demo seeds User A -> Route A -> BUS-001 and User B -> Route B -> BUS-002. All tracking routes use `current_user.vehicle.id`.

### 19. What happens if someone changes the vehicle ID in the URL/request?
**Say:** The backend compares it with the authenticated user's assigned bus and returns `403` if it differs. The authorization decision is server-side.

**Technical:** The API does not use the request parameter to select the database vehicle; it only uses it for an explicit mismatch check.

### 20. How do you store GPS history?
**Say:** Every valid incoming GPS message creates a new row linked to a vehicle. I keep previous points, so the history endpoint can return them later.

**Technical:** `gps_data.vehicle_id` is a foreign key and the table has an index on vehicle and recorded timestamp to help tracking queries.

### 21. How do you get the latest GPS location?
**Say:** The API sorts the assigned vehicle's points by timestamp from newest to oldest and returns the first one. If no point has arrived, it returns a not-found response.

**Technical:** It orders by `recorded_at` and then `id` to break timestamp ties; the route query is still scoped to the assigned vehicle.

### 22. Why use a GPS simulator?
**Say:** I didn't have GPS hardware, so I used a Python simulator to generate changing coordinates and test the data flow. I describe it as simulated data, not real vehicle data.

**Technical:** The simulator emits timestamps and coordinates for both buses at a two-second interval.

### 23. What happens if the MQTT broker goes down?
**Say:** FastAPI is configured to start without waiting for the broker, and the MQTT client attempts to connect asynchronously. GPS updates cannot be received while the broker is unavailable.

**Technical:** The code logs connection failure and uses Paho's loop. Durable broker storage or replay of messages missed while the API is down is not configured.

### 24. What happens if the FastAPI server goes down?
**Say:** Flutter requests fail and show a connection/backend error, while new tracking API requests cannot be served. When the server returns, the app can poll again; this setup does not guarantee missed MQTT messages are replayed.

**Technical:** API calls have an eight-second timeout; MQTT durability/replay is not configured. Existing MySQL history remains stored independently.

### 25. What happens if MySQL goes down?
**Say:** Database-dependent API operations cannot complete until MySQL is available again. The database health check reports a service-unavailable response when it cannot connect.

**Technical:** The MQTT callback catches SQLAlchemy errors and logs them; it does not persist that failed message for retry, which is a future reliability improvement.

### 26. How does Flutter handle API errors?
**Say:** The API service handles timeouts, backend connection failures, invalid login, unauthorized requests, and server errors with readable messages. The screens show loading indicators and empty or missing-location states.

**Technical:** HTTP status codes are converted to `ApiException`; the dashboard also treats `404` current GPS as no location yet. Flutter behavior is source-implemented but not locally run here.

### 27. What was the most challenging part?
**Say:** The important design challenge was making sure users could not access another bus by changing a request parameter. I solved that by using the authenticated user's assignment in every tracking query.

**Technical:** The authorization check is in FastAPI and the database filter uses the assigned vehicle primary key rather than a client-controlled vehicle identifier.

### 28. What would you improve in the future?
**Say:** I would test on a real Flutter installation, add automated integration tests, and use encrypted token storage. I would also use real device GPS and a production map tile provider if the app were deployed.

**Technical:** Other future work could add retries/monitoring for MQTT ingestion, route geometry from stored route data, HTTPS, account administration, and deployment configuration.

### 29. What security measures did you implement?
**Say:** Passwords are hashed, protected APIs require a signed expiring JWT, and tracking authorization is checked on the backend. I also keep local secrets in an ignored `.env` file.

**Technical:** The demo uses HS256 and shared-preferences token storage; production would need HTTPS, secure platform token storage, managed secrets, stronger operational controls, and likely rate limiting.

### 30. Explain the complete system from beginning to end.
**Say:** A simulator publishes a bus position to an MQTT topic, Mosquitto forwards it to FastAPI, and the listener validates and saves it in MySQL. A user logs in from Flutter, gets a JWT, and requests assigned tracking data; FastAPI checks the user and returns only that user's bus location for the dashboard and map.

**Technical:** GPS writes append history; API reads are scoped to `current_user.vehicle.id`. Flutter polling refreshes the display every five seconds. The route line is fixed demo geometry and the bus marker uses backend GPS data.

## 6. Demo script (3–5 minutes)

1. Start MySQL in Windows Services and confirm `http://127.0.0.1:8000/db-health` after the API is running.
2. Start Mosquitto service, or open a terminal and run `mosquitto -v`.
3. Backend terminal: `cd` to `vehicle-tracking-backend`, activate `.venv`, run `python -m uvicorn app.main:app --reload`.
4. Simulator terminal: activate the backend `.venv`, then run `python gps_simulator.py`. Point out that the values are simulated.
5. Show FastAPI `/docs`, log in as User A, and call `/me/route`, `/me/vehicle`, current, and history with the bearer token.
6. Show history accumulating records and current location changing while the simulator runs.
7. Run Flutter on the configured emulator/browser, log in as User A, and show Route A, BUS-001, speed/coordinates, history, and map marker.
8. Log out and sign in as User B to show Route B and BUS-002.
9. In `/docs`, authorize as User A and call `/me/tracking/current?vehicle_id=BUS-002`; show the expected `403`.

If Flutter is not installed at demo time, explain that the client source is prepared but not locally build-verified; do not claim a live app demonstration.

## 7. Honest project limitations

- No physical GPS device; coordinates are generated by the simulator.
- MySQL is used, not PostgreSQL.
- Flutter SDK was not installed on the development machine, so Flutter build/run is not locally verified. Mosquitto, the simulator, FastAPI, and MySQL did run together.
- Docker and Docker Compose configuration are not included.
- Flutter polls every five seconds; there are no WebSockets/push updates.
- Route polylines are static example coordinates selected by route name; the moving marker uses actual backend GPS response data.
- OpenStreetMap public tile server requires internet and is not a guaranteed production map service.
- Demo token persistence uses shared preferences, not encrypted secure storage.
- MQTT/database ingestion errors are logged but are not queued for later retry.
- No automated test suite was added; manual/API checks are described in the READMEs.
- The backend and Flutter repositories were pushed publicly to `nishacodes-ind` on GitHub; their URLs are listed in the submission checklist.

## 8. FUTURE improvements (not implemented)

- Connect real vehicle GPS hardware.
- Use WebSockets for live dashboard updates.
- Load route geometry from database-managed route data.
- Add admin tools to manage accounts, routes, and assignments.
- Add durable retry/monitoring for MQTT ingestion.
- Use HTTPS and encrypted token storage.
- Add automated unit/integration tests and deployment monitoring.
- Configure Docker Compose after the local setup is verified.
