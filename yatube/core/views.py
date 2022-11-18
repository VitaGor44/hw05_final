# from django.shortcuts import render
#
#
# def page_not_found(request, exception):
#     # Переменная exception содержит отладочную информацию,
#     # в шаблон пользовательской страницы 404 она не выводится
#     return render(
#         request,
#         "core/404.html",
#         {"path": request.path},
#         status=404
#     )
#
# def server_error(request):
#         return render(request, "core/500.html", status=500)
#
# def permission_denied(request, exception):
#     return render(request, 'core/403.html', status=403)