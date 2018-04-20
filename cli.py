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

# Import video settings
from video_annot.settings import VIDEOS_FOLDER
from video_annot.settings import VIDEOS_PARTS_FOLDER
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
    path = os.path.join(folder, "%(id)s.{}".format(FORMAT))
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
    cmd = 'youtube-dl --format {} --merge-output-format {} --match-filter="{}" --output="{}" {} "{}"'.format(FORMAT, FORMAT, filters, path, other, full_query)
    call(cmd, shell=True)


def split_videos(*, folder=VIDEOS_FOLDER, out=VIDEOS_PARTS_FOLDER, duration_sec=5):
    for filename in glob.glob(os.path.join(folder, '**', '*.{}'.format(FORMAT))):
        out_folder = os.path.dirname(filename).replace(folder, out)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        filename_without_ext, _ = os.path.splitext(os.path.basename(filename))
        tpl = 'ffmpeg -i {} -threads 4 -vcodec copy -f segment -segment_time {} {}/{}_part_%06d.{}'
        cmd = tpl.format(
            filename,
            duration_sec,
            out_folder,
            filename_without_ext,
            FORMAT
        )
        call(cmd, shell=True)


def add_videos(*, label=None, folder=VIDEOS_FOLDER):
    if label is None:
        labels = [l.name for l in models.LabelType.objects.all()]
    else:
        labels = [label]
    
    for label in labels:
        if models.LabelType.objects.filter(name=label).count() == 0:
            print('label type not found in the database, creating a label type named "{}"'.format(label))
            label_type = _create_label_type(label)
        else:
            label_type = models.LabelType.objects.get(name=label)
        print('---> Using "{}" as a LabelType'.format(label))
        print('Adding videos...')
        pattern = '*.{}'.format(FORMAT)
        for filename in glob.glob(os.path.join(folder, label, pattern)):
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
    run([download, add_videos, split_videos])
