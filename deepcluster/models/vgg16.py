# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import torch
import torch.nn as nn
import math
from random import random as rd

__all__ = [ 'VGG', 'vgg16', 'vgg16_tweak']


class VGG(nn.Module):

    def __init__(self, features, num_cluster, num_category):
        super(VGG, self).__init__()
        self.features = features
        # window size 128 / 2^5 = 4
        self.classifier = nn.Sequential(
            nn.Linear(512 * 1 * 1, 4096),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(4096, 128),
            nn.ReLU(True), # should be removed
        )
        self.cluster_layer = nn.Sequential(
            nn.Linear(128, num_cluster),  # nn.Linear(4096, num_cluster),
            nn.Softmax(dim=1),  # should be removed and replaced by ReLU for category_layer
        )
        self.category_layer = nn.Sequential(
            nn.Linear(128, num_category),
            nn.Softmax(dim=1),
        )
        self._initialize_weights()
        # if sobel:
        #     # grayscale = nn.Conv2d(3, 1, kernel_size=1, stride=1, padding=0)
        #     grayscale = nn.Conv2d(4, 1, kernel_size=1, stride=1, padding=0)
        #     grayscale.weight.data.fill_(1.0 / 3.0)
        #     grayscale.bias.data.zero_()
        #     sobel_filter = nn.Conv2d(1, 2, kernel_size=3, stride=1, padding=1)
        #     sobel_filter.weight.data[0,0].copy_(
        #         torch.FloatTensor([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        #     )
        #     sobel_filter.weight.data[1,0].copy_(
        #         torch.FloatTensor([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        #     )
        #     sobel_filter.bias.data.zero_()
        #     self.sobel = nn.Sequential(grayscale, sobel_filter)
        #     for p in self.sobel.parameters():
        #         p.requires_grad = False
        # else:
        #     self.sobel = None

    def forward(self, x):
        # if self.sobel:
        #     x = self.sobel(x)
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        if self.cluster_layer:
            x = self.cluster_layer(x)
        elif self.category_layer:
            x = self.category_layer(x)
        return x

    def cluster_layer_forward(self, x):
        if self.cluster_layer:
            x = self.cluster_layer(x)
        return x

    def category_layer_forward(self, x):
        if self.category_layer:
            x = self.category_layer(x)
        return x

    def _initialize_weights(self):
        for y,m in enumerate(self.modules()):
            if isinstance(m, nn.Conv2d):
                #print(y)
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                for i in range(m.out_channels):
                    m.weight.data[i].normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                m.weight.data.normal_(0, 0.01)
                m.bias.data.zero_()


def make_layers(input_dim, batch_norm):
    layers = []
    in_channels = input_dim
    cfg = [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M']
    for v in cfg:
        if v == 'M':
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        else:
            conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
            if batch_norm:
                layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
            else:
                layers += [conv2d, nn.ReLU(inplace=True)]
            in_channels = v
    return nn.Sequential(*layers)


def vgg16(sobel=False, bn=True, out=1000):
    dim = 2 + int(not sobel)
    model = VGG(make_layers(dim, bn), out, sobel)
    return model

def vgg16_tweak(bn=True, num_cluster=64, num_category=3):
    dim = 4
    model = VGG(make_layers(dim, bn), num_cluster, num_category)
    return model