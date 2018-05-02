from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Video
from .models import Label
from .models import LabelType


def index(request):
    return render(request, 'annotator/index.html')


def nothing(request):
    return render(request, 'annotator/nothing.html')


@login_required
def class_selection(request):
    classes = []
    for label_type in LabelType.objects.filter():
        name = label_type.name.replace('_', ' ')
        slug = label_type.name
        classes.append((name, slug))
    context = {'classes': classes}
    return render(request, 'annotator/class_selection.html', context)


@login_required
def random_video(request):
    try:
        _insert_annotation_if_post_request(request)
    except AlreadyAnnotatedError:
        return render(request, 'annotator/annotated.html')

    class_name = request.GET.get('class')
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
    context = {'video': video}
    return render(request, 'annotator/video.html', context)


@login_required
def video(request, video_id):
    try:
        _insert_annotation_if_post_request(request)
    except AlreadyAnnotatedError:
        return render(request, 'annotator/annotated.html')
    video = Video.objects.get(id=video_id)
    nb = Label.objects.filter(user=request.user, video=video).count()
    if nb > 0:
        return render(request, 'annotator/annotated.html')
    context = {'video': video}
    return render(request, 'annotator/video.html', context)


def _insert_annotation_if_post_request(request):
    if request.method == 'POST':
        answer = request.POST.get('submit')
        video_id = int(request.POST.get('video_id'))
        video = Video.objects.get(id=video_id)
        if answer not in ('Yes', 'No'):
            raise ValueError(
                'Issue in the form: "answer" should be either "Yes" or "No"')
        answer = True if answer == 'Yes' else False
        nb = Label.objects.filter(user=request.user, video=video).count()
        if nb > 0:
            raise AlreadyAnnotatedError()
        label = Label(
            label_type=video.query_label_type,
            video=video,
            user=request.user,
            video_has_label=answer,
        )
        label.save()


class AlreadyAnnotatedError(Exception):
    pass
