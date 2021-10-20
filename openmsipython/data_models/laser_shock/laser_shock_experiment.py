#imports
from gemd.entity.object import MeasurementSpec
from .run_from_filemaker_record import MeasurementRunFromFileMakerRecord

class LaserShockExperimentSpec(MeasurementSpec) :

    def __init__(self) :
        pass

class LaserShockExperiment(MeasurementRunFromFileMakerRecord) :
    
    def get_spec(self,record,specs) :
        pass

#Tags
#Grant Funding: MEDE Metals
#Launch ID: F038-R1C2
#recordId: 7
#modId: 16

#Notes
#Notes & Comments: Bad magnification on camera

#Source
#Performed By: Lezcano
#Date: 10/11/2021

#Conditions
#Laser page
#Energy: 750 #Laser: Measured Energy (mJ)
#New Energy Measurement: Yes # radial button, maybe change origin of above energy depending, or parameter in the spec
#Theoretical Beam Diameter: 1.6666666666666667 #Laser: Theoretical Beam Diameter (mm) (calculated)
#Fluence: 34.377467707849384 #Laser: Calculated Fluence (J/cm^2)
#PDV page
#PreAmp Output Power: 0 #dBm 
#PDV Spot Size: #um 
#Camera page
#Beam Profiler Gain: #dB
#Beam Profiler Exposure: #ms 
#Launch Integration page
#Base Pressure: #mTorr
#Firing page
#Return Signal Strength: N/A #dBm

#Parameters
#Experiment Type: Focusing Lens EFL calibration #dropdown menu
#Laser page
#Beam Shaper Input Beam Diameter: 25 #(mm) (dropdown menu)
#Beam Shaper: Silios #dropdown menu
#Effective Focal Length: 250 #Beam Shaping: Focusing Lens (mm) (dropdown menu)
#Drive Laser Mode: Q switched #dropdown menu
#Oscillator Setting: 10 #dropdown menu
#PDV page
#Amplifier Setting: 10 #dropdown menu
#Attenuator Angle: 260 #degrees
#Booster Amp Setting: 0 #mV  
#Focusing Lens Arrangement: #radial button 
#System Configuration: #radial button 
#Camera page
#dropdown menus for all of the below
#Camera Lens: 105 #mm
#Doubler: 1
#Camera Aperture: 0
#Lens Aperture: 11
#Camera Filter: 648 CWL/20 FWHM
#Illumination Laser: SiLux
#Laser Filter: Texwipe/diffuser
#Speed: 10,000,000 #frames/s
#Exposure: N/A #ns
#below is a radial button instead
#High Speed Camera: Shimadzu
#Beam Profiler Filter: #dropdown menu
#Launch Integration page
#Launch Ratio: ? #calculated
#PDV spot flyer ratio: #calculated
#Sample Recovery Method: none #radial button
#Launch Package Holder: Vacuum Chamber #radial button

#Properties (possibly could be other things that aren't properties actually?)
#Flyer Tilt: #dropdown
#Flyer Curvature: #dropdown
#Max Velocity: 
#Est Impact Velocity: 
#Launch Package Orientation: #dropdown
#Video Quality: #dropdown
#Recovery Box: #dropdown
#Recovery Row: #dropdown
#Recovery Column: #dropdown
#Spall State: #dropdown

#File Links
#Camera Filename: 
#Scope Filename: N/A
#Beam Profile Filename: N/A

#To skip wholesale (checklist, etc.)
#Check Energy:  
#Check Alignment:  
#Check Beam Path:  
#Check Camera:  
#Check Illumination:  
#Check Main Amp: 
#Check PDV: 
#Check PreAmp: 
#Check Triggers:  
#Check Launch ID:  
#Check Recover Sample: 
#Check Previous Sample: 
#Check Protection:  
#Check Protection Again:  
#Check Beam Profiler: 
#Check Save: 
#Check Safety:  
