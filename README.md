# PySLCacheDebugger
A cache searcher/debugger for the Second Life viewer texture cache. This project is still in initial development with the hopes of soon providing a user interface to browse the cache (thumbnails).

## Dependencies
* Python 3.6
* [Glymur](https://github.com/quintusdias/glymur) and [OpenJPEG](http://www.openjpeg.org/)
* Scipy
* Numpy

## Notes

2/5/2018
* Need to think about architecture to do asynchronous thumbnail fetch.
* Textures will have to be fully generated on the fly when called for export. Can't fit entire cache in memory!