from django.templatetags.static import static
from django.urls import reverse, reverse_lazy

from core.settings.permissions import (  # can_view_task_dashboard,
    assigner_view_all_daily_tasks,
    can_view_main_dashboard,
    is_superuser,
    view_only_workers_task,
)

UNFOLD = {
    "DASHBOARD_CALLBACK": "dashboard.views.dashboard_callback",
    "SITE_TITLE": "Internal Application - The Deep Seafood",
    "SITE_HEADER": "Internal Application",
    "SITE_SUBHEADER": "The Deep Seafood",
    "SHOW_BACK_BUTTON": True,
    "SCRIPTS": [
        lambda request: static("js/main.js"),
    ],
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": "Navigation",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "permission": can_view_main_dashboard,
                    },
                ],
            },
            {
                "title": "Projects",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "All Projects",
                        "icon": "folder_open",
                        "link": reverse_lazy("admin:tasks_project_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tasks.view_project"
                        ),
                    },
                    {
                        "title": "Categories",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:tasks_taskcategory_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tasks.view_taskcategory"
                        ),
                    },
                    {
                        "title": "Departments",
                        "icon": "apartment",
                        "link": reverse_lazy("admin:tasks_department_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tasks.view_department"
                        ),
                    },
                    {
                        "title": "Types",
                        "icon": "account_tree",
                        "link": reverse_lazy("admin:tasks_projecttype_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tasks.view_projecttype"
                        ),
                    },
                ],
            },
            {
                "title": "Tasks",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "All Daily Tasks",
                        "icon": "today",
                        "link": reverse_lazy("admin:daily_task_dashboard"),
                        "permission": assigner_view_all_daily_tasks,
                    },
                    {
                        "title": "My Daily Tasks",
                        "icon": "today",
                        "link": lambda request: (
                            f"{reverse_lazy('admin:tasks_dailytask_changelist')}?my_tasks=1"
                        ),
                        "permission": view_only_workers_task,
                    },
                    {
                        "title": "Brands",
                        "icon": "sell",
                        "link": reverse_lazy("admin:tasks_brand_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tasks.view_brand"
                        ),
                    },
                ],
            },
            {
                "title": "Support Tickets",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "All Tickets",
                        "icon": "confirmation_number",
                        "link": reverse_lazy("admin:tickets_supportticket_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tickets.view_supportticket"
                        ),
                    },
                    {
                        "title": "Ticket History",
                        "icon": "history",
                        "link": reverse_lazy(
                            "admin:tickets_supporttickethistory_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "tickets.view_supporttickethistory"
                        ),
                    },
                    {
                        "title": "Ticket Routings",
                        "icon": "route",
                        "link": reverse_lazy("admin:tickets_ticketrouting_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tickets.view_ticketrouting"
                        ),
                    },
                    {
                        "title": "Ticket Statuses",
                        "icon": "flag",
                        "link": reverse_lazy("admin:tickets_ticketstatus_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "tickets.view_ticketstatus"
                        ),
                    },
                ],
            },
            {
                "title": "Subscription Management",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "Subscriptions",
                        "icon": "subscriptions",
                        "link": reverse_lazy(
                            "admin:subscriptions_subscriptiontracker_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "subscriptions.view_subscriptiontracker"
                        ),
                    },
                    {
                        "title": "Payment Cards",
                        "icon": "credit_card",
                        "link": reverse_lazy(
                            "admin:subscriptions_paymentcard_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "subscriptions.view_paymentcard"
                        ),
                    },
                    {
                        "title": "Currencies",
                        "icon": "currency_exchange",
                        "link": reverse_lazy("admin:subscriptions_currency_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "subscriptions.view_currency"
                        ),
                    },
                    {
                        "title": "Payment Timings",
                        "icon": "schedule",
                        "link": reverse_lazy(
                            "admin:subscriptions_paymenttiming_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "subscriptions.view_paymenttiming"
                        ),
                    },
                ],
            },
            {
                "title": "Web Management",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "Domains",
                        "icon": "language",
                        "link": reverse_lazy(
                            "admin:web_management_domainmanager_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "web_management.view_domainmanager"
                        ),
                    },
                    {
                        "title": "Domain Registrars",
                        "icon": "business",
                        "link": reverse_lazy(
                            "admin:web_management_registrar_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "web_management.view_registrar"
                        ),
                    },
                    {
                        "title": "Web Pages and Forms",
                        "icon": "web",
                        "link": reverse_lazy(
                            "admin:web_management_webpagemanager_changelist"
                        ),
                        "permission": lambda request: request.user.has_perm(
                            "web_management.view_webpagemanager"
                        ),
                    },
                    {
                        "title": "DNS Zones",
                        "icon": "dns",
                        "link": reverse_lazy("admin:web_management_dnszone_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "web_management.view_dnszone"
                        ),
                    },
                ],
            },
            {
                "title": "User Management",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "auth.view_user"
                        ),
                    },
                    {
                        "title": "Groups and Permissions",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "auth.view_group"
                        ),
                    },
                    {
                        "title": "Group Members",
                        "icon": "groups",
                        "link": reverse_lazy("group_members_dashboard"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": "Other Tools",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": "Credentials",
                        "icon": "key",
                        "link": reverse_lazy("admin:credentials_credential_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "credentials.view_credential"
                        ),
                    },
                    {
                        "title": "Quick Copy",
                        "icon": "content_copy",
                        "link": reverse_lazy("admin:quickcopy_quickcopy_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "quickcopy.view_quickcopy"
                        ),
                    },
                ],
            },
            {
                "title": ("Developer Tools"),
                "collapsible": True,
                "separator": True,
                "permission": is_superuser,
                "items": [
                    {
                        "title": ("Model Visualizer"),
                        "icon": "hub",
                        "link": lambda request: reverse("django-lumen-diagram"),
                        "permission": is_superuser,
                    },
                    {
                        "title": ("Model Activity"),
                        "icon": "history",
                        "link": reverse_lazy("admin:easyaudit_crudevent_changelist"),
                        "permission": is_superuser,
                    },
                    {
                        "title": ("Login Activity"),
                        "icon": "login",
                        "link": reverse_lazy("admin:easyaudit_loginevent_changelist"),
                        "permission": is_superuser,
                    },
                    {
                        "title": ("Request Activity"),
                        "icon": "language",
                        "link": reverse_lazy("admin:easyaudit_requestevent_changelist"),
                        "permission": is_superuser,
                    },
                ],
            },
        ],
    },
}
