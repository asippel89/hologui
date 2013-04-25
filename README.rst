.. note::

   To ensure the most up to date information, please visit the documentation page at `Hologui Docs <http://holometer.uchicago.edu/~asippel/Worklog/projects/p2acnet.html>`_


Holometer Data Visualizer - HoloGUI
===================================

This project page details the development of the GUI for visualizing the holometer data. It will be an encompassing GUI which handles several data sources and plots in real time those assorted data types. 

Architecture
------------

Because this program must be able to handle multiple data sources, its infrastructure must be designed for extensibility and testability. The current application architecture follows a modified Model-View-Presenter format to accomplish this. In this architecture, GUI elements (or widgets) such as buttons, text fields, etc. are kept completely separate from any logic dealing with what they display. The view logic and state is controlled by Presenters, which have knowledge of their paired GUI object group (such as a panel or form).

The View (which is the collective term for all of the raw GUI elements and their layout) exists independently of the underlying data operations the program is designed to handle, which in this case is the data to be served up to the plots. 

Functionality
-------------

Below is a list of the desired functionality broken into sections based on category.

User Interface
~~~~~~~~~~~~~~


.. figure:: /docs/Diaggui_Screenshot.png
   :alt: Old Diaggui Screenshot
   :scale: 50%
   :align: center

   Fig 1: Diaggui Screenshot - Some of the functions of Diaggui will be improved upon and the user interface enhanced for the HoloGUI Data Visualizer
   
.. figure:: /docs/Futuristic_UI.png
   :alt: Futuristic Looking User Interface
   :scale: 75%
   :align: center

   Fig 2: Futuristic User Interface- HoloGUI will look something like this

* Simple, modern-looking user interface
* Support for saving/loading view preferences, similar to modern IDEs

  * Have plots/windows shown in a certain arrangement, with certain settings
  * Do not show unneccesary details, unless asked for them!
* Utilize dynamic view creation/customization via the WxPython AUI framework
* Consistent basic interface accross application modes (CSD, ACNET, Control System)

CSD Viewer
~~~~~~~~~~

For viewing live Cross Spectra from the interferometers. Data is received over a TCP connection from the CSD streaming software.

.. figure:: /docs/CSDView_Screenshot.png
   :alt: Example Screenshot of CSDView GUI 2/22/2013
   :scale: 50%
   :align: Center
           
   Fig 3: Example Screenshot of CSDView GUI- 2/22/2013

* Connects to a TCP server to stream cross spectra data
* Collects the data streamed this way
* Plot/Update plot in real time (or several times per second)
* View the RMS of the CSD over time
* Select a region of time in the RMS plot and calculate/view the averaged CSD over that time frame

ACNET Data
~~~~~~~~~~

Uses existing :ref:`p2acnet` to display arbitrary data from Fermilab's ACNET service. The Holometer uses this for logging a variety of objects, most notably the vacuum levels and temperature.

* Should have similar capabilities as the CSD Viewer, including having multiple open tabs/panes
* Should allow for continuous updating of plot based on incoming ACNET information

Plot Canvas
~~~~~~~~~~~

* Would like for the actually drawing of the plots to not be expensive (i.e. don't want to bog down computer simply by updating plot)
* Ability to zoom in/out, save, and control view options of the plot. This includes:
  
  * X and Y Axis paramters (auto adjust or set manually)
  * Set line colors/styles
  * Labels and Titles
  * Other general plot options


Development
-----------

Project Timeline
~~~~~~~~~~~~~~~~

* Alpha Release (Monday, March 4 2013)
  
  * Organize project files into hierachical packages
  * Make public git repository available
  * Implement versioning system
  * Most basic features implemented; clean slate
* User Feedback/Continued Development (Complete by Monday, March 18 2013)

  * Use valuable user feedback to guide further development efforts
  * Release new versions continuously; instruct users to pull often
  * Begin adding other data source options in separate branch


Current To Do List
~~~~~~~~~~~~~~~~~~

* Very Important! Need to have model calculate the running average based on the number of coadded frames; This is what needs to be plotted in the csd plots as well as the rms plots

  * Update 4/3/2013: Should check this again and determine how the model should behave with real data
* Add buttons for plots that force autoscaling, clear the data, etc. 

  * Update 4/3/2013: 
* Allow for calculating/displaying CSD for a given time frame

  * Update 2/26/13: Now can select time region in RMS plots, now just need to send that to controller (and then the model)
* Sort the channels listed in the plot settings panel
* Allow for the ability to specify axis parameters, such as legend location, etc.
  
  * Update 2/26/13: Title, Legend, and Grid now can be updated from the settings panel; still need to implement preventing the automatic rescaling of axis
* Clean up plot updating

  * Attempt to use blitting, i.e. don't redraw entire canvas unless you want to adjust axis parameters
  * Should allow faster, smoother plot updates
  * Less annoying axis changing
* Need to exchange metadata and incorporate that into plots (units, legend, etc)

  * Update 2/26/13: Began implementing this, need more information on what metadata will be sent and what needs to be done with it
* Set up so that both RMS and CSD plots can reset the data (clear data_dict) when unsubscribed from a particular channel
* Refactor code before alpha release!!

  * Do so by going through the process of adding another plot type and seeing the difficulties
  * Implement ticketing system??
