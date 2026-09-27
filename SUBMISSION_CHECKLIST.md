# Submission Checklist

Checked means verified in the current workspace. Flutter items remain open until run with an installed Flutter SDK; GitHub items remain open until the two public remotes are created and pushed.

## Backend

- [x] FastAPI starts and `/health` responds.
- [x] MySQL connection works (`/db-health` returned connected).
- [x] SQLAlchemy models and table creation work.
- [x] Authentication works (valid and invalid login checked).
- [x] Authorization works (both cross-vehicle requests returned 403).
- [x] MQTT subscriber works with local Mosquitto.
- [x] GPS simulator publishes changing sample coordinates.
- [x] Current-location API returns the latest saved point.
- [x] History API returns stored GPS records.
- [x] Backend README is present.

## Flutter

- [ ] Login screen runtime verified (Flutter SDK not installed here).
- [ ] API connection and JWT behavior runtime verified.
- [ ] Dashboard runtime verified.
- [ ] Assigned vehicle and route display runtime verified.
- [ ] Current location display runtime verified.
- [ ] Map tile display and moving marker runtime verified.
- [ ] Error handling runtime verified.
- [x] Flutter README and run instructions are present.
- [x] Dart source for these screens and services is present.

## GitHub

- [ ] Public backend repository created under `nishacodes-ind`.
- [ ] Public Flutter repository created under `nishacodes-ind`.
- [x] No `.env` file or local `.venv` is tracked in either local repo.
- [x] Secret-pattern scan of tracked files found no embedded credentials; expected environment configuration and demo documentation are not secrets.
- [x] Backend README is present.
- [x] Flutter README is present.
- [x] Both repositories have `.gitignore` files.
- [x] Both local Git repositories use the `main` branch and have an initial commit.
- [ ] Public repository access, README rendering, and pushed files verified on GitHub.
- [ ] Final commit pushed to both GitHub repositories.

## Known submission notes

- The project uses MySQL (`vehicle_tracking`) and PyMySQL; it was not migrated to PostgreSQL.
- GPS values are simulated; there is no physical GPS device.
- Flutter source has not been built or launched on this computer because Flutter is not installed.
- Docker Compose is not included.
