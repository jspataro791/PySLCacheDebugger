# PySLCacheDebugger
A cache searcher/debugger for the Second Life viewer texture cache. This project is still in initial development with the hopes of soon providing a user interface to browse the cache (thumbnails). This project aims to be an open source replacement to the widely-used SLCacheViewer which was recently broken by a change in the SL viewer source code. 

Note that this program will *only* work for Second Life viewers with the new core cache changes. This has been tested with Firestorm 5.0.11 and Second Life Viewer 5.1.1.512121.

Currently only supports Windows 10 platform.

## Dependencies
* Python 3.6
* [Glymur](https://github.com/quintusdias/glymur) and [OpenJPEG 2.3.0](http://www.openjpeg.org/)
* Scipy
* Numpy
* PyQt5
* PyInstaller
* Inno Setup

## Building

This project is built with PyInstaller and Inno Setup. For a successful build, OpenJPEG 2.3.0 must be installed to C:\Program Files\openjpeg-v2.3.0-windows-x64\. See config\glymur\glymurrc for the path it is expecting.

    $ pyinstaller pyslcachedebugger.spec

Run installer.iss in Inno Setup to create an installer executable.

## Notes

2/13/2018
* It appears that [Pillow](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000) might support JPEG2000 codestreams. If this can be loaded in-memory, then replacing Glymur with Pillow is the obvious choice.

2/10/2018
* Glymur not reading the file from memory is causing serious bottlenecks. It takes several minutes to load a 450MB cache file whereas SLCacheViewer took, maybe, 10 seconds.
* Problem saving files when not running as administrator. 
* Should rewrite in C# for better JPEG2000 support?

2/5/2018
* Need to think about architecture to do asynchronous thumbnail fetch.
* Textures will have to be fully generated on the fly when called for export. Can't fit entire cache in memory!
