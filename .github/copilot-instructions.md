# SportSight Codebase Instructions

## Project Overview
SportSight is a Django 5.2 web application for tracking football/soccer player performance analytics. It combines team management, match tracking, and player performance comparison with a role-based authentication system (admin vs. regular users).

## Architecture

### Django Structure
- **Project**: `config/` - Contains settings, URL routing (root), and WSGI/ASGI entry points
- **App**: `core/` - Single app handling all models, views, and templates
- **Database**: SQLite3 at project root (development only)
- **Authentication**: Built-in Django auth with staff/is_staff flag for admin distinction

### Key Data Model (core/models.py)
```
Team → Players → Matches ← PlayerPerformance (join table)
```
- `Team`: Team entities with unique names
- `Player`: Associates to Team via FK, includes position and jersey number
- `Match`: Match records with date, opponent, venue
- `PlayerPerformance`: Bridge table linking Players to Matches with performance metrics (goals, assists, tackles, shots_on_target, pass_accuracy, saves)

### Critical Pattern: Role-Based Access Control
In [core/views.py](core/views.py) login redirects users based on staff status:
- `user.is_staff = True` → admin dashboard
- `user.is_staff = False` → user dashboard
All views requiring access use `@login_required` decorator with role checks inside view logic.

## Development Workflow

### Running the Server
```bash
python manage.py runserver
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Panel Access
Django admin at `/admin/` - add users and teams via admin interface directly.

### Template Structure
- Root templates: `templates/` (base_site.html)
- App templates: `core/templates/core/` (home, login, dashboards, analytics, compare pages)
- Static files: `core/static/core/` (CSS, JS, images organized hierarchically)

## Code Conventions

### View Pattern
Views follow a consistent pattern:
- Check `@login_required` first
- Validate role/permissions inside view (e.g., `if not request.user.is_staff`)
- Fetch aggregated data using QuerySet optimizations (e.g., `select_related()`, `order_by()`)
- Build context dict and render template

### QuerySet Optimizations
Use `select_related()` for foreign keys to avoid N+1 queries:
```python
PlayerPerformance.objects.select_related("player").order_by("id")
```

### Common Analytics Operations
- Totals: Manual summation of model fields (`sum(x.goals for x in qs)`)
- No aggregation functions used yet (room for ORM optimization)

## Key Integration Points

1. **Authentication Flow**:
   - Login: `login_page()` → authenticate() → role check redirect
   - Logout: `logout_view()` → redirect to login
   - Settings: `LOGIN_URL="/login/"`, `LOGIN_REDIRECT_URL="/dashboard/"`, `LOGOUT_REDIRECT_URL="/login/"`

2. **Analytics Features**:
   - [analytics_page()](core/views.py#L49): Fetches all PlayerPerformance, builds match labels and goals list for charting
   - [compare_page()](core/views.py#L67): Compares two players across all their matches, generates insight string

3. **Static & Media**:
   - `STATIC_URL='/static/'` - served from `core/static/core/`
   - No media files configured yet

## Common Tasks

**Adding a new view**: 
1. Define function in [core/views.py](core/views.py), add `@login_required` if needed
2. Add role checks inside (e.g., `if not request.user.is_staff`)
3. Register in [core/urls.py](core/urls.py) with unique name

**Adding a new model field**:
1. Edit [core/models.py](core/models.py)
2. Run `python manage.py makemigrations && python manage.py migrate`

**Modifying analytics calculations**:
- Current approach is manual Python summation - consider migrating to Django ORM aggregation for performance (`.annotate()`, `.aggregate()`)

## Development Notes

- **No external dependencies**: Only uses Django core and built-in SQLite
- **Production warning**: DEBUG=True, ALLOWED_HOSTS=[], SECRET_KEY exposed in settings - replace before deployment
- **No API layer**: All interactions through HTML forms/views; no REST endpoints
- **Testing structure**: tests.py exists but empty - no test suite established
