from clize import run
from subprocess import call
from hashlib import sha256
import os
import glob

# setting up django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_annot.settings")
django.setup()
from django.contrib.auth.models import User

from video_annot.settings import VIDEOS_FOLDER
from video_annot.settings import ADMIN
from video_annot.settings import FORMAT
from annotator import models


admin = User.objects.get(username=ADMIN)

def download(query, *, nb=10, max_duration=60, other='', label=None, out=VIDEOS_FOLDER):
    full_query = 'ytsearch{}:{}'.format(nb, query)
    filters = 'duration < {}'.format(max_duration)
    if label is None:
        label = _slug(query)
    folder = os.path.join(out, label)
    path = os.path.join(folder, "%(id)s.mp4")
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
    cmd = 'youtube-dl --format mp4 --merge-output-format mp4 --match-filter="{}" --output="{}" {} "{}"'.format(filters, path, other, full_query)
    call(cmd, shell=True)


def add_videos(label):
    if models.LabelType.objects.filter(name=label).count() == 0:
        print('label not found, creating LabelType named "{}"'.format(label))
        label_type = _create_label_type(label)
    else:
        label_type = models.LabelType.objects.get(name=label)
    print('---> Using "{}" as a LabelType'.format(label))
    print('Adding videos...')
    for filename in glob.glob(os.path.join(VIDEOS_FOLDER, label, '*.mp4')):
        print('Adding "{}"'.format(filename))
        try:
            video = models.Video(url=filename, user=admin, query_label_type=label_type)
            video.save()
        except django.db.utils.IntegrityError as ex:
            print(ex)
            print('Video already exists, passing...')

def _create_label_type(name):
    return models.LabelType(name=name, user=admin).save()

def _slug(s):
    return s.replace(' ', '_')

def _unslug(s):
    return s.replace('_', ' ')

if __name__ == '__main__':
    run([download, add_videos])
