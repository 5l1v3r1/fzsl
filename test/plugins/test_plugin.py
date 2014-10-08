import fzsl

class UnsuitableScanner(fzsl.Scanner):
    def __init__(self):
        super(UnsuitableScanner, self).__init__('unsuitable')

    def is_suitable(self, path):
        return False

    def scan(self, path, rescan=False):
        return []

class ABCScanner(fzsl.Scanner):
    def __init__(self):
        super(ABCScanner, self).__init__('abc')

    def is_suitable(self, path):
        return True

    def scan(self, path, rescan=False):
        return ['a', 'b', 'c']

class KwdsScanner(fzsl.Scanner):
    def __init__(self, arg1, arg2, arg3):
        super(KwdsScanner, self).__init__('kwds')
        self._args = [arg1, arg2, arg3]

    def is_suitable(self, path):
        return True

    def scan(self, path, rescan=False):
        return self._args

class BrokenScanner1(fzsl.Scanner):
    def __init__(self):
        super(BrokenScanner1, self).__init__('broken1')

    def scan(self, path, rescan=False):
        return []

class BrokenScanner2(fzsl.Scanner):
    def __init__(self):
        super(BrokenScanner2, self).__init__('broken2')

    def is_suitable(self, path):
        return True

class BrokenScanner3(fzsl.Scanner):
    def __init__(self):
        super(BrokenScanner3, self).__init__('broken3')

    def is_suitable(self, path):
        return True

    def scan(self, path):
        return []

