from PIL import Image
import constants
import os

def generateQuadrants(arr):
    quadrants = []

    for i in range(0, len(arr), 16): 
        quadrants.append(decodeQuadrant(arr[i:i+16]))

    return quadrants

def getColorPaletteIndexFromBits(b1, b2):
    #0 0 W 000000000 0
    #1 0 G 000000010 1
    #0 1 D 000000001 2
    #1 1 B 000000011 3

    # Bitshift the bits of b2 to the left by 1. (00000001 << 1 = 00000010)
    # Next, bitwise 'or' the new value of b2 with b1 (00000010 | 00000001 = 00000011)
    # 
    #this will result in 4 unique outputs for each color index.
    return b2 << 1 | b1

def decodeQuadrant(arr):
    out = []

    for i in range(0, len(arr), 2):
        #each hex value represents 8 bits (and 8 pixels)
        #get each byte and the byte after it
        byte = format(arr[i], '08b') 
        nextByte = format(arr[i+1], '08b') 
        #for each bit in the byte, get the color index from it
        #plus the bit in the same offset of the next byte. 
        for x in range(len(byte)): #always going to be 8 (8 bits in hex (byte) and thus 8 pixels in the quad)..
            p1 = int(byte[x])
            p2 = int(nextByte[x])
            out.append(getColorPaletteIndexFromBits(p1, p2))

    return out

def sortQuadrants(quadrants): 
    #you'd expect them to be sorted like:
    #  0   1   2   3
    #  4   5   6   7
    #  8   9  10  11
    # 12  13  14  15
    #
    #Every 4 quads seems to be sorted vertically then horizontally.
    #but every 2 x 4 quads are organized horizontally...
    #to draw the image, they should be sorted like below. 
    #(unless youve got a better optimization, so that we can skip this step)

    quadrantCnt = len(quadrants)
    ordered = []

    print(quadrantCnt)
    if quadrantCnt == 1 or quadrantCnt == 2:
        # 8x8       8x16
        # 0         0
        #           1
        ordered = quadrants #already sorted
    elif quadrantCnt == 4:
        # 16x16
        # 0  2 
        # 1  3
        ordered = [
            quadrants[0],
            quadrants[2],
            quadrants[1],
            quadrants[3]
        ]
    elif quadrantCnt == 16:
        # 32x32
        # 0  2   8  10
        # 1  3   9  11
        # 4  6  12  14
        # 5  7  13  15
        ordered = [
            quadrants[0],
            quadrants[2],
            quadrants[8],
            quadrants[10],
            quadrants[1],
            quadrants[3],
            quadrants[9],
            quadrants[11],
            quadrants[4],
            quadrants[6],
            quadrants[12],
            quadrants[14],
            quadrants[5],
            quadrants[7],
            quadrants[13],
            quadrants[15]
        ]

    return ordered

def exportImage(name, quadrants):
    quadrantCnt = len(quadrants)
    try:
        imgWidth  = constants.SPRITE_SIZES[quadrantCnt][0]
        imgHeight = constants.SPRITE_SIZES[quadrantCnt][1]
    except:
        print(f'Size not supported. Quandrants: {quadrantCnt}')
        return
    print(f'Image size: {imgWidth}x{imgHeight}, (quadrants: {quadrantCnt})')

    quadrantHorizontalCnt = int(imgWidth / constants.QUAD_SIZE)

    #create new image and pixel map
    img = Image.new('RGB', (imgWidth, imgHeight))
    pixels = img.load() 
    
    #generate pixels for each quadrant
    for quadIndex in range(quadrantCnt):
        #quadrant coordinates
        qx = int(quadIndex % quadrantHorizontalCnt) * constants.QUAD_SIZE
        qy = int(quadIndex / quadrantHorizontalCnt) * constants.QUAD_SIZE
        
        quadrant = quadrants[quadIndex]

        #iterate each pixel in the quadrant
        for pIndex in range(len(quadrant)):
            #every quadrant is made of 64 pixels (8x8)
            #get the pixel x and y
            px = qx + int(pIndex % 8)
            py = qy + int(pIndex / 8)
            #set the pixel color based on the index value in the palette.
            pixelIndex = quadrant[pIndex]
            pixels[px, py] = constants.PALETTE[pixelIndex] 
    
    #finally, save the image.
    try:
        os.makedirs(constants.EXPORT_FOLDER)
    except:# folder already most likely exists. fix your perms otherwise.
        pass

    img.save(f'{constants.EXPORT_FOLDER}/{name}.png')
