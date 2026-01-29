from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Team, Player, Match, PlayerPerformance

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(PlayerPerformance)

admin.site.site_header = "SportSight Admin"
admin.site.site_title = "SportSight Admin"
admin.site.index_title = "Dashboard"

def admin_extra_links(request):
    return format_html(
        '<div style="margin:10px 0;">'
        '<a style="margin-right:12px;" href="{}">📊 Analytics</a>'
        '<a style="margin-right:12px;" href="{}">⚔ Compare Players</a>'
        '<a href="{}">🏠 Custom Dashboard</a>'
        '</div>',
        reverse("analytics"),
        reverse("compare"),
        reverse("dashboard")
    )

# Inject links into every admin page header
admin.site.each_context = (lambda original: (lambda request: {
    **original(request),
    "extra_links": admin_extra_links(request),
}))(admin.site.each_context)
