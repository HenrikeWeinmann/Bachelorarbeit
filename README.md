# DICOM Image viewer and selection tool

This a tool that displays 'DICOM' images and allows the user to make selections by a mouse click.
Any Cine Data set can be loaded as long as it follows a given structure.
A data set can be loaded via Finder/File Manager or a path to the data set.
## Set Up and Download instructions
To run the application you will need all files located in the Application Folder on 
this Github directory.
At this point in time there is no .exe available.

To start the application, run the Main.py file.
The main interface of the application should open.

To load Data, it must be in this form:
- CINE study
  - slice01
    - frame01
    - frame02
    - frame03
    - ...
  - slice02
    - frame01
    - frame02
    - frame03
    - ...
  - slice03
    - ...


Single images and single slices can be loaded the same way.

## Functions provided by the Tool
- display image using different color maps
- scroll through Data Set and make selections by mouse click
- autoplay the sequence or go though frame by frame

### Selection Modes available:
- single point selection mode
- multiple point selection mode
- polygon selection mode
- *freehand selection (only in multiple point selection)*

### Plans for the future...
- multiple visions of an area (minimap)
- color themes

By Henrike Weinmann
Last Updated(24.06.2021)
