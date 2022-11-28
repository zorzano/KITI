class KGIoTDriver(object):

    def close(self):
        # Empty method, to be fulfiiled by inheritors
        raise NotImplementedError()

    def write(self, name):
        # Empty method, to be fulfiiled by inheritors
        raise NotImplementedError()
