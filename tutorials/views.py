import markdown
import nh3
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from tutorials.models import Tutorial


class TutorialLoginView(LoginView):
    template_name = "tutorials/tutorials_login.html"
    next_page = reverse_lazy("tutorials:list")
    redirect_authenticated_user = True

    def get_success_url(self):
        # Always open the tutorial list after login.
        return str(self.next_page)


@login_required(login_url="tutorials:login")
def tutorial_list(request):
    tutorials = Tutorial.objects.filter(is_published=True)

    return render(
        request,
        "tutorials/list.html",
        {"tutorials": tutorials},
    )


@login_required(login_url="tutorials:login")
def tutorial_detail(request, pk):
    tutorial = get_object_or_404(
        Tutorial,
        pk=pk,
        is_published=True,
    )

    rendered = markdown.markdown(
        tutorial.content,
        extensions=["extra", "sane_lists"],
    )

    content_html = nh3.clean(
        rendered,
        tags={
            "p",
            "br",
            "hr",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "strong",
            "em",
            "del",
            "blockquote",
            "ul",
            "ol",
            "li",
            "pre",
            "code",
            "a",
            "img",
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
        },
        attributes={
            "a": {"href", "title"},
            "img": {"src", "alt", "title"},
            "code": {"class"},
            "ol": {"start"},
        },
        url_schemes={"http", "https", "mailto"},
    )

    return render(
        request,
        "tutorials/detail.html",
        {
            "tutorial": tutorial,
            "content_html": content_html,
        },
    )
