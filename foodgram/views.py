from django.shortcuts import render
from django.views.generic import TemplateView


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


class AboutAuthorView(TemplateView):
    template_name = 'static_templates/about-author.html'


class AboutTechView(TemplateView):
    template_name = 'static_templates/about-tech.html'
