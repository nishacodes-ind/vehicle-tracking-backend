# Vehicle Tracking Backend

A beginner-friendly FastAPI backend for a GPS vehicle tracking assessment. It uses **MySQL** (the database already configured for Phases 1–4), SQLAlchemy, JWT login, and MQTT GPS ingestion. GPS comes from a Python simulator; there is no physical GPS device.

## Features

- Passwords stored as Argon2 hashes and JWT bearer authentication.
- Two demo accounts assigned to different routes and vehicles.
- Backend authorization derives the allowed vehicle from the authenticated user.
- MQTT subscriber stores every valid GPS message as a historical MySQL row.
- APIs return the assigned route, assigned vehicle, latest location, and history.
- `/health` and `/db-health` checks.

## Technologies and architecture

```text
Python GPS simulator -> Mosquitto MQTT broker -> FastAPI MQTT listener -> MySQL
Flutter app -> FastAPI REST API -> MySQL
```

The simulator publishes to `vehicles/BUS-001/gps` or `vehicles/BUS-002/gps`. The `vehicles/+/gps` subscriber accepts both topics. FastAPI validates the payload, matches the vehicle code to a database vehicle, and inserts a new `gps_data` record. It never overwrites earlier locations.

## Folder structure

```text
app/
  auth/             password hashing, JWT, current-user dependency
  models/           User, Route, Vehicle, GPSData SQLAlchemy tables
  routers/          login, profile, assignments, tracking endpoints
  schemas/          API request/response validation
  services/         MQTT subscriber
  main.py
  create_tables.py
  seed_demo_data.py
gps_simulator.py
requirements.txt
.env.example
```

## Modified from previous phases

- `app/main.py` was extended with the new routers, CORS for local Flutter web testing, and MQTT listener startup/shutdown. The earlier health endpoints remain.
- `app/models/gps_data.py` uses a MySQL-compatible UTC timestamp default and an index on vehicle plus timestamp for latest/history queries.
- `.env.example` was extended with JWT and MQTT settings and safe placeholder values. The real `.env` remains local and is ignored by Git.
- The existing MySQL database configuration and Route/User/Vehicle relationships were preserved; they were not migrated to PostgreSQL.

## Database design

- `routes.id` is the primary key; one route can have multiple vehicles and users.
- `vehicles.id` is the primary key and `vehicles.route_id` is a foreign key to `routes.id`.
- `users.id` is the primary key. `users.route_id` and `users.vehicle_id` point to that user's assignment.
- `gps_data.id` is the primary key; `gps_data.vehicle_id` points to `vehicles.id`. A vehicle has many GPS records, preserving history.
- Integer primary keys identify rows. Foreign keys connect rows and prevent accidental references to missing rows.

The assessment statement sometimes mentions PostgreSQL in its MQTT section, but the selected and already working database in this project is **MySQL**. No PostgreSQL migration was made.

## Environment variables

Copy `.env.example` to `.env`, then set the local MySQL username/password and a private random JWT secret. `.env` is ignored by Git; do not commit it.

| Name | Purpose |
| --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL connection |
| `JWT_SECRET_KEY` | Signs access tokens; keep secret and use a long random value |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 60) |
| `MQTT_HOST`, `MQTT_PORT` | Mosquitto address (local defaults shown) |
| `MQTT_ENABLED` | Set `false` to run API without connecting to MQTT |
| `DEMO_USER_PASSWORD` | Optional seed password override; demo-only |

## Installation and local run (Windows PowerShell)

From this directory, with MySQL running:

```powershell
Copy-Item .env.example .env
notepad .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.create_tables
python -m app.seed_demo_data
python -m uvicorn app.main:app --reload
```

If `.venv` already exists, activate it and skip the create command. The API is at `http://127.0.0.1:8000`; interactive API docs are at `http://127.0.0.1:8000/docs`. `GET /health` checks FastAPI and `GET /db-health` checks the MySQL connection.

For a physical phone on the same Wi-Fi, start the backend with `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`, then use the computer's LAN IP in Flutter's `API_BASE_URL`. Allow port 8000 through Windows Firewall if prompted.

Demo login for both seeded users is `DemoBus2026!` unless overridden before seeding:

| Email | Assigned route | Assigned vehicle |
| --- | --- | --- |
| `user-a@example.com` | Route A | BUS-001 |
| `user-b@example.com` | Route B | BUS-002 |

The seed command is safe to rerun and resets these demo account passwords to the configured demo password. Do not use these accounts in a public deployment.

## MQTT and GPS simulator

Install Mosquitto locally and start its broker on port 1883. For the normal Windows Mosquitto installer, start the Mosquitto service from Windows Services, or run its `mosquitto.exe` in a separate terminal. Then:

```powershell
# Terminal 1: broker (only if you are not using the Windows service)
mosquitto -v

# Terminal 2: from vehicle-tracking-backend, with .venv active
python gps_simulator.py

# Terminal 3: start the FastAPI server (if it is not already running)
python -m uvicorn app.main:app --reload
```

The simulator sends changing sample coordinates every two seconds for both buses. The MQTT payload includes `vehicle_id`, latitude, longitude, speed, and ISO-8601 UTC timestamp. Mosquitto is the broker: the simulator publishes messages to a topic, while FastAPI subscribes to those topics. The API can start while the broker is offline; it logs the connection failure and connects if the broker becomes available. MQTT persistence/replay across an API outage is not configured.

## API endpoints

All protected endpoints require `Authorization: Bearer <access_token>`. The backend does not accept an arbitrary vehicle selection as authorization.

| Method and URL | Auth | Purpose / request | Success / common errors |
| --- | --- | --- | --- |
| `POST /auth/login` | No | JSON `{"email":"user-a@example.com","password":"DemoBus2026!"}` | `200` token response; `401` invalid credentials; `403` inactive account; `422` malformed input |
| `GET /me` | Yes | Current user, no body | `200` user; `401` absent/invalid/expired token |
| `GET /me/route` | Yes | Signed-in user's assignment, no body | `200` route; `401` unauthorized |
| `GET /me/vehicle` | Yes | Signed-in user's vehicle, no body | `200` vehicle; `401` unauthorized |
| `GET /me/tracking/current` | Yes | Latest point for assigned vehicle | `200` GPS record; `404` no GPS yet; `401` unauthorized |
| `GET /me/tracking/history?limit=100` | Yes | Newest-first GPS history for assigned vehicle; limit 1–500 | `200` list (can be empty); `401` unauthorized |

For an authorization demonstration, add `?vehicle_id=BUS-002` while signed in as User A. The backend compares this code with the vehicle attached to the authenticated user and returns `403`. The query parameter is only a check/demo, never the source of access rights. The normal client does not send it.

Example with curl from PowerShell:

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/auth/login -ContentType 'application/json' -Body '{"email":"user-a@example.com","password":"DemoBus2026!"}'
$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri http://127.0.0.1:8000/me -Headers $headers
Invoke-RestMethod -Uri http://127.0.0.1:8000/me/route -Headers $headers
Invoke-RestMethod -Uri http://127.0.0.1:8000/me/vehicle -Headers $headers
Invoke-RestMethod -Uri http://127.0.0.1:8000/me/tracking/current -Headers $headers
Invoke-RestMethod -Uri http://127.0.0.1:8000/me/tracking/history -Headers $headers
```

To see the expected `403`, call the tracking endpoint with `?vehicle_id=BUS-002` and `$headers` for User A. To test unauthenticated access, call `/me` without `-Headers` and expect `401`.

## Authentication and authorization

The login endpoint finds the email in MySQL, verifies its Argon2 password hash, and returns a signed JWT. Protected endpoints decode the token to get the user ID and load that user. Tracking queries filter on `current_user.vehicle.id`; changing a vehicle ID in a request cannot change that database filter. The client stores the token with Flutter preferences for this local assessment app; production apps should use secure platform storage and HTTPS.

## Testing checklist

1. `GET /health` -> `{"status":"ok"}`.
2. `GET /db-health` -> `{"status":"ok","database":"connected"}`.
3. Seed command prints both route and vehicle assignments.
4. Login succeeds for each demo email; a wrong password returns `401`.
5. Protected request without token returns `401`.
6. User A `/me/route` and `/me/vehicle` show Route A and BUS-001; User B shows Route B and BUS-002.
7. User A request `GET /me/tracking/current?vehicle_id=BUS-002` returns `403`.
8. With broker, API, and simulator running, wait several seconds; current location returns a point and history grows with each message.
9. Use the Flutter README steps to check app login, dashboard, map, and error states.

The backend API, local Mosquitto broker, simulator, and MySQL storage were exercised together in this workspace. Flutter could not be built or run here because the Flutter SDK is not installed; follow the Flutter README on a machine with Flutter installed.

## Docker

Docker is optional and no Docker configuration is included. The assessment can be run locally using MySQL, Mosquitto, and Python.
