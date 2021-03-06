import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

class DataPipeline(object):
    def __init__(self, 
                 image_path, 
                 training_params):
        try:
            with np.load(image_path) as data:
                images = data['imgs']
                labels = data['labels']
        except:
            data = np.load(image_path)
            images = data['imgs']
            labels = data['labels']

        print(images.shape)
        images = np.expand_dims(images, axis=-1)

        # tf.cast() ???
        images = images.astype(np.float32)
        # complete shuffle
        idx = np.arange(images.shape[0])
        
        print('begin: complete shuffling...')
        np.random.shuffle(idx)
        images = images[idx]
        labels = labels[idx]

        load = int(training_params['load'])
        print('number of images to be loaded: {}'.format(load))
        
        self.images = images[0:load]
        self.labels = labels[0:load]
        print(self.images.shape, self.labels.shape)
        print('end: complete shuffling...')
        
        self.batch_size = training_params['batch_size']

        with tf.name_scope('pipeline'):
            self._build_dataset()

        # params.json must contain either iterations or epochs
        try:
            self.n_run = int(training_params['iterations'])
        except KeyError:
            self.n_run = int(training_params['epochs']) * (self.images.shape[0] // self.batch_size)

    def _build_dataset(self):
        self.images_ph = tf.placeholder(self.images.dtype, self.images.shape)
        self.labels_ph = tf.placeholder(self.labels.dtype, self.labels.shape)
        dataset = tf.data.Dataset.from_tensor_slices((self.images_ph, self.labels_ph))
        dataset = dataset.shuffle(self.images.shape[0] // 100)
        dataset = dataset.batch(batch_size=self.batch_size)
        dataset = dataset.prefetch(buffer_size=1)
        iterator = dataset.make_initializable_iterator()
        self.initializer = iterator.initializer
        self.next_images, self.next_labels = iterator.get_next()