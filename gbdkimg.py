from PIL import Image
import constants

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

    quadrantCnt = len(quads)
    ordered = []

    if quadrantCnt == 1 or quadrantCnt == 2:
        # 8x8       8x16
        # 0         0
        #           1
        ordered = quads #already sorted
    elif quadrantCnt == 4:
        # 16x16
        # 0  2 
        # 1  3
        ordered = [
            quads[0],
            quads[2],
            quads[1],
            quads[3]
        ]
    elif quadrantCnt == 16:
        # 32x32
        # 0  2   8  10
        # 1  3   9  11
        # 4  6  12  14
        # 5  7  13  15
        ordered = [
            quads[0],
            quads[2],
            quads[8],
            quads[10],
            quads[1],
            quads[3],
            quads[9],
            quads[11],
            quads[4],
            quads[6],
            quads[12],
            quads[14],
            quads[5],
            quads[7],
            quads[13],
            quads[15]
        ]

    return ordered

def exportImage(quadrants, name):
    quadrantCnt = len(quadrants)
    imgWidth  = constants.SPRITE_SIZES[quadrantCnt][0]
    imgHeight = constants.SPRITE_SIZES[quadrantCnt][1]

    print(f'Image size: {imgWidth}x{imgHeight}, (quadrants: {quadrantCnt})')

    quadrantHorizontalCnt = imgWidth / constants.QUAD_SIZE 

    #create new image and pixel map
    img = Image.new('RGB', (imgWidth, imgHeight))
    pixels = img.load() 
    
    #generate pixels for each quadrant
    for i in range(quadrantCnt):
        #quadrant coordinates
        qx = int(i % quadrantHorizontalCnt) * constants.QUAD_SIZE
        qy = int(i / quadrantHorizontalCnt) * constants.QUAD_SIZE
        
        quadrant = quadrants[i]

        #iterate each pixel in the quadrant
        for j in range(len(quadrant)):
            #every quadrant is made of 64 pixels (8x8)
            #get the pixel x and y
            px = qx + int(j % 8)
            py = qy + int(j / 8)
            #set the pixel color based on the index value in the palette.
            pixelIndex = quadrant[j]
            pixels[px, py] = constants.PALETTE[pixelIndex] 
    
    #finally, save the image.
    img.save(name + ".png")
