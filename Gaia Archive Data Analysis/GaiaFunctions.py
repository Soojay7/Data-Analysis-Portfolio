import math
import numpy as np 

#Global constants
kappa = 0.004743717361

ra_pol = 192.8595
dec_pol = 27.12825

l_north = 122.932

sin_dec_pol = np.sin(np.radians(dec_pol))
cos_dec_pol = np.cos(np.radians(dec_pol))

TGAL = (np.array([[-0.0548755604, -0.8734370902, -0.4838350155],
	[0.4941094279, -0.4448296300, 0.7469822445],
	[-0.8676661490,  -0.1980763734, 0.4559837762]]))


def equatorial_galactic(ra,dec):
	"""Transforms equatorial coordinates (ra,dec) to Galactic coordinates (gl,gb). All inputs must be numpy arrays of the same dimension
	
		param ra: Right ascension (degrees)
		param dec: Declination (degrees)
		output (gl,gb): Tuple containing Galactic longitude and latitude (degrees)
	"""
	
	#Check for parameter consistency
	num_stars = np.size(ra)
	if np.size(dec) != num_stars:
		raise ValueError('The dimensions ra and dec do not agree. They must all be numpy arrays of the same length.')
	
	#Compute intermediate quantities
	ra_m_ra_pol = ra - ra_pol
	sin_ra = np.sin(np.radians(ra_m_ra_pol))
	cos_ra = np.cos(np.radians(ra_m_ra_pol))
	sin_dec = np.sin(np.radians(dec))
	cos_dec = np.cos(np.radians(dec))
	
	#Compute Galactic latitude
	gamma = sin_dec_pol*sin_dec + cos_dec_pol*cos_dec*cos_ra
	gb = np.degrees(np.arcsin(gamma))
	
	#Compute Galactic longitude
	x1 = cos_dec * sin_ra
	x2 = (sin_dec - sin_dec_pol*gamma)/cos_dec_pol
	gl = l_north - np.degrees(np.arctan2(x1,x2))
	gl = (gl+360.)%(360.)
	#gl = np.mod(gl,360.0) might be better
	
	#Return Galactic coordinates tuple
	return (gl, gb)

def equatorial_XYZ(ra,dec,dist,dist_error=None):
	"""
	Transforms equatorial coordinates (ra,dec) and distance to Galactic position XYZ. All inputs must be numpy arrays of the same dimension.
	
	param ra: Right ascension (degrees)
	param dec: Declination (degrees)
	param dist: Distance (parsec)
	param dist_error: Error on distance (parsec)
	
	output (X,Y,Z): Tuple containing Galactic position XYZ (parsec)
	output (X,Y,Z,EX,EY,EZ): Tuple containing Galactic position XYZ and their measurement errors, used if any measurement errors are given as inputs (parsec)
	"""
	
	#Verify keywords
	num_stars = np.size(ra)
	if np.size(dec) != num_stars or np.size(dist) != num_stars:
		raise ValueError('ra, dec and distance must all be numpy arrays of the same size !')
	if dist_error is not None and np.size(dist_error) != num_stars:
		raise ValueError('dist_error must be a numpy array of the same size as ra !')
	
	#Compute Galactic coordinates
	(gl, gb) = equatorial_galactic(ra,dec)
	
	cos_gl = np.cos(np.radians(gl))
	cos_gb = np.cos(np.radians(gb))
	sin_gl = np.sin(np.radians(gl))
	sin_gb = np.sin(np.radians(gb))
	
	X = cos_gb * cos_gl * dist
	Y = cos_gb * sin_gl * dist
	Z = sin_gb * dist
	
	if dist_error is not None:
		#X_gb = sin_gb * cos_gl * dist * np.pi/180.
		#X_gl = cos_gb * sin_gl * dist * np.pi/180.
		X_dist = cos_gb * cos_gl
		EX = np.abs(X_dist * dist_error)
		Y_dist = cos_gb * sin_gl
		EY = np.abs(Y_dist * dist_error)
		Z_dist = sin_gb
		EZ = np.abs(Z_dist * dist_error)
		return (X, Y, Z, EX, EY, EZ)
	else:
		return (X, Y, Z)
		
def equatorial_UVW(ra,dec,pmra,pmdec,rv,dist,pmra_error=None,pmdec_error=None,rv_error=None,dist_error=None):
	"""
	Transforms equatorial coordinates (ra,dec), proper motion (pmra,pmdec), radial velocity and distance to space velocities UVW. All inputs must be numpy arrays of the same dimension.
	
	param ra: Right ascension (degrees)
	param dec: Declination (degrees)
	param pmra: Proper motion in right ascension (milliarcsecond per year). 	Must include the cos(delta) term
	param pmdec: Proper motion in declination (milliarcsecond per year)
	param rv: Radial velocity (kilometers per second)
	param dist: Distance (parsec)
	param ra_error: Error on right ascension (degrees)
	param dec_error: Error on declination (degrees)
	param pmra_error: Error on proper motion in right ascension (milliarcsecond per year)
	param pmdec_error: Error on proper motion in declination (milliarcsecond per year)
	param rv_error: Error on radial velocity (kilometers per second)
	param dist_error: Error on distance (parsec)
	
	output (U,V,W): Tuple containing Space velocities UVW (kilometers per second)
	output (U,V,W,EU,EV,EW): Tuple containing Space velocities UVW and their measurement errors, used if any measurement errors are given as inputs (kilometers per second)
	"""
	
	#Verify keywords
	num_stars = np.size(ra)
	if np.size(dec) != num_stars or np.size(pmra) != num_stars or np.size(pmdec) != num_stars or np.size(dist) != num_stars:
		raise ValueError('ra, dec, pmra, pmdec, rv and distance must all be numpy arrays of the same size !')
	if pmra_error is not None and np.size(pmra_error) != num_stars:
		raise ValueError('pmra_error must be a numpy array of the same size as ra !')
	if pmdec_error is not None and np.size(pmdec_error) != num_stars:
		raise ValueError('pmdec_error must be a numpy array of the same size as ra !')
	if rv_error is not None and np.size(rv_error) != num_stars:
		raise ValueError('rv_error must be a numpy array of the same size as ra !')
	if dist_error is not None and np.size(dist_error) != num_stars:
		raise ValueError('dist_error must be a numpy array of the same size as ra !')
	
	#Compute elements of the T matrix
	cos_ra = np.cos(np.radians(ra))
	cos_dec = np.cos(np.radians(dec))
	sin_ra = np.sin(np.radians(ra))
	sin_dec = np.sin(np.radians(dec))
	T1 = TGAL[0,0]*cos_ra*cos_dec + TGAL[0,1]*sin_ra*cos_dec + TGAL[0,2]*sin_dec
	T2 = -TGAL[0,0]*sin_ra + TGAL[0,1]*cos_ra
	T3 = -TGAL[0,0]*cos_ra*sin_dec - TGAL[0,1]*sin_ra*sin_dec + TGAL[0,2]*cos_dec
	T4 = TGAL[1,0]*cos_ra*cos_dec + TGAL[1,1]*sin_ra*cos_dec + TGAL[1,2]*sin_dec
	T5 = -TGAL[1,0]*sin_ra + TGAL[1,1]*cos_ra
	T6 = -TGAL[1,0]*cos_ra*sin_dec - TGAL[1,1]*sin_ra*sin_dec + TGAL[1,2]*cos_dec
	T7 = TGAL[2,0]*cos_ra*cos_dec + TGAL[2,1]*sin_ra*cos_dec + TGAL[2,2]*sin_dec
	T8 = -TGAL[2,0]*sin_ra + TGAL[2,1]*cos_ra
	T9 = -TGAL[2,0]*cos_ra*sin_dec - TGAL[2,1]*sin_ra*sin_dec + TGAL[2,2]*cos_dec
	
	#Calculate UVW
	reduced_dist = []
	for i in range(len(dist)):
		red = kappa*dist[i]
		reduced_dist.append(red)
	#reduced_dist = kappa*dist
	U = T1*rv + T2*pmra*reduced_dist + T3*pmdec*reduced_dist
	V = T4*rv + T5*pmra*reduced_dist + T6*pmdec*reduced_dist
	W = T7*rv + T8*pmra*reduced_dist + T9*pmdec*reduced_dist
	
	#Return only (U, V, W) tuple if no errors are set
	if pmra_error is None and pmdec_error is None and rv_error is None and dist_error is None:
		return (U, V, W)
		
	#Propagate errors if they are specified
	if pmra_error is None:
		pmra_error = np.zeros(num_stars)
	if pmdec_error is None:
		pmdec_error = np.zeros(num_stars)
	if rv_error is None:
		rv_error = np.zeros(num_stars)
	if dist_error is None:
		dist_error = np.zeros(num_stars)
	reduced_dist_error = []
	for i in range(len(dist_error)):
		red = kappa*dist_error[i]
		reduced_dist_error.append(red)
	#reduced_dist_error = kappa*dist_error
	
	#Calculate derivatives
	T23_pm = np.sqrt((T2*pmra)**2+(T3*pmdec)**2)
	T23_pm_error = np.sqrt((T2*pmra_error)**2+(T3*pmdec_error)**2)
	EU_rv = T1 * rv_error
	EU_pm = T23_pm_error * reduced_dist
	EU_dist = T23_pm * reduced_dist_error
	EU_dist_pm = T23_pm_error * reduced_dist_error
	
	T56_pm = np.sqrt((T5*pmra)**2+(T6*pmdec)**2)
	T56_pm_error = np.sqrt((T5*pmra_error)**2+(T6*pmdec_error)**2)
	EV_rv = T4 * rv_error
	EV_pm = T56_pm_error * reduced_dist
	EV_dist = T56_pm * reduced_dist_error
	EV_dist_pm = T56_pm_error * reduced_dist_error

	T89_pm = np.sqrt((T8*pmra)**2+(T9*pmdec)**2)
	T89_pm_error = np.sqrt((T8*pmra_error)**2+(T9*pmdec_error)**2)
	EW_rv = T7 * rv_error
	EW_pm = T89_pm_error * reduced_dist
	EW_dist = T89_pm * reduced_dist_error
	EW_dist_pm = T89_pm_error * reduced_dist_error
	
	#Calculate error bars
	EU = np.sqrt(EU_rv**2 + EU_pm**2 + EU_dist**2 + EU_dist_pm**2)
	EV = np.sqrt(EV_rv**2 + EV_pm**2 + EV_dist**2 + EV_dist_pm**2)
	EW = np.sqrt(EW_rv**2 + EW_pm**2 + EW_dist**2 + EW_dist_pm**2)
	
	#Return measurements and error bars
	return (U, V, W, EU, EV, EW)
