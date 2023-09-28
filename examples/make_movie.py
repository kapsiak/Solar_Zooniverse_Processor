import os
import sys
import getopt
import math
import numpy

import solar.visual.img as im
import solar.service.hek as hserv
import solar.database

from solar.database.tables import Fits_File, Visual_File, Service_Request
from solar.service.cutout import Cutout_Service
from solar.service.attribute import Attribute 
from datetime import timedelta

'''
Main functions:
make_fits()
    -looks for HEK jet events occurring during this time
    -makes the .fts files for the found events and saves them to sets of folders
make_frames()
    -make images from the .fts files and saves them to sets of folders
make_subjects()
    -makes video subjects from the images and saves them
    -returns a dictionary of the subjects (created and pre-existing)
make_metdata()
    -uses dictionary of created subjects to write the metadata file to accompany subjects
'''

fits_folder = 'files/fits'
pngs_folder = 'files/generated/png'
movie_folder = 'files/generated/mp4'
meta_folder = 'files/exports'
temp_folder = 'files/temp'
overwrite = False
visuals_only = False
videos_only = False
skip_metadata = False

def add_one(string_int):
    """
    Takes a 2-character string of an integer and returns a 2-character string of the integer + 1
    """
    number = int(string_int)
    number += 1
    output = ''
    
    if number < 10:
        output = '0' + str(number)
    else:
        output = str(number)

    return output

def tomorrow(date):
    """
    Gives the day after the given date

    Parameters
    ----------
    date : str
        Day formatted as YYYY-MM-DD
    
    Returns
    -------
    tomorrow : str
        Day after the given date, formatted as YYYY-MM-DD
    """

    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]
    day_after = ''

    if month == "02": #If month is february
        if int(year) % 4 == 0 and not int(year) % 100 == 0 or int(year) % 1000 == 0: #If it's a leap year
            if day == "29": #Month changes
                day_after = year + "-03-01"
            else: #Month doesn't change
                day_after = year + '-' + month + '-' + add_one(day)
        elif day == "28": #Not leap year, month changes
            day_after = year + "-03-01"
        else: #Month doesn't change
            day_after = year + '-' + month + '-' + add_one(day)
    elif month in ["04", "06", "30", "11"] and day == "30": #If the month has only 30 days
        day_after = year + '-' + add_one(month) + '-01'
    elif day == "31": #If it's the 31st
        if month == "12": #If it's December
            day_after = str(int(year) + 1) + '-01-01'
        else: #Any other month
            day_after = year + '-' + add_one(month) + '-01'
    else: #Nothing special, just add one to the day
        day_after = year + '-' + month + '-' + add_one(day)
    
    return day_after

def check_directory(folder):
    """
    Checks if a folder exists
    If it does not, creates the folder and its parent directories

    Parameters
    ----------
    folder : str
        The folder that we want to make sure exists

    Returns
    -------
    existed : bool
        Returns true if the folder already existed
    """
    try:
        #If folder exists, we return True and are done
        if os.path.isdir(folder):
            return True
        #Otherwise, we make the folder and return False
        else:
            os.mkdir(folder)
            return False
    #If FileNotFoundError occurs, it is because the parent directory doesn't exist.
    except FileNotFoundError:
        #Makes sure there is no '/' at the end of the given folder name
        if folder.endswith('/'):
            folder = folder[:-1]

        #Make sure parent directory exists
        parent_dir = folder[:folder.rfind('/')]
        check_directory(parent_dir)
        
        #Now we make the folder and return False
        os.mkdir(folder)
        return False

def make_fits(date, pre_existing, cadence=24):
    """
    Generates fits files from cutouts matching the given date

    Parameters
    ----------
    date : str
        Date of the event
    pre_existing : str[]
        sol_standards of the fits files which already exist
    cadence : int
        Time between starts of each produced cutout in seconds
        Default cadence is 24
    """

    #0db.py
    solar.database.create_tables()

    #Define start and end times of search
    starttime = ''
    endtime = ''

    if len(date.split('-')) == 3: #If day is provided
        starttime = date + "T00:00:00"
        endtime = tomorrow(date) + "T00:00:00"
        
    elif len(date.split('-')) == 2: #If only month is provided
        starttime = date + "-01T00:00:00"
        if date.split('-')[1] == "12": #If it's December
            endtime = str(int(date.split('-')[0]) + 1) + '-01-01T00:00:00'
        else: #Any other month
            endtime = date.split('-')[0] + '-' + add_one(date.split('-')[1]) + '-01T00:00:00'
    
    else: #If only year is provided
        starttime = date + '-01-01T00:00:00'
        endtime = str(int(date) + 1) + '-01-01T00:00:00'

    print("Searching HEK database for suspected solar jets between")
    print(starttime + "\tand\t" + endtime)

    #1HEKrequestcut.py
    hek = hserv.Hek_Service(
        event_starttime=starttime,
        event_endtime=endtime,
        event_type=["cj"])
    events = hek.data
    hek.submit_request()
    hek.save_data()

    for event in events:
        #Skip this event if a .fts file already exists for it
        modified_sol_standard = event.sol_standard.replace(':', '-')
        if modified_sol_standard in pre_existing:
            continue

        cutout = Cutout_Service._from_event(event)

        #TODO: Are both of these cadence changes needed?
        #Changes cadence from default if needed
        if cadence != 24: 
            start_time, = [x for x in cutout.params if x.name == "starttime"]
            end_time, = [x for x in cutout.params if x.name == "endtime"]
            frame_num = math.ceil((end_time.value - start_time.value) / timedelta(seconds = cadence))
            for x in cutout.params:
                if x.name == "max_frames":
                    cutout.params.remove(x)
                    cutout.params.append(Attribute("max_frames", frame_num))
                    print("max_frames:\t" + str(frame_num))
                else:
                    print(str(x.name) + ":\t" + str(x.value))

        cutout.fetch_data(delay=60)
        cutout.save_data()
        cutout.save_request()
        
        cutout.submit_request()
        cutout.save_request()

    #2checkHEKstatus.py
    #old_cutout_request = Service_Request.select()
    #for obj in old_cutout_request:
        #print(obj.event.sol_standard)
        #print(obj.status)

    #3downloadreq.py
    submitted_cutout_request = Service_Request.select().where(Service_Request.status=='submitted')
    print("Downloading data for " + str(len([obj for obj in submitted_cutout_request])) + " events")
    for obj in submitted_cutout_request:
        cutout = Cutout_Service._from_model(obj)

        #Changes cadence from default if needed
        if cadence != 24: 
            start_time, = [x for x in cutout.params if x.name == "starttime"]
            end_time, = [x for x in cutout.params if x.name == "endtime"]
            frame_num = math.ceil((end_time.value - start_time.value) / timedelta(seconds = cadence))
            for x in cutout.params:
                if x.name == "max_frames":
                    cutout.params.remove(x)
                    cutout.params.append(Attribute("max_frames", frame_num))

        cutout.fetch_data(delay=60)
        cutout.save_data()
        cutout.save_request()

    Fits_File.update_table()

def make_frames(date, pre_existing, cadence=24, dpi=150, overwrite = False):
    """
    Generates images from fits files matching the given date

    Parameters
    ----------
    date : str
        Date of the event
    pre_existing : str[]
        sol_standards of the image files which already exist
    cadence : int
        Time between starts of each produced cutout in seconds
        Default cadence is 24
    dpi : int
        Value that reflects the quality of the images - higher values are high quality .pngs
        Default dpi is 150
    overwrite : bool
        Decides if function will overwrite pre existing images
        Default is False
    """
    #4makevis.py
    image_builder = im.Basic_Image('png', dpi=dpi)
    fitsf = Fits_File.select().where(Fits_File.sol_standard.startswith('SOL' + date))
    print('Found ' + str(len([obj for obj in fitsf])) + ' cutouts, producing images...')
    start_time = fitsf[0].image_time
    print(start_time)

    for fits in fitsf:
        #If the .fts file already has a pre-existing image folder, skip making new images
        modified_sol_standard = fits.sol_standard.replace(':', '-')
        if modified_sol_standard in pre_existing:
            continue

        img = Visual_File.create_new_visual(fits, image_builder, overwrite=overwrite)
        img.save()

def make_movie(frames, fps=10, overwrite=False):
    """
    Deprecated - no longer in use

    Takes a series of .png images and turns them into an mp4 file
    
    Parameters
    ----------
    frames : str[]
        List containing a series of strings, each is a path to a folder containing desired .png files
        Sorted in order of appearance in the movie
    fps : float
        Number of frames per second which appear in the movie
        Default: 10 frames per second
    overwrite : bool
        Toggles overwriting videos
        Default: False
    """
    print("Turning images into movies...")
    for event in frames:
        print("Working on " + event)
        #Collect all .png images in the given folder
        movie_frames = []
        for file in os.listdir(event):
            if file.endswith('.png'):
                movie_frames.append(event + '/' + file)
        
        #Sort the images so that they occur in order
        movie_frames = sorted(movie_frames)

        #Builds the movie folder if it does not already exist
        check_directory(movie_folder)
        
        #Print some information
        print('Found ' + str(len(movie_frames)) + ' frames')

        #Turn images into an .mp4
        movie_name = event.sol_standard + ".mp4"
        png_to_mp4(movie_frames, movie_name=movie_name, fps=fps, overwrite=overwrite)

def png_to_mp4(pngs, fps=10, movie_name=None, overwrite=False, max_size=2**10 * 1000):
    """
    Takes pngs and converts them into mp4s

    Parameters
    ----------
    pngs : str[]
        An ordered list containing paths to each png for the movie
    fps : int
        The frames per second used in the movie
        Default is 10
    movie_name : str
        Names the movie with the given string, if provided.
        Otherwise, uses the name of the first image handed to it.
    max_size : int
        Sets the max size of the video output
        Defaults to 2**10 * 1000 bytes = 1000 Kilobytes
    """
    #Checks if movie_name has been passed as an argument
    if movie_name == None:
        #Movie is named after first image passed to it
        movie_name = pngs[0].split('/')[-1] + '.mp4'

    #Copy the pngs to be used into the temporary folder
    check_directory(temp_folder)
    for png in pngs:
        os.system('cp ' + png + ' ' + temp_folder + '/' + png.split('/')[-1])

    #Lowest possible crf is 25
    crf = 25

    #Set initial file size to be larger than the max size so that the first loop runs
    file_size = max_size + 1

    #Loop is repeated until file size is sufficiently small
    while file_size > max_size:
        #Build the ffmpeg command to create the video
        #Base command
        ffmpeg_command = "ffmpeg "
        #Suppress output
        ffmpeg_command += "-hide_banner -loglevel error "
        #-r: <fps>
        ffmpeg_command += "-framerate " + str(fps) + ' '
        #Collect all input files from the temporary folder
        ffmpeg_command += "-pattern_type glob -i \'" + temp_folder + "/*.png\' "
        if overwrite:
            #-y: Overwrite an existing video
            ffmpeg_command += "-y "
        else:
            #-n: Do not overwrite existing video
            ffmpeg_command += "-n "
        #Disables audio output
        ffmpeg_command += "-an "
        #Format the video to be playable by most video players
        ffmpeg_command += "-pix_fmt yuv420p "
        #Commands for better compression of video
        ffmpeg_command += "-c libx264 -crf " + str(crf) + " " #Note: Higher crf gives better compression at the cost of video quality
        #-r: <fps>
        ffmpeg_command += "-r " + str(fps) + ' '
        #Output file name
        ffmpeg_command += movie_folder + '/' + movie_name

        #Run ffmpeg generation of movie
        #print('Running command:')
        #print(ffmpeg_command)
        os.system(ffmpeg_command)

        #Calculates output video size
        file_size = os.path.getsize(movie_folder + '/' + movie_name)

    #Remove temporary folder and its contents
    os.system('rm -rf ' + temp_folder)

    '''
    #Use moviepy to turn images into .mp4 file
    movie = Mpy.ImageSequenceClip(pngs, fps = fps)
    print('Making movie at ' + str(fps) + ' images per second...')
    
    movie.write_videofile(movie_folder + "/" + movie_name, preset='placebo', audio=False)
    print('Movie created and saved as ' + movie_name)
    '''


def make_subjects(date, max_frames, spacing, fps=10, overwrite=False, max_size=2**10 * 1000):
    """
    Cuts up images into subjects
    Subjects are movies with max_frames frames in them.
    
    Parameters
    ----------
    date : str
        The date in the format of YYYY-MM-DD
        DD and MM can be left off if not given
    max_frames : int
        The number of frames each movie subject will have
    spacing : int
        The minimum number of overlapping frames that subjects will have with each other
    fps : int
        The number of frames per second used in the created subjects
        Default is 10
    overwrite : bool
        Toggles overwriting pre-existing subjects
        Default is False
    max_size : int
        Sets the max size of each video in bytes
        Default is 2**10 * 1000 bytes = 1000 Kilobytes

    Returns
    -------
    subjects : dict
        A dictionary containing each subject
            Each subject is a dict containing:
                images: the image names used to create the subject
                movie: the name of the .mp4 file
                sol_standard: the sol_standard of the event used to create the subject
    """

    subjects = {}
    separation = max_frames - spacing

    #Make sure png folder exists
    check_directory(pngs_folder)

    #Iterate through all image folders
    for folder in os.listdir(pngs_folder):
        #Skip folders that don't match what we're looking for
        if not folder.startswith("SOL" + date):
            continue

        #Get the total number of images generated from this event
        print(pngs_folder + "/" + folder)
        images = os.listdir(pngs_folder + "/" + folder)
        images.sort()
        num_images = len(images)

        if num_images < max_frames:
            #Collect images for this subject
            image_paths = []
            for img in images:
                image_paths.append(pngs_folder + "/" + folder + "/" + img)
            
            #Movie is named as <event.sol_standard>_sub<number>.mp4
            movie_name = folder + "_sub1.mp4"

            #Create movie
            png_to_mp4(image_paths, fps = fps, movie_name = movie_name, overwrite = overwrite, max_size=max_size)

            #Add subject to dictionary
            subjects[images[0]] = {
                'images' : images,
                'movie' : movie_name,
                'sol_standard' : folder
            }
        else:
            counter = 0
            #Create subjects with max_frames frames and spacing overlapping frames
            while counter * separation <= num_images - max_frames:
                #Collect images for this subject
                subject_images = []
                image_paths = []
                for i in range(counter * separation, counter * separation + max_frames):
                    subject_images.append(images[i])
                    image_paths.append(pngs_folder + "/" + folder + "/" + images[i])
                
                #Movie is named as <event.sol_standard>_sub<number>.mp4
                movie_name = folder + "_sub" + str(counter+1) + ".mp4"

                #Create movie
                png_to_mp4(image_paths, fps = fps, movie_name = movie_name, overwrite = overwrite, max_size=max_size)

                #Add images to subjects
                subjects[images[counter * separation]] = {
                    'images' : subject_images,
                    'movie' : movie_name,
                    'sol_standard' : folder
                }

                #Increment counter
                counter += 1

            #If we need one more subject to catch final frames, create it
            if not images[-max_frames] in subjects.keys():
                #Collect images for this subject
                subject_images = []
                image_paths = []
                for i in range(num_images-max_frames, num_images):
                    subject_images.append(images[i])
                    image_paths.append(pngs_folder + "/" + folder + "/" + images[i])
                
                #Movie is named as <event.sol_standard>_sub<number>
                movie_name = folder + "_sub" + str(counter+1) + ".mp4"

                #Create movie
                png_to_mp4(image_paths, fps = fps, movie_name=movie_name, overwrite=overwrite, max_size=max_size)

                #Add images to subjects
                subjects[images[counter * separation]] = {
                    'images' : subject_images,
                    'movie' : movie_name,
                    'sol_standard' : folder
                }

    return subjects

def make_metadata(date, subjects, fps, cadence, overwrite=False):
    """
    Creates and saves the metadata that will be uploaded with the Zooniverse subjects
    
    Parameters
    ----------
    date : str
        The dates we are generating meta data for
        Formatted as one of: YYYY-MM-DD, YYYY-MM, YYYY
    subjects : dict
        The dictionary containing the subjects and their information
    fps : int
        The frames per second used to create the subject
    cadence : int
        The cadence at which .fts cutouts were obtained from AIA
        Should be a multiple of 12
    overwrite : bool
        Toggles overwriting previous files (False prevents overwriting)
    """

    #Build the headers for the metadata
    headers = build_headers()

    rows = []
    for key in subjects.keys():
        rows.append(build_row(subjects[key], fps, cadence))

    #Make export directory if it does not already exist
    check_directory(meta_folder + '/SOL' + date)

    #Check for meta.csv
    if 'meta.csv' in os.listdir(meta_folder + '/SOL' + date):
        print('Found pre-existing file:\t' + meta_folder + '/SOL' + date + '/meta.csv')
        
        #If we have selected overwriting, we will create a new meta.csv
        if overwrite:
            print('Overwriting...')
        #Otherwise, we leave the old meta.csv alone and the function has completed its purpose
        else:
            return

    #We will save data as meta_reduced.csv
    meta_path = meta_folder + '/SOL' + date + '/meta.csv'

    #Save metadata
    with open(meta_path, 'w') as meta_file:
        write_line(meta_file, headers)
        for row in rows:
            write_line(meta_file, row)

def write_line(file, values):
    """
    Writes each element in values as its own element in one line of a file
    Adds a new line after it is done

    Parameters
    ----------
    file : _io.TextIOWrapper
        The file being written to
    values : List
        The list of values to be written
    """

    #Write all of the values separated by commas
    for value in values:
        #Convert value to a string format
        value = str(value)

        #Check to see if value contains any commas
        if ',' in value:
            #Replace all double quotes with double-double quotes
            value.replace('\"', '\"\"')

            #Surround all commas with double quotes
            value.replace(',', '\",\"')

            #Surround value with double quotes
            value = '\"' + value + '\"' 

        file.write(value)
        file.write(',')
    
    #Move to a new line
    file.write('\n')
    
def build_headers():
    """
    Gives the headers for the metadata as an ordered list of strings

    Returns
    -------
    headers : str[]
        A list of the headers/names for column entries
    """

    #TODO: Add frame rate, cadence + start & end times of subject

    headers = []

    headers.append("#file_name")
    headers.append("#fits_names")
    headers.append("#frame_per_sub")
    headers.append("#event_db_id")
    headers.append("#sol_standard")
    headers.append("#visual_type")
    headers.append("#framerate")
    headers.append("#cadence")
    headers.append("#start_time")
    headers.append("#end_time")
    headers.append("#im_ll_x")
    headers.append("#im_ll_y")
    headers.append("#im_ur_x")
    headers.append("#im_ur_y")
    headers.append("#width")
    headers.append("#height")
    headers.append("#naxis1")
    headers.append("#naxis2")
    headers.append("#cunit1")
    headers.append("#cunit2")
    headers.append("#crval1")
    headers.append("#crval2")
    headers.append("#cdelt1")
    headers.append("#cdelt2")
    headers.append("#crpix1")
    headers.append("#crpix2")
    headers.append("#crota2")
    headers.append("#stddev_crpix1")
    headers.append("#stddev_crpix2")
    headers.append("#stddev_crota2")

    return headers

#TODO: Add information to '?'s in comments
def build_row(subject, fps, cadence):
    """
    Creates an individual row for one subject
    Arguments must allow us to know start & end frames of video that this row is attached to

    Parameters
    ----------
    subject : dict
        A dictionary containing information on the subject for this row
        Should contain at least:
            sol_standard : the name of the event this subject comes from
            images : a list of the images used to make the subject
            movie : the name of the movie created for the subject
    fps : int
        The frames per second used to create the subject
    cadence : int
        The cadence at which .fts cutouts were obtained from AIA
        Should be a multiple of 12
    
    Returns
    -------
    row : str[]
        A list of the entries that make up a single row
    """
    #List of ordered column values
    row = []

    #Name of .mp4 file
    movie_name = subject['movie'].split('/')[-1]
    row.append(movie_name)

    #List of the .fts file names used to make the subject
    fits_names = [name[:name.rfind('_')] + '_.fts' for name in subject['images']]
    row.append(fits_names)

    #Find Fits_Files with matching names of the subject's intended .fts files
    fits = Fits_File.select().where(Fits_File.file_name.in_(fits_names))

    #Find the pngs files in the database with matching names to the subject images
    pngs = Visual_File.select().where(Visual_File.file_name.in_(subject['images']))

    #Number of frames in each individual video
    frames_per_sub = len(subject['images'])
    row.append(frames_per_sub)

    #HEK database id for the event
    event_db_id = fits[0].event_id
    row.append(event_db_id)
    
    #event.sol_standard for event associated with this row
    row.append(subject['sol_standard'])

    #Type of media
    visual_type = "video"
    row.append(visual_type)

    #Frame rate
    row.append(fps)

    #Cadence
    row.append(cadence)

    #Start time of the subject
    start_time = str(fits[0].image_time)
    row.append(start_time)

    #End time of the subject
    end_time = str(fits[-1].image_time)
    row.append(end_time)

    #x-value of lower-left corner of image. What is the coordinate system - degrees on solar disk?
    im_ll_x = pngs[0].im_ll_x
    row.append(im_ll_x)

    #y-value of lower-left corner of image. What is the coordinate system?
    im_ll_y = pngs[0].im_ll_y
    row.append(im_ll_y)

    #x-value of upper-right corner of image. What is the coordinate system?
    im_ur_x = pngs[0].im_ur_x
    row.append(im_ur_x)

    #y-value of upper-right corner of image. What is the coordinate system?
    im_ur_y = pngs[0].im_ur_y
    row.append(im_ur_y)

    #Width of image in pixels
    width = pngs[0].width
    row.append(width)

    #Height of image in pixels
    height = pngs[0].height
    row.append(height)
    
    #Data from the fits headers
    fits_headers = [file.get_header_as_dict() for file in fits]
    fits_header = fits_headers[0]

    #Pixels along axis 1
    naxis1 = fits_header['naxis1'];
    row.append(naxis1)

    #Pixels along axis 2
    naxis2 = fits_header['naxis2'];
    row.append(naxis2)

    #Units of the coordinate increments along naxis1 e.g. arcsec
    cunit1 = fits_header['cunit1'];
    row.append(cunit1)

    #Units of the coordinate increments along naxis2 e.g. arcsec
    cunit2 = fits_header['cunit2'];
    row.append(cunit2)

    #Coordinate value at reference point on naxis1
    crval1 = fits_header['crval1'];
    row.append(crval1)

    #Coordinate value at reference point on naxis2
    crval2 = fits_header['crval2'];
    row.append(crval2)

    #Spatial scale of pixels for naxis1, i.e. coordinate increment at reference point
    cdelt1 = fits_header['cdelt1'];
    row.append(cdelt1)

    #Spatial scale of pixels for naxis2, i.e. coordinate increment at reference point
    cdelt2 = fits_header['cdelt2'];
    row.append(cdelt2)

    #Pixel coordinate at reference point naxis1 (median value)
    crpix1_vals = [float(header['crpix1']) for header in fits_headers]
    crpix1 = numpy.median(crpix1_vals)
    row.append(crpix1)

    #Pixel coordinate at reference point (median value)
    crpix2_vals = [float(header['crpix2']) for header in fits_headers]
    crpix2 = numpy.median(crpix2_vals)
    row.append(crpix2)

    #Rotation of the hoizontal and veritcal axes in degrees (median value)
    crota2_vals = [float(header['crota2']) for header in fits_headers]
    crota2 = numpy.median(crota2_vals)
    row.append(crota2)

    #Standard deviations on the last 3 values
    stddev_crpix1 = numpy.std(crpix1_vals)
    row.append(stddev_crpix1)

    stddev_crpix2 = numpy.std(crpix2_vals)
    row.append(stddev_crpix2)

    stddev_crota2 = numpy.std(crota2_vals)
    row.append(stddev_crota2)

    return row

def print_help():
    print(
        'Usage of arguments:\n'
        'Variables:\n'
        '\t-i <date>\n'
        '\t\tFormat as one of: YYYY-MM-DD, YYYY-MM, or YYYY\n'
        '\t-f <frames per second>\tDefault: 10\n'
        '\t-c <time between frames>\tDefault: 24\n'
        '\t\tNote that changing the cadence may require a new database, as .fts files cannot be overwritten\n'
        '\t-d <dpi>\tDefault: 150\n'
        '\t-a <frames per subject>\tDefault: 50\n'
        '\t-b <overlapping frames between subjects>\tDefault: 5\n'
        'Toggles:\n'
        '\t-o Allows all pre-existing files to be overwritten\n'
        '\t-v Skips regenerating fits files and moves straight to making images\n'
        '\t-m Skips regenerating image and fits files and moves straight to making videos\n'
        '\t-n Skips generating metadata output\n'
        '\t-s <max video size in bytes>\tDefault: 1000*2^10 = 1000 Kilobytes'
    )

if __name__ == '__main__':
    event_date = '' #Path to image directory from current working directory
    
    #Default values for optional inputs
    cadence = 24 #Time interval between fits cutouts in seconds. AIA data works best when this number is a multiple of 12
    fps = 10 #Frames per second of the created videos
    dpi = 150 #Changes the resolution of the images generated - higher dpi means higher resolution
    subject_frames = 50 #Defaults as 20 minute subjects | 50 (frames) * 24s (cadence) = 1200s = 20min
    subject_overlap = 5 #Defaults as 2 minutes of overlap | 5 (frames) * 24s (cadence) = 120s = 2min
    max_size = 2 ** 10 * 1000 #Defaults to max video size being 1000*2^10 bytes = 1000 Kilobytes

    try: #Handles all of the arguments
        opts, args = getopt.getopt(sys.argv[1:], 'i:f:c:od:va:b:mns:')
        for opt, arg in opts:
            if opt=='-i':
                event_date = arg
            elif opt=='-f':
                fps = float(arg)
            elif opt=='-c':
                cadence = int(arg)
            elif opt=='-o':
                overwrite = True
            elif opt=='-d':
                dpi = int(arg)
            elif opt=='-v':
                visuals_only = True
            elif opt=='-a':
                subject_frames = int(arg)
            elif opt=='-b':
                subject_overlap = int(arg)
            elif opt=='-m':
                videos_only = True
            elif opt=='-n':
                skip_metadata = True
            elif opt=='-s':
                max_size = int(arg)
            else:
                print_help()
        
        if event_date != '' and len(event_date.split('-')[0]) == 4: #Checks to make sure that at least a year has been provided
            print('Looking for events which occured during:\t' + event_date)
        else:
            print('No event input, need to provide dates wanted.')
            print('Specify days using argument: -i <date>')
            print('Format: date = YYYY-MM-DD, YYYY-MM, or YYYY')
            sys.exit(1)
    
    #If any expected or unexpected errors occur, run these lines
    except getopt.GetoptError:
        print('Argument error.')
        print_help()
        sys.exit(1)
    except Exception as e:
        print(e)
        print('Unknown error occured')
        sys.exit(1)

    #Variable for storing the locations of fits files (if they exist)
    fits_folders = []

    #Make sure required directories exist
    check_directory(fits_folder)
    check_directory(pngs_folder)
    check_directory(movie_folder)
    check_directory(meta_folder)

    #Find all pre-existing fits files
    print("Collecting locations of folders containing .fts files:")
    for folder in os.listdir(fits_folder):
        if os.path.isdir(fits_folder + '/' + folder) and folder.startswith('SOL' + event_date):
            print(folder)
            fits_folders.append(folder)
    
    #If we are interested in generating fits files
    if not (visuals_only or videos_only):
        #Create new folders
        print("Generating new .fits files...")
        make_fits(event_date, fits_folders, cadence=cadence)
    
    #If we have skipped generating new .fts files, but have not found any old files
    elif not fits_folders:
        print("No .fts files found. Please regenerate these files before building images/videos.")
        sys.exit(1)

    #Find all locations of all the image files
    print("Collecting new locations of folders containing .png files:")
    png_folders = []
    for folder in os.listdir(pngs_folder):
        if os.path.isdir(pngs_folder + '/' + folder) and folder.startswith('SOL' + event_date):
            print(folder)
            png_folders.append(folder)

    #If we are interested in generating new images
    if not videos_only:
        #If we want to overwrite existing files and there are files to do be overwritten
        if overwrite:
            #Visual_Files do not need to be purged from the database, they can simply be overwritten
            #Remove old image folders and their contents
            print("Removing old image folders...")
            for folder in png_folders:
                os.system("rm -r " + pngs_folder + '/' + folder)
            print("Folders removed")

            #Reset the png_folders list to reflect new folder locations
            png_folders = []
        
        #Regenerate images
        print("Generating new .png images...")
        make_frames(event_date, png_folders, cadence=cadence, dpi=dpi, overwrite=overwrite)

    #If we have skipped generating new image files, but have not found any old files
    elif not png_folders:
        print("No image files found. Please regenerate these files before building videos.")
        sys.exit(1)

    #Make subjects from given dates
    print("Generating new .mp4 videos...")
    subjects = make_subjects(event_date, subject_frames, subject_overlap, fps=fps, overwrite=overwrite, max_size=max_size)

    #Make sure we are not skipping metadata creation
    if not skip_metadata:
        #Make zooniverse metadata from given subjects
        print("Creating new metadata file in " + meta_folder + "/SOL" + event_date + "/ ...")
        make_metadata(event_date, subjects, fps, cadence, overwrite=overwrite) #meta.csv
