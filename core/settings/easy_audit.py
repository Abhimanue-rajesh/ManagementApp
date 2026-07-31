# Record model create, update and delete events.
DJANGO_EASY_AUDIT_WATCH_MODEL_EVENTS = True

# Record login, logout and failed-login events.
DJANGO_EASY_AUDIT_WATCH_AUTH_EVENTS = True

# Request logging can create a very large number of database rows.
# Start with False and enable it only when you actually need it.
DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = False

# Audit records should not be manually edited or deleted from admin.
DJANGO_EASY_AUDIT_READONLY_EVENTS = True

# Do not create an update event when nothing actually changed.
DJANGO_EASY_AUDIT_CRUD_EVENT_NO_CHANGED_FIELDS_SKIP = True

# Raise audit-related errors during development only.
DJANGO_EASY_AUDIT_PROPAGATE_EXCEPTIONS = False

DJANGO_EASY_AUDIT_UNREGISTERED_URLS_EXTRA = [
    r"^/static/.*$",
    r"^/media/.*$",
    r"^/favicon\.ico$",
    r"^/jsi18n/.*$",
    r"^/autocomplete/.*$",
]
