# PySLCacheDebugger
A cache searcher/debugger for the Second Life viewer texture cache. This project is still in initial development with the hopes of soon providing a user interface to browse the cache (thumbnails). This project aims to be an open source replacement to the widely-used SLCacheViewer which was recently broken by a change in the SL viewer source code.

## Dependencies
* Python 3.6
* [Glymur](https://github.com/quintusdias/glymur) and [OpenJPEG](http://www.openjpeg.org/)
* Scipy
* Numpy
* PyQt5
* PyInstaller
* Inno Setup

## Notes

2/10/2018
* Glymur not reading the file from memory is causing serious bottlenecks. It takes several minutes to load a 450MB cache file whereas SLCacheViewer took, maybe, 10 seconds.

2/5/2018
* Need to think about architecture to do asynchronous thumbnail fetch.
* Textures will have to be fully generated on the fly when called for export. Can't fit entire cache in memory!