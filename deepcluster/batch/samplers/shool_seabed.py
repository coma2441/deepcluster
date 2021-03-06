import numpy as np

from batch.samplers.shool import Shool


class ShoolSeabed(Shool):
    def __init__(self, echograms, window_size, max_dist_to_seabed, fish_type):
        super(ShoolSeabed, self).__init__(echograms=echograms, window_size=window_size, fish_type=fish_type)

        #Get shools:
        # self.seabed_shools = super(self).seabed_shools

        #Remove shools that are not close to seabed
        self.close_shools = \
            [(e, o) for e, o in self.seabed_shools if
             np.abs(e.get_seabed()[int((o['bounding_box'][2] + o['bounding_box'][3]) / 2)] - o['bounding_box'][1]) <
             max_dist_to_seabed]

    def get_sample(self):
        """

        :return: [(int) y-coordinate, (int) x-coordinate], (Echogram) selected echogram
        """
        #Random object

        oi = np.random.randint(len(self.close_shools))
        e,o  = self.close_shools[oi]

        #Random pixel in object
        pi = np.random.randint(o['n_pixels'])
        y,x = o['indexes'][pi,:]

        #Todo: Call get_sample again if window does not contain seabed

        return [y,x], e


    def get_all_samples(self):
        """
        :return: [(int) y-coordinate, (int) x-coordinate], (Echogram) selected echogram
        """
        center_locations = []
        echograms = []
        #Random object
        for i, (e, o) in enumerate(self.close_shools):
        #Random pixel in object
            pi = np.random.randint(o['n_pixels'])
            y,x = o['indexes'][pi, :]
            # Correct x if window is not inside echogram
            if (x < self.window_size[1]//2):
                x = self.window_size[1]//2
            elif (x > e.shape[1] - self.window_size[1]//2):
                x = e.shape[1] - self.window_size[1]//2
            center_locations.append([y, x])
            echograms.append(e)
        return center_locations, echograms
