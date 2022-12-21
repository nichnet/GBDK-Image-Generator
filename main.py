import sys
import os
import example_data
import gbtdimg

import math
import constants
from PIL import Image


def generateQuadrantFromPixels(pixels):
    pass

def getColorIndexFromPixelColor(color):
    return [key for key, value in constants.PALETTE.items() if value == color][0]

def importImage(path):
    img = Image.open(path)
    imgWidth = img.size[0]
    imgHeight = img.size[1]
    print(f'Importing image: "{path}", size: {imgWidth}x{imgHeight}')

    #TODO check that size is allowed from size obj.

    quadrantHorizontalCnt = int(imgWidth / constants.QUAD_SIZE)
    quadrantVerticalCnt = int(imgHeight / constants.QUAD_SIZE)
    
    print(f'horiz quads: {quadrantHorizontalCnt}, vert quads: {quadrantVerticalCnt}')
    pixels = img.load()    

    out = []

    for qy in range(0, quadrantVerticalCnt, 1):
        for qx in range(0, quadrantHorizontalCnt, 1): 
            #for each quadrant
            quadIndex = qy + qx


            for y in range(0,8):
                for x in range(0,8): 
                    #for each pixel in the quadrant
                    px = (qx * constants.QUAD_SIZE) + x
                    py = (qy * constants.QUAD_SIZE) + y
                 #   px = qx + int(quadIndex % 8) + x
                 #   py = qy + int(quadIndex / 8) + y   
                    color = pixels[px, py][0:3] #only R,G,B, not A
                    colorIndex = getColorIndexFromPixelColor(color)
                    out.append(colorIndex)

    return out

#    for j in range(len(quadrant)):
        #every quadrant is made of 64 pixels (8x8)
        #get the pixel x and y
 

#    quadrantHorizontalCnt = int(imgWidth / constants.QUAD_SIZE)


#    qx = int(i % quadrantHorizontalCnt) * constants.QUAD_SIZE
#    qy = int(i / quadrantHorizontalCnt) * constants.QUAD_SIZE
    
 #   print(quadrantHorizontalCnt, imgWidth, imgHeight)#, qx, qy)

#    quadrant = quadrants[i]
#
#    #iterate each pixel in the quadrant
#   
#
    
    for y in range(imgHeight, 8):
        for x in range(0, 8):  
            colorIndex = getColorIndexFromPixelColor(pixels[x, y])
            out.append(colorIndex)

    return out

def twoBytesToTwoHex(bytes):
    h1 = 0
    h2 = 0

    for i in range(len(bytes)):
        b1 = bytes[i] & 1
        b2 = bytes[i] >> 1 & 1

        h1 <<= 1
        h1 |= b1


        h2 <<= 1
        h2 |= b2

    #using format instead of hex because we want to pad the 0x00 instead of 0x0
    return [format(h1, '#04x'), format(h2,'#04x')]

def decompileImageFile(path):
    colors = importImage(path)

    out = []
    for i in range(0, len(colors), 8):
        hexes = twoBytesToTwoHex(colors[i:i+8])
        out.append(hexes[0])
        out.append(hexes[1])
    
    return out

def sortQuadrantsForDecompile(quadrants):
    quadrantCnt = len(quadrants)
    unordered = []


    if quadrantCnt == 1 or quadrantCnt == 2:
        # 8x8       8x16
        # 0         0
        #           1
        unordered = quadrants #already sorted
    elif quadrantCnt == 4:
        # 16x16
        # 0  2 > 0  1
        # 1  3 > 2  3
        unordered = [
            quadrants[0],
            quadrants[2],
            quadrants[1],
            quadrants[3]
        ]
    elif quadrantCnt == 16:
        # 32x32
        # 0  2   8  10 >  0  1  2  3
        # 1  3   9  11 >  4  5  6  7 
        # 4  6  12  14 >  8  9 10 11
        # 5  7  13  15 > 12 13 14 15
        unordered = [
            #top left
            quadrants[0],
            quadrants[4],
            quadrants[1],
            quadrants[5],
            #bottom left
            quadrants[8],
            quadrants[12],
            quadrants[9],
            quadrants[13],
            #top right
            quadrants[2],
            quadrants[6],
            quadrants[3],
            quadrants[7],
            #bottom right
            quadrants[10],
            quadrants[14],
            quadrants[11],
            quadrants[15]
        ]

    return unordered



def generateOutFileInfo(width, height): #TODO other info here.. unneccessary for now.
    return '\n'.join(
        [
            'Info:',
            'Form                 : All tiles as one unit.',
            'Format               : Gameboy 4 color.',
            'Compression          : None.',
            'Counter              : None.', 
            f'Tile size            : {width} x {height}',
            'Tiles                : 0 to 0',
            '',
            'Palette colors       : None.',
            'SGB Palette          : None.',
            'CGB Palette          : None.',
            '',
            'Convert to metatiles : No.'
        ]
    )


def generateCHeaderContent(label, width, height):
    return '\n'.join(
        [
            '/*',
            '',
            f'{label}.H'
            '',
            'Include File.',
            '',
            generateOutFileInfo(width, height),
            '*/',
            '',
            '/* Bank of tiles. */',
            f'#define {label}Bank 0',
            f'extern unsigned char {label}[];'
            '',
            f'/* End of {label}.H */',
        ]
    )


def generateCSourceContent(label, data, width, height):
    dataStr = ''

    for quad in data:
        for i in range(0, len(quad), 8):
            dataStr += f'{",".join(quad[i:i+8])},\n'
#            dataStr += f'{quad[i]}, {quad[i+1]}, \n'

    return '\n'.join(
        [
            '/*',
            '',
            f'{label}.C'
            '',
            'Tile Source File.',
            '',
            generateOutFileInfo(width, height),
            '*/',
            '',
            '/* Start of tile array. */',
            f'unsigned char {label}[] = ',
            '{',
            dataStr,
            '};'
            '',
            f'/* End of {label}.C */',
            
        ]
    )


def exportCOutFIle(label, data):
    sourceFile = open(f'{constants.EXPORT_FOLDER}/{label}.c', 'w')
    sourceFile.write(generateCSourceContent(label, data, 8, 8))
    sourceFile.close()

    headerFile = open(f'{constants.EXPORT_FOLDER}/{label}.h', 'w')
    headerFile.write(generateCHeaderContent(label, 8, 8))
    headerFile.close()

if __name__ == "__main__":
    args = sys.argv
    mode = args[1]
    path = args[2]

    name = ''
    if mode == '-d':
        data = None
        if path in ['t88', 't816', 't1616', 't3232']: 
            if path == 't88':
                data = example_data.t8_8["data"]
                name = example_data.t8_8["name"]
            elif path == 't816':
                data = example_data.t8_16["data"]
                name = example_data.t8_16["name"]
            elif path == 't1616':
                data = example_data.t16_16["data"]
                name = example_data.t16_16["name"]
            elif path == 't3232':
                data = example_data.t32_32["data"]
                name = example_data.t32_32["name"]
        else:
            data = a
            name = 'Export'
            if len(args) == 5:
                name =  args[3]
                fileName = args[4]
                #TODO get data from file next arg is file..
            elif len(args) > 5:
                name =  args[3]
                data = args[4:len(args)-1]
    
                print(data)
        if data != None:
            print(f'Decoding data ({name}) and exporting as file: {constants.EXPORT_FOLDER}/{name}.png') 
            quads = gbtdimg.generateQuadrants(data)
            ordered = gbtdimg.sortQuadrants(quads)
            gbtdimg.exportImage(name, ordered)
        else:
            print('No data to decode.') 

    elif mode == '-e':
        name = args[3]
        print(f'Decoding example image ({name})')

        if path and name:
            arr = decompileImageFile(path)


            out = []


            for i in range(0, len(arr), 16):
                out.append(arr[i:i+16])

            aa = sortQuadrantsForDecompile(out)


            exportCOutFIle(name, aa)
            print(f'Exporting out files: {constants.EXPORT_FOLDER}/{name}.c & {constants.EXPORT_FOLDER}/{name}.h')


            


