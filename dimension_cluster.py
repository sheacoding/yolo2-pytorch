"""
Copyright (C) 2017, 申瑞珉 (Ruimin Shen)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import argparse
import configparser
import logging

import numpy as np
import nltk.cluster.kmeans
from PIL import Image

import utils.data
import utils.iou.numpy


def distance(a, b):
    return 1 - utils.iou.numpy.iou(-a, a, -b, b)


def image_size(path):
    with Image.open(path) as image:
        return image.size


def get_data(paths):
    dataset = utils.data.Dataset(paths)
    return np.concatenate([(data['yx_max'] - data['yx_min']) / image_size(data['path']) for data in dataset.dataset])


def main():
    args = make_args()
    config = configparser.ConfigParser()
    utils.load_config(config, args.config)
    if args.level:
        logging.getLogger().setLevel(args.level.upper())
    cache_dir = utils.get_cache_dir(config)
    paths = [os.path.join(cache_dir, phase + '.pkl') for phase in args.phase]
    data = get_data(paths)
    logging.info('num_examples=%d' % len(data))
    clusterer = nltk.cluster.kmeans.KMeansClusterer(args.num, distance, args.repeats)
    clusterer.cluster(data)
    for m in clusterer.means():
        print('\t'.join(map(str, m)))


def make_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('num', type=int)
    parser.add_argument('-r', '--repeats', type=int, default=300)
    parser.add_argument('-c', '--config', nargs='+', default=['config.ini'], help='config file')
    parser.add_argument('-p', '--phase', nargs='+', default=['train', 'val', 'test'])
    parser.add_argument('--level', default='info', help='logging level')
    return parser.parse_args()

if __name__ == '__main__':
    main()
