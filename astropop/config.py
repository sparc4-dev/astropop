# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Global configuration parameters for astropop."""


class AstropopConfig:
    """Global configuration parameters for astropop.

    Attributes
    ----------
    FRAMEDATA_DISABLE_UNCERTAINTY : bool
        If True, all FrameData uncertainty set will be disabled completely,
        reducing memory usage.
        Default is False.
    FRAMEDATA_DISABLE_FLAGS : bool
        If True, all FrameData flags and masks set will be disabled completely
        reducing memory usage.
    IMARITH_SKIP_UNCERTAINTY : bool
        If true, any imarith or imcombine operation will skip the uncertainty
        propagation. This will increase the speed of the operation and reduce
        the memory usage, but will not propagate the uncertainties.
        Default is False.
    """
    IMARITH_SKIP_UNCERTAINTY = False
    FRAMEDATA_DISABLE_UNCERTAINTY = False
    FRAMEDATA_DISABLE_FLAGS = False
