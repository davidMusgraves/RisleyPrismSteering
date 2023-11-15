This is a simple Python script to calculate the steering angle of a Risley Prism pair of two infrared materials.
The file 'Materials.csv' contains the names and Sellmeier coefficients for 20 separate IR materials.
In the *Inputs* section:
    - set the wavelength range in microns. 
    - This script is structured to use one material_1 value and an array of material_2 values in order to allow for calculation of multiple material combinations if desired.
    - Prism Ranges allows the user to set the range and step size of the search.
    - Set the thresholds for Secondary Dispersion and Compression

Upon execution, the user is prompted for an output file name.
The script then calculates the steering angle and beam compression for every step in the ranges defined in Prism Ranges in *Inputs*
