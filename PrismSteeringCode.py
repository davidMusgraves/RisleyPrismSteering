import numpy as np
import pandas as pd
import csv

# Load the Materials data into a DataFrame
Materials = pd.read_csv('Materials.csv')

# Convert the columns of the DataFrame to NumPy arrays
MaterialNumbers = Materials.values[:, 0]
MaterialNames   = Materials.values[:, 1]
B1  = Materials.values[:, 2]
C1  = Materials.values[:, 3]
B2  = Materials.values[:, 4]
C2  = Materials.values[:, 5]
B3  = Materials.values[:, 6]
C3  = Materials.values[:, 7]

# Geometric constraints on the prisms
theta0A = 0 #Angle of the incoming beam. Typically left as 0
gamma1A = 0 #Manufacturability constraints + (SWaP) lead me to think this has to be 0


######################### Inputs ########################
# Wavelength range and resolution
lambdaMin = 1.0  # Minimum wavelength in micrometers
lambdaMax = 3.0  # Maximum wavelength in micrometers
lambdaStep = 0.1  # Wavelength step in micrometers

# Materials
material_1 = 18
material_2_array = [1]

# Prism ranges
alpha1A_start = 0.0
alpha1A_stop = 1.5
alpha1A_step = 1e-4

alpha2A_start = -0.0
alpha2A_stop = -1.5
alpha2A_step = -1e-4

# SWaP thresholds
SD_threshold = 1e-3
compression_threshold = 2.0


############################## Definitions ##################################
# 1. Build index tables based on wavelength table and defined materials
def index_builder(wavelength, material_1, material_2):
    n1 = np.sqrt(1 + (B1[material_1] * wavelength ** 2) / (wavelength ** 2 - C1[material_1]) + (
                B2[material_1] * wavelength ** 2) / (wavelength ** 2 - C2[material_1]) + (
                             B3[material_1] * wavelength ** 2) / (wavelength ** 2 - C3[material_1]))
    n2 = np.sqrt(1 + (B1[material_2] * wavelength ** 2) / (wavelength ** 2 - C1[material_2]) + (
                B2[material_2] * wavelength ** 2) / (wavelength ** 2 - C2[material_2]) + (
                             B3[material_2] * wavelength ** 2) / (wavelength ** 2 - C3[material_2]))

    return n1, n2


# 2. Calculate beam steering and compression
def TwoPrismCompression(n1, n2, theta0A, gamma1A, alpha1A, alpha2A):
    # Define additional angular values based on symmetry of the A and B groups:
    beta1A = gamma1A - alpha1A
    gamma2A = beta1A
    beta2A = gamma2A - alpha2A
    alpha1B = alpha1A
    beta1B = gamma1A
    gamma1B = alpha1B + beta1B
    beta2B = gamma1B
    alpha2B = alpha2A
    gamma2B = alpha2B + beta2B

    # Step by step equations
    theta1A = theta0A - beta2A
    theta1APrime = np.arcsin((1 / n2) * np.sin(theta1A))
    theta2A = theta1APrime - alpha2A
    theta2APrime = np.arcsin((n2 / n1) * np.sin(theta2A))
    theta3A = theta2APrime - alpha1A
    theta3APrime = np.arcsin(n1 * np.sin(theta3A))
    theta4A = theta3APrime + gamma1A

    theta1B = theta4A - beta1B
    theta1BPrime = np.arcsin((1 / n1) * np.sin(theta1B))
    theta2B = theta1BPrime - alpha1B
    theta2BPrime = np.arcsin((n1 / n2) * np.sin(theta2B))
    theta3B = theta2BPrime - alpha2B
    theta3BPrime = np.arcsin(n2 * np.sin(theta3B))
    compression = 1 / (np.cos(theta3BPrime))
    if np.isnan(compression).any():
        compression = np.nan
    theta4B = theta3BPrime + gamma2B

    return theta4B, compression


################# Execution ###################################
# Build the wavelength table
wavelength = np.arange(lambdaMin, lambdaMax + lambdaStep, lambdaStep)

# Build the prism tables
alpha1A_range = np.arange(alpha1A_start, alpha1A_stop + alpha1A_step, alpha1A_step)
alpha2A_range = np.arange(alpha2A_start, alpha2A_stop + alpha2A_step, alpha2A_step)

output_filename = input("Enter the name of the output file (without extension): ") + ".csv"

with open(output_filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Material 1', 'Material 2', 'Max SA', 'alpha1A', 'alpha2A', 'SD', 'Compression'])

    for material_2 in material_2_array:
        # Build the index tables
        n1, n2 = index_builder(wavelength, material_1, material_2)

        # Initialize parameters
        SA_max = 0
        alpha1A_opt = 0
        alpha2A_opt = 0
        SD_opt = 1000

        # Loop over all alpha1A/alpha2A combinations, calculate max SA given constraints in Inputs
        for i in range(len(alpha1A_range)):
            for j in range(len(alpha2A_range)):
                alpha1A = alpha1A_range[i]
                alpha2A = alpha2A_range[j]

                theta4B, compression = TwoPrismCompression(n1, n2, theta0A, gamma1A, alpha1A, alpha2A)

                mean_SA = np.mean(theta4B)
                mean_compression = np.mean(compression)
                SD = (np.max(theta4B) - np.min(theta4B)) / 2
                

                if SD < SD_threshold and mean_compression < compression_threshold and mean_SA > SA_max:
                    SA_max = mean_SA
                    alpha1A_opt = alpha1A
                    alpha2A_opt = alpha2A
                    SD_opt = SD
                    compression_opt = mean_compression

        writer.writerow([material_1, material_2, SA_max, alpha1A_opt, alpha2A_opt, SD_opt, compression_opt])
        print("Material 1: ", material_1, ", Material 2: ", material_2, ", Max SA: ", SA_max, ", alpha1A: ",
              alpha1A_opt, ", alpha2A: ", alpha2A_opt, ", SD: ", SD_opt, ", compression: ", compression_opt)
