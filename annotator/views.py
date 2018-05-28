from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Video
from .models import Label
from .models import LabelType
from django.contrib.auth.models import User

def index(request):
    return render(request, 'annotator/index.html')


def nothing(request):
    return render(request, 'annotator/nothing.html')


@login_required
def class_selection(request):
    classes = []
    for label_type in LabelType.objects.all():
        nb_annotated = _get_nb_annotated_videos(request.user.id, label_type.id)
        nb_total = _get_total_nb_videos(label_type.id)
        name = label_type.name.replace('_', ' ')
        slug = label_type.name
        classes.append((name, slug, nb_annotated, nb_total))
    context = {'classes': classes}
    return render(request, 'annotator/class_selection.html', context)


@login_required
def random_video(request):
    class_name = request.GET.get('class')
    try:
        saved = _insert_annotation_if_post_request(request)
        if saved:
            return redirect(request.path_info + '?class={}'.format(class_name))

    except AlreadyAnnotatedError:
        return render(request, 'annotator/annotated.html')

    if class_name != '':
        label_type_id = LabelType.objects.filter(name=class_name).first().id
        where = ' AND v.query_label_type_id={}'.format(label_type_id)
    else:
        where = ''
    try:
        # return one non-annotated video randomly
        req = (
            "SELECT * FROM annotator_video as v WHERE v.id NOT IN "
            "(SELECT l.video_id FROM annotator_label as l, auth_user as u "
            "WHERE u.id=l.user_id AND u.username='{}') {} ORDER BY RANDOM() "
            "LIMIT 1"
        )
        req = req.format(request.user, where)
        videos = Video.objects.raw(req)
        video = videos[0]
    except IndexError:
        return redirect('nothing')
    nb_annotated = _get_nb_annotated_videos(request.user.id, label_type_id)
    nb_total = _get_total_nb_videos(label_type_id)
    nb_remaining = nb_total - nb_annotated
    context = {
        'video': video,
        'nb_annotated': nb_annotated,
        'nb_remaining': nb_remaining,
        'nb_total': nb_total,
    }
    return render(request, 'annotator/video.html', context)

def _get_nb_annotated_videos(user_id, label_type_id):
    return Label.objects.filter(user__id=user_id).filter(label_type_id=label_type_id).count()


def _get_total_nb_videos(label_type_id):
    return Video.objects.filter(query_label_type_id=label_type_id).count()


def _insert_annotation_if_post_request(request):
    saved = False
    if request.method == 'POST':
        answer = request.POST.get('submit')
        video_id = int(request.POST.get('video_id'))
        video = Video.objects.get(id=video_id)
        if answer not in ('Yes', 'No', 'Not sure'):
            raise ValueError(
                'Issue in the form: "answer" should be either "Yes" or "No"')
        nb = Label.objects.filter(user=request.user, video=video).count()
        if nb > 0:
            raise AlreadyAnnotatedError()
        if answer == 'Yes':
            value = Label.YES
        elif answer == 'No':
            value = Label.NO
        elif answer == 'Not sure':
            value = Label.NOT_SURE
        label = Label(
            label_type=video.query_label_type,
            video=video,
            user=request.user,
            value=value,
        )
        label.save()
        saved = True
    return saved


class AlreadyAnnotatedError(Exception):
    pass
