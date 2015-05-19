#------------------------------------------------------------------------------------------------------------
#
# Export Sprite Sheet - GIMP plug-in that build a sprite sheet and 
# a Plist Mac xml file type from layers of current image. 
# The sprite Sheet generated is in png format. Alpha version.
#
# Copyright (C) 2015  Angelo Amalfitano (angelo.amalf@gmail.com)
#
# 
#
# Export Sprite Sheet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Export Sprite Sheet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Export Sprite Sheet.  If not, see <http://www.gnu.org/licenses/>.
#
# Export Sprite Sheet make use of external software Sprite Sheet Packer (sspack)
# Copyright (c) 2009 Nick Gravelyn (nick@gravelyn.com), Markus Ewald (cygon@nuclex.org)
# http://spritesheetpacker.codeplex.com/ under MIT license. 
#
#
# Export Sprite Sheet 
#
# Installation
# 
# Copy all file MyS.py and sspack.exe in <UserDir>/.gimpXX/plug-ins directory
#
# Use:
#  To export layer of image as Plist file goto in menu File-> Export Sprite Sheet..
#  set the parameter Padding, Max sheet width, max sheet height etc.
#  Set the directory and the name of file press Save and GIMP produce two file 
#  1) A png file 
#  2) A file Plist.
#------------------------------------------------------------------------------------------------------------

'''
Created on 05/may/2015
@author: Angelo
'''
#!/usr/bin/env python

# GIMP Python plug-in template.

import gtk 
import os
from os.path import expanduser # manage user home dir
import subprocess
import string
from gimpfu import *
import time
import sys
from plistlib import writePlist 
#from sys import path

#sys.stderr = open( 'C:\\Users\\Angelo\\Desktop\\Blender3D\\gimp\\gimpstderr.txt', 'w')
#sys.stdout = open( 'C:\\Users\\Angelo\\Desktop\\Blender3D\gimp\\gimpstdout.txt', 'w')
 
# Get home dir on all os with function  expanduser("~")   /tmp temporary directory to store temp file.
#path=expanduser("~")+"\\tmp\\" 
path="C:/tmp/"
dirHomeGimp=".gimp-"
dirPlugInGimp="plug-ins"
# Path to directory of Sprite Sheet Packer.
pathToSSpack="C:/Users/Angelo/Desktop/SpriteSheetPacker/"
# global not initialized
dirSeparetor="/"
fileImagetype=".png"
fileMaptype=".txt" 
filePlisttype=".plist"

# Dictionary key PLIST file 
Frames="frames"
CurrentFrame="frame"
Offset="offset"
Rotated="rotated"
SourceColorRect="sourceColorRect"
SourceSize="sourceSize"
MetaData="metadata"
Format="format"
RealTextureFileName="realTextureFileName"
Size="size"
SmartUpdate="smartupdate"
TextureFileName="textureFileName"
# End var. for Dictionary 

gListfileImage="ListFileImage.txt"

def getFileNameList(listlayer):
    """   
        get a list of image file to create.
        :param a list of layer of current image editing.
        :return a list of file name to create.
    """
    filesToCreate=[]
    for nameLayer in listlayer:
        filesToCreate.append(nameLayer.name.decode("utf-8")+fileImagetype)
    
    return filesToCreate

def getLayerGimp(img):
    """ this function return the set of layer of image visible 
        :param img The current image editing in Gimp.
    """
    
    # crate a blank list of visible layer in image img.
    layers=[]
    
    for l in img.layers:
        if (l.visible): 
            layers.append(l)
        
    return layers

def createPNGImgFile(img,layer,listNameFile): #,mapname):
    
    """
        this function create a set of png file. Each file is a layer of image in gimp. 
        :param img the image editing in GIMP.
        :param layer the layer of image editing.
        :param listNameFile a list of file to save in png format.
        :return None on error else File txt of Image list on success 
    """  
    global gListfileImage
    i=0
    name_fileListfile=path+ gListfileImage  # "ListFileImage.txt"
    fileOfListImageName= open(name_fileListfile, 'w')
    str_fullList=""
    for l in layer:
        if __debug__ :
            print "layer name =",l,"file create =",listNameFile[i]
            # path is global variable  of path (path="C:\\tmp\\") where we save the file of layers. 
            print "File to save =",path+listNameFile[i]
        str_fullList+= path+listNameFile[i]+"\n"    
        fileOfListImageName.write(path+listNameFile[i]+"\n")
        try:
            #  the parameter explicitly assigned go  to the end of parameter not explicitly assigned.
            pdb.file_png_save_defaults(img, l, path+listNameFile[i],path+listNameFile[i],run_mode=RUN_NONINTERACTIVE)
            i+=1  
        except IOError:
            print "I/O error on create intermediate file *.png "
            fileOfListImageName.close()
            return None
    fileOfListImageName.close() 
       
    return fileOfListImageName

def createSheet(listFile,texname,mapname,sheetMaxW,sheetMaxH,imagePad,power2Tex, squareTex):
    '''
        Create a sprite Sheet call external tool sspack.exe (open tool).
        :param a list of created image file to sheet. 
        :return True on success else False
    '''
    # texname="Pack"
    # mapname="map"
    if __debug__ : # equivalen "preprocessor" directive C/C++ 
        print "Create Sheet procedure"
        print "creating this texture file ",texname
        print "creating this map file ",mapname
        print " Directory where files is created :",path
        print "param image= /image :",os.path.join(path, texname) + fileImagetype
        print "param_map =  /map   :", os.path.join(path, mapname) + fileMaptype
        print "param_maxw = /mw    :",sheetMaxW
        print "param_maxh = /mh    :",sheetMaxH
        print "param_pad           :",imagePad
        print "param_power2Tex     :",power2Tex
        print "param_squareTex     :",squareTex
        print "imgListFile  /il    :",listFile.name  
           
    # create a full path to sprite sheet packet tool sspacker.exe
    sspack = os.path.join(pathToSSpack, 'sspack.exe')
    print "External exe :",sspack    
    if(os.path.exists(sspack)):
            # this is a list of parameter used from sspack.exe
            param_img = '/image:' + os.path.join(path, texname) + fileImagetype  # the name Sprite sheet file to create
            param_map = '/map:' + os.path.join(path, mapname) + fileMaptype   # A text file for mapping name-> coordinate to sub-image in Sprite Sheet image. 
            param_maxw = '/mw:'+str(sheetMaxW) #default value for  max sheet width size  (sspack.exe)
            param_maxh = '/mh:'+str(sheetMaxH) #default value for max sheet height  for   (sspack.exe)
            param_pad = '/pad:'+str(imagePad)    #default value for pad between sub-image of final Image  (sspack.exe)
            if(power2Tex):
                param_power2Tex ='/pow2'
            else:
                param_power2Tex ="" 
                
            if(squareTex):
                param_squareTex="/sqr"
            else:
                param_power2Tex =""   
            param_imglistFile = '/il:'+listFile.name # name_fileListfile  #file txt with list of files png for create a sprite sheet.
            # end list of parameter used from sspack.exe
            # call to external tool sspacker.exe
#            subprocess.call([sspack, param_img, param_map, param_maxw, param_maxh, param_pad, param_imglistFile],shell=False)
            exe=subprocess.Popen([sspack, param_img, param_map, param_maxw, param_maxh, param_pad, param_power2Tex, param_squareTex, param_imglistFile])
            #print "execute eternal process :",exe.stdout
            #print "execute eternal process error :",exe.stderr
            exe.wait()
            print "execute eternal code exit:",exe.returncode
            return True
    return False

def getOnlyNameFile(nameFile):
    """
        get only the name of file but not the extension es. .png etc.
        :return file name only.
    """
    indexExtension=string.find(nameFile,".")
    if indexExtension==-1:
        indexExtension=len(nameFile)  
       
    #print "rename file=",(pathSheet+dirSeparetor+texname+fileImagetype)," to =",nameFile[:indexExtension]+fileImagetype   
    
    return nameFile[:indexExtension]


def delFileImageSupport(path,listofFileImage):
    """
        delete the set of file png create from layer for the creation of sprite sheet.
        :param path the Path to files to delete.
        :param the list of file to delete.
    """
    for nameImg in listofFileImage:
            os.remove(path+nameImg)
    
    return

def createPListFile(mapname,image):
    """
        Create a xml plist file from sprite sheet image.
        :param mapname the name of file with information about frame of animation.
        :param image the image info of sprite sheet generated
    """
    if __debug__ :
        print "Creating Plist file"
        print "Loading support file in :",path+mapname+fileMaptype  
    mapf=open(path+mapname+fileMaptype, 'r')
    riga=mapf.readline()
    #dictionary PList is a dictionary of tag Plist. The  key of dict. is the key in plist file and the value of dict. is the reporter value in  Plist file.
    # refer at https://docs.python.org/2.7/library/plistlib.html#plistlib.dump and https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man5/plist.5.html 
    dictPList={}
    dictAllFrames={}
    # Invio="\n"
    while len(riga)!=0:
        if __debug__ :
            print "ROW value read from file  =",riga
        val=""
        # dictionary of current frame
        dictFrame={} 
        riga=riga.replace("\n","") 
        listaSplitsubImage=riga.split(" ")
        # extract the key of current frame
        chiave=listaSplitsubImage[0]
        if(len(listaSplitsubImage)<7):      # 6 is the number of token in one row of map file ex. "frame = 0 0 100 100"
                if __debug__ :
                    print "Len of List split :",len(listaSplitsubImage)   
                #build the current tag for frame.
                val+="{"+listaSplitsubImage[2]+","+listaSplitsubImage[3]+"},{"+listaSplitsubImage[4]+","+listaSplitsubImage[5]+"}"
                val="{"+val+"}" #+Invio
                dictFrame[CurrentFrame]=val
                dictFrame[Offset]="{0,0}"
                dictFrame[Rotated]=False
                dictFrame[SourceColorRect]="{{0,0},"+listaSplitsubImage[4]+",{"+listaSplitsubImage[5]+"}}" #+Invio
                dictFrame[SourceSize]="{"+listaSplitsubImage[4]+","+listaSplitsubImage[5]+"}" #+Invio
                if __debug__ :
                    print "dictionary frame :",dictFrame
        else:
            raise NameError,"Error format not recognized."
        # build key-value couple for current frame in dictAllFrames 
        dictAllFrames[chiave]=dictFrame    
        riga=mapf.readline() # next line from file.  
    #End while  
    #close map file     
    mapf.close()
    #Create a meta data dictionary used for build a frames of animation  
    filename=os.path.basename(image.filename)
    if __debug__:
        print "Texture file name :",filename
    dictmeta={}
    dictmeta[Format]=2
    dictmeta[RealTextureFileName]=filename # image.filename get complete path and file name
    dictmeta[Size]="{"+str(image.width)+","+str(image.height)+"}"  #+Invio
    dictmeta[SmartUpdate]="Created with GIMP "+time.strftime("%d/%m/%Y %H:%M:%S") 
    dictmeta[TextureFileName]=filename    # image.filename get complete path and file name
    dictPList[Frames]=dictAllFrames
    dictPList[MetaData]=dictmeta
    # create a plist file with data info in dictPList.
    # mapname is the same name of name of file plist
    writePlist(dictPList, path+mapname+filePlisttype)
    if __debug__ :
        print "End create Plist file"
    return 

#callback function used from gtk.FileChooserDialog
def previewCallBack(filechooser,imgprw):
    filename=filechooser.get_preview_filename()
    try:
        prwBuffer=gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
        imgprw.set_from_pixbuf(prwBuffer)
        have_preview = True
    except:
        have_preview = False
        filechooser.set_preview_widget_active( have_preview)
    filechooser.set_preview_widget_active(have_preview)
    return

#                                MAIN
def do_spriteSheet(img, layer, imagePad,sheetMaxW, sheetMaxH, power2Tex, squareTex):
# Python for change a global variable using:  global my_var.  
    global path,pathToSSpack
    
    # get full GIMP version number ex. 2.8.0
    versionGimp=pdb.gimp_version()
    # get GIMP major number version  ex. 2.8 rfind get the last char "."
    MajorNumber=versionGimp.rfind(".") 
    # get sub-string from 1-st char to char number MajorNumber
    MajorNumberVersGimp=versionGimp[:MajorNumber]
    # build the directory where is install the script with external tool sspack.exe (var pathToSSpack)
    Testpath=expanduser("~")+dirSeparetor+dirHomeGimp+MajorNumberVersGimp+dirSeparetor+dirPlugInGimp
    # stand. error output to file for debug.
    sys.stderr = open( Testpath+'\\gimpstderr.txt', 'w')
    # stand. output to file for debug.
    sys.stdout = open( Testpath+'\\gimpstdout.txt', 'w')
    # set path to sspack.exe
    pathToSSpack=Testpath+dirSeparetor 
    
    print"do_spriteSheet procedure" 
    
    # create an image using gtk lib.
    image= gtk.Image()
    # create a file chooser object using gtk lib class FileChooserDialog.
    chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
    # add callback function "previewCallBack" 
    # the name of connection callback is "update-preview" the parameter pass to callback is image (the image to update for preview).
    chooser.connect("update-preview",previewCallBack,image)
    # ask confirmation for overwrite an exists file.
    chooser.set_do_overwrite_confirmation(True)
    # update the image if necessary in file chooser.
    chooser.set_preview_widget(image)
    # create a filter for select a subset of image.
    fil = gtk.FileFilter()
    fil.set_name("Images")
    fil.add_mime_type("image/png")
    #fil.add_mime_type("image/jpg")
    fil.add_pattern("*.png")
    #fil.add_pattern("*.jpg")
    chooser.add_filter(fil)
    # run the chooser for save the file sprite sheet.
    response=chooser.run()
    if response != gtk.RESPONSE_OK:
            return
        

    NameFileRes=chooser.get_filename() 
    chooser.destroy()

    # duplicate the current image editing in Gimp. 
    imageCopy=pdb.gimp_image_duplicate(img) 
    

    
    pathSheet=os.path.dirname(NameFileRes)
    NameFileRes=os.path.basename(NameFileRes)
    
    print"path sheet:",pathSheet
    print"Name file creating :",NameFileRes
    
   
#     if __debug__ :
#         sys.stderr = open( 'C:\\Users\\Angelo\\Desktop\\Blender3D\\gimp\\gimpstderr.txt', 'w')
#         sys.stdout = open( 'C:\\Users\\Angelo\\Desktop\\Blender3D\gimp\\gimpstdout.txt', 'w')
#       sys.stderr = open( Testpath+'\\gimpstderr.txt', 'w')
#       sys.stdout = open( Testpath+'\\gimpstdout.txt', 'w')

    #Set the current Save directory of file sheet .png e Plist 
    path=pathSheet+dirSeparetor
    
    # get visible layer of image 
    # layersImage is a list of Layer Object defined in gimp.
    layersImage=getLayerGimp(imageCopy)
    
    # get list of file image to create
    listofFileImage=getFileNameList(layersImage)
    
    texname= getOnlyNameFile(NameFileRes)
    mapname= getOnlyNameFile(NameFileRes)
    sheetMaxW=int(sheetMaxW)
    sheetMaxH=int(sheetMaxH)
    imagePad=int(imagePad)
    
    
    if __debug__ :
        print "creating this texture file ",texname
        print "creating this map file ",mapname
    
    # create file image from file list and list of layers
    name_filelistFileimg=createPNGImgFile(imageCopy, layersImage, listofFileImage)
         
    # create a sprite sheet pack with call to external tool sspack        
    createSheet(name_filelistFileimg,texname,mapname,sheetMaxW,sheetMaxH,imagePad,power2Tex, squareTex)
#     indexExtension=string.find(NameFileRes,".")
#     if indexExtension==-1:
#         indexExtension=len(NameFileRes)  
#        
#     print "rename file=",(pathSheet+dirSeparetor+texname+fileImagetype)," to =",NameFileRes[:indexExtension]+fileImagetype    
#     os.rename(pathSheet+dirSeparetor+texname+fileImagetype, NameFileRes[:indexExtension]+fileImagetype)    
    # os.remove("path/to/nomeFile") delete the file in the path specified.
          
    # these print redirected to gimpstdout.txt
    if __debug__ :
        print "file name  =",img.filename
        print "image name =",img.name
        print "layer 0 name =",img.layers[0].name," layer is visible? =",img.layers[0].visible
        print "layers of Image",layersImage
        print "The sheet file is in Dir :",pathSheet
        print "GIMP version : ",pdb.gimp_version() # ex. 2.8.0
        print "Current work directory :",Testpath
    # Load the sprite sheet generated ( a png file).
    imageSheet=pdb.file_png_load(os.path.join(path, texname)+fileImagetype,os.path.join(path, texname)+fileImagetype,run_mode=RUN_NONINTERACTIVE)
    # Finally create a PList file.
    createPListFile(mapname,imageSheet)
    # remove not necessary files: *.png and mapname.txt
    #the set of file png of animation. 
    delFileImageSupport(path,listofFileImage)
    # delete the map file mapname.txt not necessary we need only PList file type
    #os.remove(path+mapname+fileMaptype)
    # delete file support gListfileImage
    #os.remove(path+gListfileImage)
    
    # Set up an undo group, so the operation will be undone in one step.
    #pdb.gimp_undo_push_group_start(img)

    # Do stuff here.
    #pdb.gimp_invert(img.layers[0])

    # Close the undo group.
    #pdb.gimp_undo_push_group_end(img)
    
# this register call is necessary to GIMP.
register(
    proc_name = "python_fu_do_spriteSheet", 
    blurb =     "Make a Sprite sheet from layers generating a sheet png file and a xml Apple plist file format.", # brief description of plug-in
    help =      "This plug-in is in Alpha stage. This using  the external tool sspack.exe Make a Sprite sheet from layers and export the result in xml Apple plist file format.", # Long description of plug-in
    author =    "Angelo Amalfitano",
    copyright = "Angelo Amalfitano",
    date =      "2015",
    imagetypes = "*",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc..  * refers to  all type of image.
    function =  do_spriteSheet,
    menu =      "<Image>/File/Export", #L_ayers to Sheet",  # "<Image>/File/Export"  The menu name and position (in this case the menu is in File menu the voice is:"Export"
    label =     "E_xport Sprite Sheet...", # the label visualize in menu for call the function do_spriteSheet.
    params = [  # parameters to pass to function "do_priteSheet" respect the order between params in register and param in do_spriteSheet
        (PF_IMAGE, "img", "Input image", None),  # first parameter pass to do_spriteSheet procedure.  With PF_IMAGE type of parameter in PythonFU (is the type Image defined in GimpFu). The Image object is bind to img,  the name of parameter in script. The value for parameter img= None means select automatically current image.
        (PF_LAYER, "layer", "Input layer", None),  # second parameter. None select the current selected layer.
#         (PF_DIRNAME, "pathSheet", "Save Directory", os.getcwd()),
#         (PF_STRING, "NameFileRes", "Name of file PNGs", ""),        
        (PF_SPINNER,"imagePad","Image Padding",1,(1,100,1)),
        (PF_SPINNER, "sheetMaxW", "Max Sheet Width:",4096,(1,4096,1)), # third parameter. Parameter from user. 50 is the value propose from system.
        (PF_SPINNER, "sheetMaxH", "Max Sheet Height:",4096,(1,4096,1)),
        (PF_BOOL,"power2Tex","Texture Power of Two:",True),
        (PF_BOOL,"squareTex","Square Texture:",True)
    ], 
    results = [] # the result of function if any
    #other parameters of register(): domain, on_query, on_run
)



main()
