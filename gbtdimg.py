import constants
import sys
import example_data
import decoder
import encoder


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
            quads = encoder.generateQuadrants(data)
            ordered = encoder.sortQuadrants(quads)
            encoder.exportImage(name, ordered)
        else:
            print('No data to decode.') 

    elif mode == '-e':
        name = args[3]
        print(f'Decoding example image ({name})')

        if path and name:
            arr = decoder.decompileImageFile(path)

            out = []

            for i in range(0, len(arr), 16):
                out.append(arr[i:i+16])

            unsorted = decoder.sortQuadrantsForDecompile(out)

            decoder.decoderexportCOutFIle(name, unsorted)
            print(f'Exporting out files: {constants.EXPORT_FOLDER}/{name}.c & {constants.EXPORT_FOLDER}/{name}.h')


            


