import io
import os
import subprocess
import sys

import PIL.Image as Im
import pyocr
import pyocr.builders
from PIL import Image as Im
from pyocr import tesseract as tool
from wand.image import Image

VALIDITY = [".jpg",".gif",".png",".tga",".tif",".bmp"]

FNULL = open(os.devnull, 'w') #Open file in write mode to The file path of the null device. For example: '/dev/null' 

path = ""

class rename(object):
    
    def __init__(self, path):
        
        ocr_language = 'eng'
        
        path = path
        
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        self.tool = tools[0]
        print("OCR tool: %s" % self.tool)

        try:
            langs = self.tool.get_available_languages()
            self.lang = langs[0]
            if ocr_language in langs:
                self.lang = ocr_language
            print("OCR selected language: %s (available: %s)" % (self.lang.upper(), ", ".join(langs)))
        except Exception as e:
            print("{}".format(e))
    
    def create_directory(self, path):
        if not os.path.exists(path): #No path
	        os.makedirs(path) #Create path
    
    def get_rotation_info(self, filename):
        arguments = ' %s - -psm 0'
        filename = "'" + filename + "'" #Needed as filename need to be in quotes having spaces which is not accepted direct in  subprocess
        # /to/dir = '/to/dir'
        stdoutdata = subprocess.getoutput('tesseract' + arguments % filename)
        degrees = None

        for line in stdoutdata.splitlines():
            print(line)
            info = 'Orientation in degrees: '
            if info in line:
                degrees = -float(line.replace(info, '').strip())
        return degrees

    def fix_dpi_and_rotation(self, filename, degrees, ext):
        im1 = Im.open(filename)
        print('Fixing rotation %.2f in %s...' % (degrees, filename))
        im1.rotate(degrees).save(filename)

    def savefile(self,initial, txt, directory_path):
        
        prompt = " [y/n]: "
        
        sys.stdout.write('Save the OCR in /OCR-text/ ? ' + prompt)
        choice = input().lower().strip()
        if choice[0] == 'y':
            #return True
            if (bool(os.path.exists(directory_path)) == False): #No directory created
                self.create_directory(directory_path) #function to create directory
            fw = open(directory_path + "/" + initial + ".txt" , "w+")
            fw.write(txt)
            fw.close()
        if choice[0] == 'n':
            #return False
            sys.stdout.write("Not saving the OCR in txt format \n \n")
        else:
            sys.stdout.write("Please respond with 'y' or 'n': \n")
        
    def main(self, path):

        directory_path = path + '/OCR-text/' #Create text_conversion folder
        count = 0
        other_files = 0

        for f in os.listdir(path): #Return list of files in path directory

            ext = os.path.splitext(f)[1] #Split the pathname path into a pair i.e take .png/ .jpg etc

            if ext.lower() not in VALIDITY: #Convert to lowercase and check in validity list          
                other_files += 1 #Increment if other than validity extension found
                #sys.stdout.write("Extension other than image is not supported. \n")
                continue

            else:

                count += 1

                image_file_name = path + '/' + f #Full /dir/path/filename.extension
                filename = os.path.splitext(f)[0] #Filename without extension
                filename = ''.join(e for e in filename if e.isalnum() or e == '-') #Join string of filename if it contains alphanumeric characters or -
                
                '''
                text_file_path = directory_path + filename #Join dir_path with file_name
                if self.tool.can_detect_orientation():
                    orientation = self.tool.detect_orientation(image_file_name, lang=self.lang)
                    angle = orientation["angle"]
                    if angle != 0:
                        image_file_name.rotate(orientation["angle"])
                print("Orientation: {}".format(orientation))
                '''
                
                degrees = self.get_rotation_info(image_file_name)
                print(degrees)
                if degrees:
                    self.fix_dpi_and_rotation(image_file_name, degrees, ext)

                txt = tool.image_to_string(
                    Im.open(image_file_name), lang=self.lang,
                    builder=pyocr.builders.TextBuilder()
                )
                
                #txt = txt.split()[:5]
                initial = txt.replace('\a', ' ').replace('\b', ' ').replace('\f', ' ').replace('\n',' ').replace('\r', '').replace('\t',' ').replace('\v',' ') #.replace(' ','_') #.replace('.','_') #Replace \n and \t with space
                initial = initial[:60] #Take 1st 100 words
                print('Filename:' + initial + '\n')

                os.chmod(path, 0o777)
                os.rename(image_file_name, initial + ext)

                self.savefile(initial, txt, directory_path)

                print(str(count) + (" file" if count == 1 else " files") + " processed")

        if count + other_files == 0:
            print("No files found") #No files found
        else :
            print(str(count) + " / " + str(count + other_files) + " files converted")

def ocr_rename_main(path):
    s = rename(path)
    s.main(path) # Def main to path