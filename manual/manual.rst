===============
MapStory Manual
===============

.. contents::


Getting Started
===============

Registration
------------

Create a MapStory in 5 Minutes
------------------------------

Uploading Your StoryLayers
==========================
.. _uploads:

To get started with building your own stories, you must first upload some data,
referred to as StoryLayers in MapStory. A StoryLayer might stand on it's own
or be used as part of a StoryMap containing multiple StoryLayers.

Before uploading your StoryLayers, please read this section to understand the
currently supported data formats and tips that will make this process easier.

Structuring Your Data To Support Time
-------------------------------------

Specifying the temporal extent of a spatial feature.

* start date
* optional end date

Specifying the nature of the temporal aspect of your data.

* inteveral data
* list data

.. include:: time.rst

Supported Files
---------------
.. _upload-support:

CSV Files
.........
.. _upload-csv:

CSV files containing a latitude and longitude column are supported. 

Zipping Your Data
.................
.. _upload-zip:

To make your data upload faster, consider creating a zip file of your data.
This can often reduce the size of your upload by 5-10 times. Ensure that the
zip file does not contain any additional directory structures or uneeded files.
Only a single StoryLayer may be uploaded at a time using a zip file.

Due to the nature of a zip file, the upload must complete before feedback can
be given on the presence of all files, so if unsure, you can drag the files you
think you might use into the upload form for immediate feedback. When things
look proper, proceed with the upload using the zip.

Other Tips
..........
.. _upload-tips:

* While MapStory supports many projections, to ensure it is recognized, consider
  using EPSG:4326 or (@todo other terminology - WGS84?). Convert your data
  before uploading using your favorite tool(link).
* If your data is on a global level, consider simplifying the geometries to
  reduce the upload size and make your StoryLayer faster during playback.
* Know your data - if there are attributes that you don't understand or are a
  remnant from some processing algorithm, remove them as they take up space and
  don't contribute to understanding the story.
