from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import (
    NoReverseMatch,
    URLPattern,
    URLResolver,
    get_resolver,
    reverse,
)


class AllPagesLoadTest(TestCase):
    """
    Check that all normal static pages available to a superuser load
    without unexpected errors.

    Special endpoints such as autocomplete and read-only model add pages
    are skipped before requesting them.
    """

    # URLs that should not be requested during this page-load test.
    EXCLUDED_URLS = {
        # Authentication actions
        "admin:logout",
        "admin:password_change",
        "admin:password_change_done",
        # Django Admin AJAX endpoint that requires query parameters.
        "admin:autocomplete",
        # Read-only history models where manual creation is blocked.
        "admin:tasks_projecthistory_add",
        "admin:tickets_supporttickethistory_add",
    }

    # Paths that are not normal HTML pages.
    EXCLUDED_PATH_PREFIXES = (
        "/static/",
        "/media/",
        "/api/",
    )

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.superuser = User.objects.create_superuser(
            username="test_superadmin",
            email="superadmin@example.com",
            password="StrongTestPassword123!",
        )

    def setUp(self):
        self.client.force_login(self.superuser)

    def test_all_named_pages_load_for_superuser(self):
        passed_urls = []
        skipped_urls = []
        failed_urls = []

        url_names = sorted(set(self.get_named_urls()))

        for url_name in url_names:
            # Skip protected or action-based URLs before making a request.
            if url_name in self.EXCLUDED_URLS:
                skipped_urls.append(
                    (
                        url_name,
                        None,
                        self.get_exclusion_reason(url_name),
                    )
                )
                continue

            try:
                url = reverse(url_name)
            except NoReverseMatch:
                skipped_urls.append(
                    (
                        url_name,
                        None,
                        "Requires URL arguments",
                    )
                )
                continue

            if url.startswith(self.EXCLUDED_PATH_PREFIXES):
                skipped_urls.append(
                    (
                        url_name,
                        url,
                        "Excluded path prefix",
                    )
                )
                continue

            try:
                response = self.client.get(
                    url,
                    follow=True,
                )
            except Exception as error:
                failed_urls.append(
                    (
                        url_name,
                        url,
                        f"{type(error).__name__}: {error}",
                    )
                )
                continue

            if response.status_code >= 400:
                failed_urls.append(
                    (
                        url_name,
                        url,
                        response.status_code,
                    )
                )
                continue

            passed_urls.append(
                (
                    url_name,
                    url,
                    response.status_code,
                )
            )

        self.print_report(
            passed_urls=passed_urls,
            skipped_urls=skipped_urls,
            failed_urls=failed_urls,
        )

        self.assertFalse(
            failed_urls,
            self.format_failure_message(failed_urls),
        )

    def get_named_urls(self):
        """
        Collect all named URLs from the project's root URL configuration.
        """
        resolver = get_resolver()

        return self.walk_url_patterns(
            patterns=resolver.url_patterns,
        )

    def walk_url_patterns(self, patterns, namespaces=None):
        """
        Recursively collect URL names while preserving namespaces.
        """
        namespaces = namespaces or []
        collected_urls = []

        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                current_namespaces = namespaces.copy()

                if pattern.namespace:
                    current_namespaces.append(pattern.namespace)

                collected_urls.extend(
                    self.walk_url_patterns(
                        patterns=pattern.url_patterns,
                        namespaces=current_namespaces,
                    )
                )

            elif isinstance(pattern, URLPattern) and pattern.name:
                full_name = ":".join([*namespaces, pattern.name])

                collected_urls.append(full_name)

        return collected_urls

    def get_exclusion_reason(self, url_name):
        reasons = {
            "admin:logout": "Logout action",
            "admin:password_change": "Password action page",
            "admin:password_change_done": "Password action page",
            "admin:autocomplete": (
                "Django Admin AJAX endpoint requiring query parameters"
            ),
            "admin:tasks_projecthistory_add": ("Project history is read-only"),
            "admin:tickets_supporttickethistory_add": (
                "Support ticket history is read-only"
            ),
        }

        return reasons.get(
            url_name,
            "Explicitly excluded",
        )

    def print_report(
        self,
        passed_urls,
        skipped_urls,
        failed_urls,
    ):
        print("\n")
        print("=" * 100)
        print("SUPERUSER PAGE ACCESSIBILITY REPORT")
        print("=" * 100)

        print(f"\nPassed pages: {len(passed_urls)}")

        for url_name, url, status_code in passed_urls:
            print(f"[PASS {status_code}] " f"{url_name:<60} " f"{url}")

        print(f"\nSkipped URLs: {len(skipped_urls)}")

        for url_name, url, reason in skipped_urls:
            url_display = url or "-"

            print(f"[SKIPPED] " f"{url_name:<60} " f"{url_display} — {reason}")

        print(f"\nFailed pages: {len(failed_urls)}")

        for url_name, url, error in failed_urls:
            print(f"[FAILED] " f"{url_name:<60} " f"{url} — {error}")

        print("\n" + "-" * 100)
        print(f"Passed:  {len(passed_urls)}")
        print(f"Skipped: {len(skipped_urls)}")
        print(f"Failed:  {len(failed_urls)}")

        print("\nRESULT: PASSED" if not failed_urls else "\nRESULT: FAILED")

        print("=" * 100)

    def format_failure_message(self, failed_urls):
        lines = [
            "",
            "The following pages failed to load:",
        ]

        for url_name, url, error in failed_urls:
            lines.append(f"- {url_name}: {url} — {error}")

        return "\n".join(lines)
