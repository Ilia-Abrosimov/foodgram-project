from .models import Follow, Recipe


def extend_context(context, user):
    context['purchase_list'] = Recipe.objects.filter(purchase_by=user)
    context['favorites'] = Recipe.objects.filter(favorite_by=user)
    return context


def add_subscription_status(context, user, author):
    context['is_subscribed'] = Follow.objects.filter(
        user=user, author=author
    ).exists()
    return context


def tag_filter(model, tags):
    if tags:
        return model.objects.prefetch_related(
                'author', 'tags'
            ).filter(
                tags__slug__in=tags
            ).distinct()
    else:
        return model.objects.prefetch_related(
                'author', 'tags'
            ).all()
