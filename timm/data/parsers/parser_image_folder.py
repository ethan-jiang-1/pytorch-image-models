""" A dataset parser that reads images from folders

Folders are scannerd recursively to find image files. Labels are based
on the folder hierarchy, just leaf folders by default.

Hacked together by / Copyright 2020 Ross Wightman
"""
import os

from timm.utils.misc import natural_key

from .parser import Parser
from .class_map import load_class_map
from .constants import IMG_EXTENSIONS


def find_images_and_targets(folder, types=IMG_EXTENSIONS, class_to_idx=None, leaf_name_only=True, sort=True):
    labels = []
    filenames = []
    for root, subdirs, files in os.walk(folder, topdown=False, followlinks=True):
        rel_path = os.path.relpath(root, folder) if (root != folder) else ''
        label = os.path.basename(rel_path) if leaf_name_only else rel_path.replace(os.path.sep, '_')
        for f in files:
            base, ext = os.path.splitext(f)
            if ext.lower() in types:
                filenames.append(os.path.join(root, f))
                labels.append(label)
    if class_to_idx is None:
        # building class index
        unique_labels = set(labels)
        sorted_labels = list(sorted(unique_labels, key=natural_key))
        class_to_idx = {c: idx for idx, c in enumerate(sorted_labels)}
    images_and_targets = [(f, class_to_idx[l]) for f, l in zip(filenames, labels) if l in class_to_idx]
    if sort:
        images_and_targets = sorted(images_and_targets, key=lambda k: natural_key(k[0]))
    return images_and_targets, class_to_idx


class ParserImageFolder(Parser):

    def __init__(
            self,
            root,
            class_map=''):
        super().__init__()

        self.root = root
        class_to_idx = None
        if class_map:
            class_to_idx = load_class_map(class_map, root)
        self.samples, self.class_to_idx = find_images_and_targets(root, class_to_idx=class_to_idx)
        if len(self.samples) == 0:
            raise RuntimeError(
                f'Found 0 images in subfolders of {root}. Supported image extensions are {", ".join(IMG_EXTENSIONS)}')

        #ethan changed 0:
        self._hack_check_if_cache_needed()

    # ethan changed 1: add _get_img_data_xxx methods
    def _hack_check_if_cache_needed(self):
        if hasattr(self, "cache_needed"):
            return self.hk_cache_needed
        if "HACK_CACHE_NEEDED" in os.environ:
            self.hk_cache_needed = True
        else:
            self.hk_cache_needed = False
        self.hk_cache = {}

    def _hack_get_img_data_from_fs(self, index):
        path, target = self.samples[index]
        return open(path, 'rb'), target

    def _hack_get_img_data_from_cache(self, index):
        import io
        path, target = self.samples[index]
        if path not in self.hk_cache:
            with open(path, 'rb') as f:
                content = f.read()
            self.hk_cache[path] = content 
        content = self.hk_cache[path]
        return io.BytesIO(content), target
            
    def __getitem__(self, index):
        # ethan changed 2: the original code here is defined in _get_img_data_from_fs
        if self.hk_cache_needed:
            return self._hack_get_img_data_from_cache(index)
        else:
            return self._hack_get_img_data_from_fs(index)

    def __len__(self):
        return len(self.samples)

    def _filename(self, index, basename=False, absolute=False):
        filename = self.samples[index][0]
        if basename:
            filename = os.path.basename(filename)
        elif not absolute:
            filename = os.path.relpath(filename, self.root)
        return filename
