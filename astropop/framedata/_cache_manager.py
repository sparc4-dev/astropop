# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Managing the cache folder for FrameData memmaping."""

import os
import atexit
import shutil

from astropy.config import get_cache_dir

from ..logger import logger


__all__ = ['CacheManager']


class CacheManager:
    """Manage the cache folder for FrameData memmaping.

    Parameters
    ----------
    cache_folder : str, optional
        The cache folder to use. If None, use the default astropop cache folder.
    delete_on_exit : bool, optional
        If True, delete the cache folder on exit. Default is True.
    """

    def __init__(self, cache_folder=None, delete_on_exit=True):
        if cache_folder is None:
            cache_folder = os.path.join(get_cache_dir(),
                                        'astropop_cache',
                                        os.urandom(8).hex())

        self._cache_folder = os.path.abspath(cache_folder)
        self._files = []
        self._delete_on_exit = delete_on_exit

        # ensure cache folder is created
        os.makedirs(self.path, exist_ok=True)
        logger.debug('Cache folder created: %s', self.path)

        # ensure delete on exit if necessary
        atexit.register(self._cleanup)

    @property
    def path(self):
        """The cache folder path."""
        return str(self._cache_folder)

    @property
    def managed_files(self):
        """List of files in the cache folder."""
        return list(self._files)

    @property
    def listdir(self):
        """List of files in the cache folder."""
        return os.listdir(self.cache_folder)

    def add_file(self, basename):
        """Add a file to this cache folder.

        Parameters
        ----------
        basename : str
            The basename of the file to add to the cache folder.

        Returns
        -------
        str
            The full path to the file in the cache folder.
        """
        if os.path.basename(basename) != basename:
            raise ValueError('basename must be a file name, not a path')

        logger.debug('Adding file to cache: %s', basename)
        self._files.append(basename)
        return os.path.join(self.cache_folder, basename)

    def remove_file(self, basename):
        """Remove a file from this cache folder.

        Parameters
        ----------
        basename : str
            The basename of the file to remove from the cache folder.
        """
        basename = os.path.basename(basename)
        if basename not in self._files:
            raise ValueError('File not in cache folder: %s' % basename)

        logger.debug('Removing file from cache: %s', basename)
        self._files.remove(basename)
        os.remove(os.path.join(self.path, basename))

    def _cleanup(self):
        if self._delete_on_exit:
            for f in self._files:
                self.remove_file(f)
            if len(self.listdir) == 0:
                logger.info('Removing cache folder: %s', self.path)
                shutil.rmtree(self.path)
                return
            logger.warning('Cache folder not empty: %s', self.path)
        logger.info('Cache folder not removed: %s', self.path)

    def __del__(self):
        self._cleanup()

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f'<CacheManager: {self.path}>'
