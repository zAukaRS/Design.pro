def categories_context(request):
    from .models import Category
    return {'all_categories': Category.objects.all()}
