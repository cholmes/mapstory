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


Styling Your StoryLayer
=======================
.. _stlying:

When your StoryLayer is uploaded, a style is created for it unless you have
provided one during upload. A style dictates how a StoryLayer will look when
it is displayed either in a map or on it's own. A StoryLayer has a default
style and zero or more optional styles that it can be displayed with. The
default style is how the StoryLayer will be displayed on the info page and
will also be the default when added to a StoryMap. When in a StoryMap, a
StoryLayer may appear multiple times with different styles applied.

One can manage the default style, upload additional styles, or download styles 
for a StoryLayer on the info page under the `Style` tab. If the StoryLayer has
optional styles, they can be previewed here, too.

You must be the owner of a StoryLayer for this functionality to be available.


Editing Styles
--------------

At the moment, MapStory provides some support for editing styles when a 
StoryLayer is part of a StoryMap. Styles in MapStory are stored in an open text 
format known as
`SLD <http://docs.geoserver.org/stable/en/user/styling/sld-introduction.html>`_ .
This means they can be edited by hand or in other tools, such as
`QGIS <http://qgis.org/>`_ .


Publishing Your Work
====================

When first created, a StoryLayer or StoryMap is considered `Private`. This
means that only you can search for or view it. When you are ready, ensure that
you choose the appropriate publishing status. This can be done on the info page
at the bottom of the `Info` tab.

.. tip::
   :class: alert alert-info
   
   If you are changing the status of a StoryMap, any StoryLayers it uses that
   you own will also be changed.

The available options:

.. list-table:: Publishing Status Options
   :header-rows: 1
   
   * - Value
     - Meaning
   * - Private (Only visible to me)
     - Only you can search for and view this.
   * - Linkable (Anyone with a link can view)
     - Will be hidden from search but others can view via the link.
   * - Public (Anyone can search for and view)
     - As implied.
