from django.core.paginator import Paginator

POST_PAGES: int = 10


def paginate_page(request, post_list):
    page_obj = Paginator(post_list, POST_PAGES)
    page_number = request.GET.get('page')
    return page_obj.get_page(page_number)