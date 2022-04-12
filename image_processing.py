from contextlib2 import nullcontext
import pandas as pd
import os
import sys
from PIL import Image, ImageOps, ExifTags, ImageDraw, ImageFont

# HEIC files - convert them to jpg format with EXIF data enabled
			
def get_font(picture, caption):
    fontsize = 10  # starting font size
    img_fraction = 0.25 # portion of image width you want text width to be
    font = ImageFont.truetype("arial.ttf", fontsize)
    while font.getsize(caption)[0] < img_fraction*picture.size[0]: # Loop to ensure relative size of the font with respective to image
    # https://stackoverflow.com/questions/4902198/pil-how-to-scale-text-size-in-relation-to-the-size-of-the-image
         # iterate until the text size is just larger than the criteria
         fontsize += 5
         font = ImageFont.truetype("arial.ttf", fontsize)
    # Add water mark ---------------------------
    return font

# finds current working dir
setwd = os.chdir('E:\Coursera Material\Python For Everyone\Botany\static\\flora_title\TBD\Image_processing')
outpath = 'E:\Coursera Material\Python For Everyone\Botany\static\\flora_title\TBD\Processed_images'
formats = ('.jpg', '.jpeg')
Image_Library = pd.DataFrame(columns = ['File_Name', 'Family', 'Botanical_name','Record_count', 'Attribute', 
                                        'Photo_DateTime','Contributor','Caption'])
# looping through all the files
# in a current directory
for file in os.listdir(setwd):	
   	#If the file format is JPG or JPEG
       if os.path.splitext(file)[1].lower() in formats:
           filepath = os.path.join(os.getcwd(),file)
           picture = Image.open(filepath)
           
           # Add watermark-------------------
           pos=(50,90)
           draw_caption = ImageDraw.Draw(picture)
           black = (255, 255, 255)
           caption = 'mandarsj11@gmail.com'
           
            
           try: # true if exif is not empty
                #---------------- Prevent image orientation - https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
                exif=dict(picture.getexif().items())
                image_orientation = exif[274] # meaning of various exif tags - https://www.exiv2.org/tags.html
                #----image_orientation meaning - https://sirv.com/help/articles/rotate-photos-to-be-upright/
                if image_orientation in (2,'2'):
                     picture=picture.transpose(Image.FLIP_LEFT_RIGHT)
                elif image_orientation in (3,'3'):
                     picture=picture.transpose(Image.ROTATE_180)
                elif image_orientation in (4,'4'):
                     picture=picture.transpose(Image.FLIP_TOP_BOTTOM)
                elif image_orientation in (5,'5'):
                     picture=picture.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
                elif image_orientation in (6,'6'):
                     picture=picture.transpose(Image.ROTATE_270)
                elif image_orientation in (7,'7'):
                     rpicture=picture.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
                elif image_orientation in (8,'8'):
                     picture=picture.transpose(Image.ROTATE_90)        
                try:
                datetime = pd.to_datetime(exif[36867], format='%Y:%m:%d %H:%M:%S')
                    print("The date and time when the original image data was generated: ",file)
                except KeyError:
                    datetime = pd.to_datetime(exif[306], format='%Y:%m:%d %H:%M:%S')
                    print("The date and time the file was changed: ",file)

                #---------------------
                picture.thumbnail((1000, 1000), Image.ANTIALIAS)
                draw_caption = ImageDraw.Draw(picture)
                draw_caption.text(pos, caption, fill=black, font=get_font(picture, caption)) 
                print("image has exif data - ",file, image_orientation)
                picture.save(os.path.join(outpath, file), #os.path.join((os.path.splitext(file)[0]+"_Comp.jpg")
                             "JPEG",
                             optimize = True,
             				 quality = 95)
                
           except KeyError:
                picture.thumbnail((1000, 1000), Image.ANTIALIAS)
                draw_caption = ImageDraw.Draw(picture)
                draw_caption.text(pos, caption, fill=black, font=get_font(picture, caption))
                print("image has no exif data - ",file)
                datetime = ''
                picture.save(os.path.join(outpath, file), #os.path.join((os.path.splitext(file)[0]+"_Comp.jpg")
                             "JPEG",
                             optimize = True,
             				 quality = 95)
           
           file_split = file.split('_')
           Image_Library = Image_Library.append({
                                        'File_Name':file,
                                        'Family':file_split[0],
                                        'Botanical_name':file_split[1],
                                        'Record_count':file_split[2],
                                        'Attribute':file_split[3],
                                        'Photo_DateTime':datetime,
                                        'Contributor': 'Mandar Joshi',
                                        'Caption':''
                                        },ignore_index=True)
           
writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter',datetime_format='dd-mmm-yyyy hh:mm AM/PM')
Image_Library.to_excel(writer)
writer.save()
print('DataFrame is written successfully to Excel File.')
# --- getting list of all files in a directory
"""
from os import listdir
from os.path import isfile, join
mypath = 'E:\Coursera Material\Python For Everyone\Botany\static\\flora_title\TBD\Processed_images'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
onlyfilesdf = pd.DataFrame(onlyfiles, columns =['File_name'], dtype = str)

#onlyfilesdf['File_name1'] = onlyfilesdf['File_name']

onlyfilesdf[['Family', 'Name','Record count','Attribute','Photo DataTime']] = onlyfilesdf['File_name'].str.split('_', expand=True)
#onlyfilesdf.drop(['crap'], axis = 1, inplace = True)

"""
