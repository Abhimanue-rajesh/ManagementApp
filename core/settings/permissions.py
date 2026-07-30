def can_view_main_dashboard(request):
    return not request.user.groups.filter(
        name__in=[
            "Daily Task Workers",
            "Daily Task Assigners",
        ]
    ).exists()


def can_view_task_dashboard(request):
    return request.user.groups.filter(name="Daily Task Assigners").exists()


def view_only_workers_task(request):
    return (
        request.user.groups.filter(name="Daily Task Workers").exists()
        and not request.user.groups.filter(name="Daily Task Assigners").exists()
    )


def assigner_view_all_daily_tasks(request):
    return (
        request.user.groups.filter(name="Daily Task Assigners").exists()
        and not request.user.groups.filter(name="Daily Task Workers").exists()
    )
