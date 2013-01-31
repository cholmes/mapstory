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
or be used as part of a MapStory containing multiple StoryLayers.

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
.. _styling:

When your StoryLayer is uploaded, a style is created for it unless you have
provided one during upload. A style dictates how a StoryLayer will look when
it is displayed either in a map or on it's own. A StoryLayer has a default
style and zero or more optional styles that it can be displayed with. The
default style is how the StoryLayer will be displayed on the info page and
will also be the default when added to a MapStory. When in a MapStory, a
StoryLayer may appear multiple times with different styles applied.

One can manage the default style, upload additional styles, or download styles 
for a StoryLayer on the info page under the `Style` tab. If the StoryLayer has
optional styles, they can be previewed here, too.

To update an existing style, ensure this option is selected and the name matches
and existing style.

If a name is not provided, an attempt will be made to extract a name from the
SLD using the first `Name` underneath a `NamedLayer`. If this cannot be found,
a name must be provided explicitly.

You must be the owner of a StoryLayer for all style functionality to be available.


Editing Styles
--------------

At the moment, MapStory provides some support for editing styles when a 
StoryLayer is part of a MapStory. Styles in MapStory are stored in an open text
format known as
`SLD <http://docs.geoserver.org/stable/en/user/styling/sld-introduction.html>`_ .
This means they can be edited by hand or in other tools, such as
`QGIS <http://qgis.org/>`_ .

.. tip::
   :class: alert alert-info

   For adventurous users, editing the SLD by hand may be desirable. To get a
   template, (or just to see if you're adventurous enough), download an existing
   SLD and take a look at it.


Publishing Your Work
====================

When first created, a StoryLayer or MapStory is considered `Private`. This
means that only you can search for or view it. When you are ready, ensure that
you choose the appropriate publishing status. This can be done on the info page
at the bottom of the `Info` tab.

.. tip::
   :class: alert alert-info
   
   If you are changing the status of a MapStory, any StoryLayers it uses that
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

Using media in annotations
==========================

The following types of media can be embedded in an annotation popup in the description field:

* YouTube
* Flickr
* An arbitrary hyperlink

To embed a YouTube video, use the following syntax:

    [youtube=http://www.youtube.com/watch?v=O_s3EryiL7M]

If you want to influence the width and or height of the video iframe, add a w and/or h url parameter, e.g.:

    [youtube=http://www.youtube.com/watch?v=O_s3EryiL7M&w=350] 

but in keep in mind that the popups have a maximum width of 500 pixels.

You can combine the YouTube video with any HTML in front or after the YouTube declaration.

For Flickr use the Share button in the Flickr interface and then press the Grab HTML/BBCode hyperlink.
Copy/paste the HTML, but make sure to change the target to _blank on the anchor:

    <a target="_blank" href="http://www.flickr.com/photos/jetbluestone/8128332626/" title="48.. by jetbluestone, on Flickr"><img src="http://farm9.staticflickr.com/8472/8128332626_b231b833db.jpg" width="371" height="500" alt="48.."></a>

To embed any arbitrary hyperlink in the annotation popup, just use plain old HTML, for example:

    <a target="_blank" href="http://myurl" title="myhyperlink">click here to go to my url</a>

