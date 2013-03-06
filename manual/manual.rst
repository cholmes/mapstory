===============
MapStory Manual
===============

.. contents::


.. _intro:

Introduction
============

**MapStory** is a collaborative map sharing and publishing platform with a focus on storytelling. Maps are shown with an element of time to create animations to aid in the storytelling.

A **MapStory** is also the name for those temporal maps. A MapStory can also include one or more StoryLayers, other geospatial layers, and annotations.

A **StoryLayer** is a component of a MapStory that contains geospatial data with an element of time. Like a standard geospatial layer, but containing a timestamp as one of its attributes.

A **StoryTeller** is an author of a MapStory. Anyone who registers for an account on MapStory.org can be a StoryTeller. (See the Registration_ section for more details.)

For more information, please see the `MapStory wiki <http://wiki.mapstory.org>`_.


.. _registration:

Registration
============

You can interact with existing MapStories and StoryLayers without needing to register. Simply click the **Search MapStory** link and select either **Search MapStories**, **Search StoryLayers**, or **Search StoryTellers**.

Before you can create a MapStory, you will need to register for an account:

* To register for an account, navigate to `MapStory.org <http://mapstory.org>`_ and click on **Register** in the top right of the screen.
* You will be asked to enter a user name and password (twice for confirmation) as well as an email address. All fields are required. Note that the user name must consist of only letters, numbers, and underscores.
* Click **Signup** when finished.
* A confirmation email will be sent to you which will contain a URL. Navigate to that URL to confirm your registration.

You are now ready to create your own MapStories.


.. _5minmap:

Create a MapStory in 5 minutes
==============================

A MapStory consists of one of more StoryLayers. The quickest way to create a MapStory is to use an existing StoryLayer as source material.

* Click the **Search MapStory** link at the top and select **Search StoryLayers**. (You can also type in a keyword in the **Quick Search** box to find a StoryLayer.)

* Find a suitable StoryLayer in the list. You can narrow down the search using the category links on the left.

* Click **Create a Story using this StoryLayer**.

* The next page is the MapStory authoring interface. Here you can add other layers, change the base layer, alter styling, and even edit the features.

* When you're finished, click the **Save Map** button. A dialog box will display where you can enter a **Title** and **Abstract** for your new MapStory. When finished, click **Save**.

You've now created your first MapStory. The next step is to tell your own story using your own data.


.. _prep:

Preparing your data to become a StoryLayer
==========================================

To get started with telling your own MapStories, the first step is to upload some data to be a StoryLayer. A StoryLayer can be viewed on its own, but most often it is a component of one or more MapStories.

This section will help you understand the currently supported data formats, as well as show tips that will make the upload process easier.

.. _prep.time:

Structuring your data to support time
-------------------------------------

A central aspect of a StoryLayer is that it contains a **time** component, that is, it contains information about the given data over a period of time. To this end, the data must contain a timestamp in one or more of its attributes.

If two timestamp attributes exist, it is possible to set features to occur over a time range (with one attribute denoting the start and the other denoting the end). If a single timestamp exists, then the feature will be set to occur at that given instant only.

.. _prep.time.attribute:

Selecting an attribute
~~~~~~~~~~~~~~~~~~~~~~

The attribute that will be selected to offer the time component for the StoryLayer can be in any of the following formats:

* A timestamp
* An integer representing a year
* A string (text) that can be interpreted as a timestamp

This attribute is selected during the StoryLayer upload process. (See the section on Uploading_.)

.. _prep.time.formats:

Time formats
~~~~~~~~~~~~

If the attribute in question is a string that can be interpreted as a timestamp, you will need to tell MapStory how the string should be interpreted. If specifying the time format, you can use the following formatting flags:

* ``y``—year
* ``M``—month
* ``d``—day of month
* ``H``—hour of day (0-23)
* ``k``—hour of day (1-24)
* ``m``—minute in hour
* ``s``—second in minute

Some things to keep in mind:

* Single quotes represent a literal character not to be interpreted.
* Repeat a formatting flag to represent the maximum number of digits, such as ``yyyy``
* If a timestamp doesn't have a year component, it will be assumed to be 1970. There is no way to set a constant for the year.

You can also tell MapStory to use its "best guess" algorithm to try to automatically determine the data format. This will work when the date is in one of variants of the ISO 8601 time format, such as any of the following:

* ``yyyy-MM-dd'T'HH:mm:ss.SSS'Z'``
* ``yyyy-MM-dd'T'HH:mm:sss'Z'``
* ``yyyy-MM-dd'T'HH:mm:ss'Z'``
* ``yyyy-MM-dd'T'HH:mm'Z'``
* ``yyyy-MM-dd'T'HH'Z'``
* ``yyyy-MM-dd``
* ``yyyy-MM``
* ``yyyy``

Some common custom examples follow. If the timestamp looks like the string on the left, use the format on the right:

* Jun 2012—``MMM-y``
* May/15/2012—``MMM/d/yyyy``
* 11/1/2012—``M/d/y``

.. _prep.time.period:

Relevant time periods
~~~~~~~~~~~~~~~~~~~~~

A feature can currently support either one or two timestamp attributes. If a single attribute is used, this is interpreted by MapStory to mean that the feature is displayed at a single point in time. If two attributes are used, the attributes represent the beginning and ending of the period in which the feature in considered displayed. The decision on whether to utilize an end timestamp is specific to your data and story.

.. _prep.filetypes:

Supported Files
---------------

MapStory can load the following file types:

* CSV (comma-separated value)—These non-spatial files can be loaded when they contain columns with latitude and longitude values.
* Shapefile—MapStory can read any standard shapefile, including an optional PRJ (projection file).

.. _prep.filetypes.archive:

Archive
~~~~~~~

To reduce the size of the data being uploaded to MapStory and so making the upload faster, consider creating an archive (zip file) of your data. This can increase upload speeds by many times, depending of the type of data being uploaded. If creating an archive, ensure that the archive does not contain any directory structures or extraneous files. 

Only a single StoryLayer may be uploaded at a time using an archive. Also note that the name of the resulting StoryLayer will be taken from the file name of the shapefile, not the file name of the archive.

.. _prep.filetypes.tips:

Other Tips
~~~~~~~~~~

Here are some other tips that may prove useful when preparing your data for upload:

* While MapStory supports many projections, consider using WGS84 (EPSG:4326) to ensure it is recognized.
* If your data is on a global level or is very detailed, consider simplifying the geometries to reduce the upload size and make your StoryLayer faster to render during playback.
* Similar to simplifying the geometries, if there are attributes that aren't necessary to understanding the MapStory, consider removing them to save processing time.


.. _uploading:

Uploading your data
===================

Once your data is prepared, it is ready to be uploaded. From the **Upload StoryLayer** form, you can either drag and drop files or use the **Browse...** button to select the file(s).

When uploading a shapefile that hasn't been made into an archive, first select the file with the ``.shp`` extension. When the file has been selected, the form will expand to include places to select the other files associated with that shapefile, including the ``.shx``, ``.dbf``, and optional ``.prj`` files.

Separately to the data, you can also upload a Styled Layer Descriptor (SLD) file for use in styling the StoryLayer. This style will automatically be associated with this layer upon upload.

If uploading an archive, be aware that the upload will need to finish before the contents of the archive can be checked for integrity. If you would like immediate feedback on whether the data is in the correct format, you can select the files individually in the form.


.. _styling:

Styling your StoryLayer
=======================

A style dictates how a StoryLayer will look when it is displayed. When your StoryLayer is uploaded, a default style will be created for it unless a style file was provided during the upload. If a style file was provided, that style will be associated with the newly uploaded layer. A StoryLayer has a default style and any number of optional styles that can be displayed in addition. The default style is how the StoryLayer will be displayed on the `Info tab`_ and will also be the default when added to a MapStory. When contained in a MapStory, a StoryLayer may appear multiple times with different styles applied.

One can manage the default style, upload additional styles, or download styles for a StoryLayer on the `Style tab`_. If the StoryLayer has optional styles, they can be previewed here, too.

To update an existing style, ensure that the **Update existing style** option is selected and that the name matches an existing style.

If a name is not provided, an attempt will be made to extract a name from the SLD. If a proper name cannot be found, a name must be provided explicitly.

You must be the owner of a StoryLayer for all style functionality to be available.

Editing styles
--------------

MapStory provides some limited support for editing styles when a StoryLayer is part of a MapStory. Styles are stored in an open text format known as Styled Layer Descriptor (SLD). An SLD can be edited in a simple text editor or in any program that supports editing of SLD files, such as `QGIS <http://qgis.org>`_ or `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`_.


.. _publishing:

Publishing your content
=======================

When first created, a StoryLayer or MapStory is set to be Private. This means that only you can search for or view it. To change the status, navigate to the **Publishing Status** section on the `Info tab`_. The available options are: **Only visible to me** (default), **Anyone with the link can view**, and **Anyone can search for and view**.

If you are changing the status of a MapStory, any StoryLayers that comprise that MapStory will also have their status changed.


.. _storylayer:

StoryLayer page
===============

The StoryLayer page contains a map window where the StoryLayer can be viewed, as well as information about the StoryLayer.

When viewing a StoryLayer, there are a number of tabs that correspond to various functionality associate with that layer. The tabs available are **Info**, **Style**, **Share**, **Flag**, **Add**, and **Download**.

In addition to the tabs, there is a StoryLayer rating option. Click on the stars to rate the layer between one and five stars.

At the very bottom of the page is a place where you can add comments to the page. Simply type in some text in the comment field and click **Submit** to contribute to the conversation.

.. _storylayer.map:

StoryLayer map window
---------------------

The Map window is the centerpiece of the StoryLayer page. The map window contains a view of the data with an optional base layer. This map window can be zoomed and panned as desired, but by default it will zoom to the maximum extent of the layer across the entire time frame.

The map window contains a few controls at the bottom. The controls are, from left to right:

* **Play/Pause**—Controls the starting and stopping of the map animation
* **Timeline**—Displays and controls the current map time instance
* **Loop**—When enabled, the animation will continue from the beginning after it has completed
* **2x Playback**—When enabled, will double the speed of the playback
* **Reverse one frame**—Will skip backward to the previous time instance
* **Advance one frame**—Will skip forward to the next time instance
* **Show map legend**—Will toggle the map legend, where the base map can also be toggled
* **Data and time options**—Allows you to specify start and end timestamp range and animation options
* **Full screen**—Will toggle viewing the map over the entire screen area

.. _storylayer.infotab:

Info tab
--------

The Info tab, which is the default tab when viewing a StoryLayer, contains fields for metadata. From this tab, you can enter a proper layer **Title** (distinct from the internal layer name), **Keywords**, **Abstract** (description), the **Purpose of this StoryLayer**, the intended **Language**, any **Supplemental Information** about the layer, and a **Data Quality Statement**. This information will be available to anyone who views this StoryLayer.

In addition to the metadata, you can also associate this StoryLayer with a range of preexisting topics, from **Culture & Ideas** to **GeoPolitics**.

You can set a thumbnail for this layer by adjusting the map window to a desired location and then by clicking the **Set thumbnail** button.

You change the visibility of the layer by clicking the **Change Status** button. There are three options: **Only visible to me** (default), **Anyone with the link can view**, and **Anyone can search for and view**.

.. _storylayer.styletab:

Style tab
---------

The Style tab allows you to select from existing styles associated with the StoryLayer or upload a new style. Styles can't be directly edited on this tab; to edit a style, you must create a MapStory and load this StoryLayer.

.. _storylayer.sharetab:

Share tab
---------

The Share tab has buttons to allow this StoryLayer to be shared on popular social networking sites.

.. _storylayer.flagtab:

Flag tab
--------

The Flag tab allows you to insert a comment stating whether a given StoryLayer appears to be inappropriate, broken, or otherwise problematic.

.. _storylayer.addtab:

Add tab
-------

The Add tab allows you to add the StoryLayer to your list of Favorites, as well as to associate this StoryLayer with a MapStory that is in progress.

.. _storylayer.downloadtab:

Download tab
------------

The download tab allows you to download the data that comprises the StoryLayer, as well as any associated styles. The formats available for download are:

* Zipped shapefile
* GML (2.0, 3.1.1)
* CSV
* Excel
* GeoJSON
* JPEG
* PDF
* PNG
* KML (full download or live viewing in Google Earth)


.. _mapstoryviewer:

MapStory fullscreen viewer
==========================

There are two ways to view a MapStory:

* Through the standard viewing page, much like the StoryLayer page
* In a full screen viewer

You can get to the MapStory fullscreen viewer in multiple ways:

* Search for a given MapStory and selecting it
* Click **View this StoryLayer in fullscreen** on a StoryLayer page
* Click **Create New MapStory** from the homepage

This section will describe the MapStory fullscreen viewer interface.

.. _mapstoryviewer.top:

Top of viewer
-------------

The header of the page shows the title of the MapStory. There is also a **View info** link that will take you back to the standard MapStory viewer page. Clicking the **Maps** link will take you to the **Search MapStories** page.

.. _mapstoryviewer.toolbar:

Toolbar
-------

The toolbar runs across the top of the screen just below the header, and contains a few different actions relevant to manipulation of the MapStory.

* **Map Properties**—Displays a dialog with three additional options: **Number of zoom levels**, **Wrap dateline (Yes/No)**, and **Background color**.
* **Save Map**—Saves changes made to the map. If the map is new, a new map will be saved and given a unique numerical identifier on the page, accessible by the following URL: ``http://mapstory.org/maps/####/view``, where ``####`` is the numerical identifier of the MapStory. This number is generated by MapStory and cannot be changed.
* **Publish Map**—Displays a pop-up window containing HTML code for embedding the map in a web page
* **Zoom in**—Increases the current zoom level by one
* **Zoom in/out**—Decreases the current zoom level by one
* **Zoom to previous extent**—Returns to the previous map extent
* **Zoom to next extent**—Returns to the next map extent (activated only after using **Zoom to previous extent**)
* **Zoom to max extent**—Zooms to the maximum extent of all layers
* **Get Feature Info**—When activated, displays a pop-up containing attribute information for all the features on a given clicked point on the map
* **Notes**—A menu containing three options:

  * **Show notes**—Toggles whether existing notes are displayed
  * **Add note**—Creates a new note (annotation) on the map. A note consists of a title, description, and timestamps (start and optional end), as well as an optional geometry showing the area of interest.
  * **Edit note**—Edits an existing note

* **Create a new feature**—Creates a new feature in the selected layer. The new feature must be drawn and attribute values populated manually.
* **Edit existing feature**—Edits an existing feature in the selected layer. Either the geometry or attribute values can be edited.

.. _mapstoryviewer.layers:

Layers panel
------------

The layers panel contains information related to the layers associated with the MapStory. This can include StoryLayers as well as base layers, such as OpenStreetMap.

The Layers panel has its own toolbar:

* **Add layers**—Displays the Available Layers panel for adding new layers to the MapStory
* **Remove layer**—Removes the currently selected layer from the list
* **Layer Properties**—Displays the Layer Properties panel for viewing and editing the properties of the selected layer (layer name and description, display settings, and layer styles). For attribute information, use the **Get Feature Info** tool in the main toolbar.
* **Layer Styles**—Displays the Layer Styles panel for editing layer styling rules

Below the Layers toolbar is the layers list. The layers list consists of two sections: **Overlays** and **Base Maps**. Overlays can be Storylayers or any layer from a remote Web Map Server. **Base Maps** consist of hosted web service layers such as OpenStreetMap. Any number of Overlays can be active at any one time, while only a single Base Map can be visible.

.. _mapstoryviewer.map:

MapStory map window
-------------------

The majority of the fullscreen viewer is the map window. This is where the MapStory animation itself is displayed. At the bottom of the window is the animation control, which is identical to that found in the `StoryLayer map window`_.

.. _annotations:

Using media in annotations
==========================

The following types of media can be embedded in an annotation pop-up in the description field:

* A URL
* YouTube video
* Flickr photo

To embed a YouTube video, use the following syntax::

    [youtube=http://www.youtube.com/watch?v=O_s3EryiL7M]

If you want to influence the width and or height of the video, add a ``w`` and/or ``h`` URL parameter::

    [youtube=http://www.youtube.com/watch?v=O_s3EryiL7M&w=350]

Pop-ups have a maximum width of 500 pixels.

You can combine the YouTube video with any HTML in front or after the YouTube declaration.

For Flickr, use the **Share** button in the Flickr interface and then press the **Grab HTML/BBCode** hyperlink. Copy/paste the HTML, but make sure to change the target to ``_blank`` on the anchor::

    <a href="http://www.flickr.com/photos/jetbluestone/8128332626/" title="48.. by jetbluestone, on Flickr" target="_blank">
      <img src="http://farm9.staticflickr.com/8472/8128332626_b231b833db.jpg" width="371" height="500" alt="48..">
    </a>

To embed any arbitrary URL in the annotation pop-up, just enter it as is::

    <a target="_blank" href="http://example.com" title="Example URL">Click here to go to this example URL</a>


.. _tutorial:

Tutorial 
========

This example will create a MapStory based on a single uploaded StoryLayer, with annotations added.

.. _tutorial.acquire:

Step 0: Acquire data
--------------------

This example will use a single layer prepared for upload, consisting of the locations of `Hurricane Sandy <http://en.wikipedia.org/wiki/Hurricane_Sandy>`_ over the course of its lifespan. It is in shapefile format, and it was taken from `NOAA <http://noaa.gov>`_ as part of their `freely available GIS data <http://www.nhc.noaa.gov/gis/>`_.

To get this data, navigate to http://www.nhc.noaa.gov/gis/, find the area titled "Preliminary Best Track Information", select 2012 in the the select box, and then click the link for Hurricane Sandy.

Separately, there is an SLD (style) file that has been prepared using a third-party utility. This will be uploaded along with the data.

.. _tutorial.prepare:

Step 1: Prepare data
--------------------

The shapefile attribute that contains the timestamp is called ``DTG``, and its values are of the form ``yyyyMMddHH``.

Investigating the data shows that it has a type of Integer. In order to be able to manually map this custom date string to a standard timestamp, the attribute needs to be of type String (text).

This data preparation can be done via third-party utilities such as `QGIS <http://qgis.org>`_ or `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`_. The instructions below will create a copy of the contents of the ``DTG`` attribute in a new attribute called ``DTGSTRING``, which will be of type String.

In QGIS:

* Open the file **Add Vector Layer...**.

* Right-click on the layer in the **Layers** list and select **Open attribute table**.

* Click **Toggle Editing Mode**.

* Click **Field Calculator**.

* Fill out the form. Check the **Create new field** box, enter an **Output field name** of ``DTGSTRING``, and select **Output field type** as **Text (String)**. In the **Expression** field, enter **tostring(DTG)**, and click **OK**.

* Click the **Save Edits** button.

* After the edits are made, create an archive (ZIP file) of the edited files.

.. _tutorial.upload:

Step 2: Upload data
-------------------

* Log in to your MapStory account and then return to the main MapStory page.

* Click **Upload StoryLayers**.

* Drag and drop the archive onto the box titled **Drag and Drop Files Here**. Alternately, click the **Browse...** button next to the Data field, and select the file for upload.

* Since we have an SLD already created and ready to be associated with this layer, we can also drag and drop the file in the same way. Alternately, click the **Browse...** button next to the SLD field, and select the file for upload.

* When finished, click **Upload**.

.. _tutorial.crs:

Step 3: Specify coordinate reference system
-------------------------------------------

In most cases, MapStory will be able to determine the intended coordinate reference system to be used in your data. In this case, the PRJ file which includes the CRS definition was included, but MapStory is unable to parse it. In such a case, MapStory will ask you to input the intended CRS.

In this case, the data is in standard WGS84 geographic coordinates, so when it asks for the EPSG code, enter **EPSG:4326**. Then click **Submit**.

.. _tutorial.time:

Step 4: Associate time attribute
--------------------------------

Once the upload has successfully completed, the next page will allow you to associate a particular attribute with the time aspect of the StoryLayer.

* When asked "Does this data have date/time attributes?", click **Yes**.

* The data was taken at varying intervals, so when asked "Was the data collected at regular intervals?", click **No**. 
* Next, set the **Start Date/Time**. There are two supported Types, **Text** and **Year Number**. When selecting Text, you will have the opportunity to interpret the text field of a particular attribute as a timestamp. When selecting Year Number, the integer in the attribute will be interpreted literally. In our case, select the **Text** option. In the **Attribute** field, select **DTGSTRING**. In the **Date Format** field, select **Custom** and then enter the following string in the **Custom Format** field: **yyyyMMddHH**

* When asked "Does this data have an end date/time attribute?", click **No**.

* Click **Next** to continue.

* At this point, the StoryLayer will finish being configured. The next page will show the StoryLayer, and allow you to see the animation of the data over time. In the map display, click **Play** to see the map in motion.

.. _tutorial.info:

Step 5: Add layer info
----------------------

Data without description doesn't make for a compelling MapStory, so the next step is to add metadata to the StoryLayer. Add the following on the `Info tab`_:

* **Title**—Hurricane Sandy storm track
* **Keywords**—hurricane, storm, weather
* **Abstract**—This data set is a subjectively-smoothed representation of Hurricane Sandy's location and intensity at regular intervals over its lifetime.
* **Purpose**—The best track is a living database which servers as the official U.S. National Weather Service historical record of the tropical cyclone.
* **Supplemental Information**—Originally sourced from the National Weather Service's National Hurricane Center GIS Archive at http://www.nhc.noaa.gov/gis/ .
* **Data Quality Statement**—This data is taken from a reliable source and is believed to be reasonably accurate.

Then click **Update information**.

.. _tutorial.createmap:

Step 6: Create MapStory
-----------------------

* Now that the StoryLayer has been tested, it is time to include it in a MapStory. To do this click **Create MapStory**.

* The `MapStory fullscreen viewer`_ will open, containing the layer and a base layer. Change the base layer to **Naked Earth** by clicking the radio box next to its name.

* Before continuing, it is a good idea to save the map. Click the **Save Map** button on the top left of the toolbar.

* In the dialog box that shows, enter the following information:

  * **Title**—Hurricane Sandy storm track
  * **Abstract**—This data set is a subjectively-smoothed representation of Hurricane Sandy's location and intensity at regular intervals over its lifetime.

* Click **Save**.

.. _tutorial.annotations:

Step 7: Add annotations
-----------------------

* Now that that map is saved, the **Notes** option (annotations) becomes available. We will add three notes to this map.

* Click **Add note** and **Event** from the toolbar.

* Enter the following information:

  * **Title**—First landfall
  * **Abstract**—Hurricane makes first landfall at Santiago de Cuba.
  * **Start date**—10/24/2012 10PM
  * **End date**—10/25/2012 10PM
  * **Save to map**—(check)
  * **Save to timeline**—(check)

* Click **Save**.

* Repeat this process again:

  * **Title**—Sharp turn
  * **Abstract**—Note the sharp landward turn the hurricane makes here.
  * **Start date**—10/28/2012 10PM
  * **End date**—10/29/2012 10PM
  * **Save to map**—(check)
  * **Save to timeline**—(check)

* And finally:

  * **Title**—Second landfall
  * **Abstract**—Hurricane makes landfall near Brigantine, New Jersey.
  * **Start date**—10/29/2012 2PM
  * **End date**—10/29/2012 8PM
  * **Save to map**—(check)
  * **Save to timeline**—(check)

* Click **Play** on the map to view it with the annotations.

* Click **Save map** again to make sure that all of our changes have been saved.

.. _tutorial.publishmap:

Step 8: Publish MapStory
------------------------

The final step is to publish your map. At this point, your map will still be set to **Private**, as that is the default.

* Return to the main viewer by clicking the **View info** link.

* Note the URL of this page.

* Click the `Info tab`_.

* Click **Change status**.

* Select **Anyone can search for and view**.

Your map is published! You can give out the URL as noted above and others will be able to see your MapStory.
