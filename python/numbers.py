""" Numbers...
    Quick aggregation based on regex of variable names.

    Use case:

    # for i in range(10): # typical loop
    with Aggregate("counts_*ref"):
        counts_ref = 2  # not defined prior
        counts_dark_ref = [2,3]  # any object

    print(counts_ref)  # [2]

    print(counts_dark_ref)  # [[2,3]]
    print(counts_dark_ref.mean())
    print(counts_dark_ref.ucert())
    print(counts_dark_ref.std())


    Implementation:

    - Intercept assignment calls
    - Check if variable name matches regex
    - Property for dynamic behaviour?
    - Need variables to be instances, possible to do:

      class A(): pass # ...
      # in Aggregate interception
      a = A()
      a = 2
      print(type(a) is A) # True

      Turns out, no: https://stackoverflow.com/questions/11024646/is-it-possible-to-overload-python-assignment
      Can treat modules as a class and bar assignments from there via __setattr__.
      Alternatively, possible to introspect and use bytecode?

    Ended up doing:
    >>>>>>>>>>>>> ORIGINAL >>>>>>>>>>>>>>>
    for i in range(10):
        counts = i
    --------------------------------------
    collect = Collection()
    for i in range(10):
        collect.counts = 1
    <<<<<<<<<<<<< MODIFIED <<<<<<<<<<<<<<<
    """

class Collector:
    """ Generic collection class """
    def __init__(self):
        self._values = []  # container

    @staticmethod
    def of(data: object):
        # Check if can subclass into NumberCollector
        try:
            assert not isinstance(data, str)  # avoids 'float("2.0")'
            float(data)  # duck typing
        except (AssertionError, ValueError, TypeError):
            return Collector()
        else:
            return NumberCollector()

    def append(self, value):
        self._values.append(value)

    def __iter__(self):
        for value in self._values:
            yield value

    def __repr__(self):
        return repr(self._values)

class NumberCollector(Collector):
    """ Using Welford's online algorithm
    Source: https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
    Source: https://stackoverflow.com/a/1348615
            Use of sample variance, as dividing by counts fails to account
            variance between sample mean and true mean.
    """

    def __init__(self):
        self._count = 0
        self._mean = 0
        self._meansq = 0

    def append(self, value):
        self._count += 1
        delta = value - self._mean
        self._mean += delta / self._count
        deltasq = value - self._mean
        self._meansq += delta * deltasq

    @staticmethod
    def _get_sf_dp(value, sf=2):
        """ Returns number of decimal places for rounding to 'sf' significant figures.
        Source: https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python/56974893
        """
        import math
        if value == 0 or not math.isfinite(value):
            return None # unbounded precision
        return sf - math.ceil(math.log10(abs(value)))

    @property
    def count(self):
        return self._count

    @property
    def mean(self):
        return self._mean

    @property
    def stddev(self):
        if self._count < 2:
            return 0
        return (self._meansq / (self._count - 1))**0.5
    
    def to_ufloat(self):
        import uncertainties
        return uncertainties.ufloat(self.mean, self.stddev)

    def __iter__(self):
        # Can remove via metaclass as well
        raise TypeError("'NumberCollector' object is not iterable")

    def __repr__(self):
        mean, stddev = self.mean, self.stddev
        dp = NumberCollector._get_sf_dp(stddev, 2)
        if dp is None:
            return "{} +/- {} ({:d})".format(mean, stddev, self.count)

        mean, stddev = round(mean, dp), round(stddev, dp)
        precision = max(dp, 0)  # ignore negative precisions during print
        return "{:.{precision}f} +/- {:.{precision}f} ({:d})".format(
            mean, stddev, self.count, precision=precision)

class Collection:

    RESET = "_SPECIAL_RESET_KEY"

    def __setattr__(self, name, value):
        # Delete attribute if special key 'RESET' or 'self' supplied
        if value is Collection.RESET or value is self:
            if hasattr(self, name):
                super().__delattr__(name)
            return

        # Create a Collector if not existing, and add new value
        if not hasattr(self, name):
            super().__setattr__(name, Collector.of(value))
        getattr(self, name).append(value)

# Collector
c = Collector()
c.append(1)
c.append(2)
print(c) # [1, 2]

for val in c:
    print(val) # prints 1, then 2

# NumberCollector
nc = NumberCollector()
nc.append(1)
nc.append(2)
print(nc) # 1.50 +/- 0.71 (2)

# for val in nc:
#     print(val)

# Test
collect = Collection()
counts = []
for i in [4,7,13,16]:
    _i = i + 1e10
    collect.counts = _i
    counts.append(_i)
print(collect.counts) # 10000000010.0 +/- 5.5 (4)
print(collect.counts.stddev**2) # 30

# Verify
import numpy as np
print(np.std(counts, ddof=1)**2) # 30
