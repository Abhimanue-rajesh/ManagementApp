from tasks.admin.daily_tasks import Brand, DailyTask
from tasks.admin.projects import (
    DepartmentAdmin,
    ProjectAdmin,
    ProjectHistoryAdmin,
    ProjectHistoryInline,
    ProjectTypeAdmin,
    TaskActionStepInline,
    TaskActivityAdmin,
    TaskAdmin,
    TaskCategoryAdmin,
)

__all__ = [
    "ProjectHistoryInline",
    "ProjectAdmin",
    "DepartmentAdmin",
    "ProjectTypeAdmin",
    "ProjectHistory",
    "ProjectHistoryAdmin",
    "TaskActionStepInline",
    "TaskActivityAdmin",
    "TaskAdmin",
    "TaskCategoryAdmin",
    "Brand",
    "DailyTask",
]
