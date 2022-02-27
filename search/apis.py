from django.http import HttpResponseBadRequest

from search.forms import CommentForm
from search.models import *


def comment(request):
    if request.method == "POST":
        item_type = request.GET.get('type', '')
        item_id = int(request.GET.get('id', ''))
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            comment = commentform.save(commit=False)
            # TODO get current author, do not save if not present
            print(request.user)
            comment.author = Person.objects.filter(name__istartswith="Nat")[0]
            comment.save()
            commentform.save_m2m()

            if item_type == 'Q':
                question = Question.objects.get(pk=item_id)
                question.comments.add(comment)
                question.tags.add(*comment.tags.all())
                print('Added tags')

            return comment.id
    return HttpResponseBadRequest()
